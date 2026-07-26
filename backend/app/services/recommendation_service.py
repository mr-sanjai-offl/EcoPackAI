"""
Recommendation Service (Step 5 - Business Logic)

This service wraps the ML inference logic and adds production concerns:
- Inference timing
- Request counting for metrics
- Error handling

The route layer (recommend.py) delegates ALL logic here.
Routes should never contain business logic — only HTTP concerns.
"""
import time
import logging
import pandas as pd
import numpy as np
from app.services.model_service import model_service
from app.schemas.request import ProductRequest
from app.db.database import SessionLocal
from app.models.analytics import PredictionHistory, RecommendationResult

logger = logging.getLogger("ecopackai")


class RecommendationService:
    """Business logic for generating packaging recommendations."""
    
    # Metrics counters
    total_requests: int = 0
    total_latency_ms: float = 0.0
    
    @classmethod
    def recommend(cls, request: ProductRequest) -> dict:
        """Generate recommendations for a product.
        
        Args:
            request: Validated ProductRequest from the API.
            
        Returns:
            Dictionary containing recommendations and metadata.
        """
        start_time = time.perf_counter()
        
        # Parse dimensions
        parts = request.dimensions_cm.split('x')
        length_cm = float(parts[0])
        width_cm = float(parts[1])
        height_cm = float(parts[2])
        volume_cm3 = length_cm * width_cm * height_cm
        density_index = request.product_weight_kg / (volume_cm3 / 1000)
        
        product = {
            'product_weight_kg': request.product_weight_kg,
            'volume_cm3': volume_cm3,
            'density_index': density_index,
            'category': request.category,
            'sub_category': request.sub_category,
            'preferred_material_type': request.preferred_material_type,
            'sustainability_priority': request.sustainability_priority,
            'max_packaging_cost': request.max_packaging_cost,
            'fragile': request.fragile,
            'food_grade_required': request.food_grade_required,
            'moisture_sensitive': request.moisture_sensitive,
            'temperature_sensitive': request.temperature_sensitive,
        }
        
        # Stage 1: Hard Filtering
        valid_materials = model_service.materials.copy()
        valid_materials = valid_materials[
            valid_materials['weight_capacity_kg'] >= request.product_weight_kg
        ]
        if request.food_grade_required:
            valid_materials = valid_materials[valid_materials['food_safe'] == True]
        
        total_evaluated = len(valid_materials)
        
        if total_evaluated == 0:
            inference_ms = (time.perf_counter() - start_time) * 1000
            return {
                "model_version": model_service.model_version,
                "inference_time_ms": round(inference_ms, 2),
                "total_materials_evaluated": 0,
                "recommendations": []
            }
        
        # Stage 2: ML Scoring
        pairs = []
        for _, mat in valid_materials.iterrows():
            pair = dict(product)
            for key in ['strength_score', 'weight_capacity_kg', 'co2_emission_kg',
                        'cost_per_kg', 'material_efficiency', 'material_type',
                        'water_resistance', 'industry_usage', 'sustainability_rating',
                        'food_safe']:
                pair[key] = mat[key]
            pair['_material_id'] = mat['material_id']
            pair['_material_name'] = mat['material_name']
            pair['_biodegradability'] = mat.get('biodegradability_score', 0)
            pair['_recyclability'] = mat.get('recyclability_percent', 0)
            pairs.append(pair)
        
        df_pairs = pd.DataFrame(pairs)
        feature_cols = [c for c in df_pairs.columns if not c.startswith('_')]
        
        X_inference = df_pairs[feature_cols]
        X_processed = model_service.preprocessor.transform(X_inference)
        scores = model_service.model.predict(X_processed)
        df_pairs['predicted_score'] = scores
        
        # Stage 3: Ranking
        top = df_pairs.sort_values('predicted_score', ascending=False).head(request.top_n)
        
        recommendations = []
        for rank, (_, row) in enumerate(top.iterrows(), 1):
            recommendations.append({
                "rank": rank,
                "material_id": int(row['_material_id']),
                "material_name": row['_material_name'],
                "overall_score": round(float(row['predicted_score']), 2),
                "confidence": round(min(float(row['predicted_score']) / 100, 1.0), 3),
                "predicted_cost_per_kg": round(float(row['cost_per_kg']), 2),
                "predicted_co2_kg": round(float(row['co2_emission_kg']), 3),
                "strength_score": round(float(row['strength_score']), 1),
                "sustainability_rating": row['sustainability_rating'],
                "biodegradability": round(float(row['_biodegradability']), 2),
                "recyclability_percent": round(float(row['_recyclability']), 1),
                "reason": cls._generate_reason(row)
            })
        
        inference_ms = (time.perf_counter() - start_time) * 1000
        
        # Update metrics
        cls.total_requests += 1
        cls.total_latency_ms += inference_ms
        
        logger.info(f"Recommendation generated in {inference_ms:.2f}ms for {request.category}/{request.sub_category}")
        
        return {
            "model_version": model_service.model_version,
            "inference_time_ms": round(inference_ms, 2),
            "total_materials_evaluated": total_evaluated,
            "recommendations": recommendations
        }
        
    @staticmethod
    def save_history(request: ProductRequest, result: dict):
        """Save prediction and recommendations to the database asynchronously.
        
        We open a new DB session here because this runs as a BackgroundTask
        after the main API request has finished (and its DB session is closed).
        """
        try:
            with SessionLocal() as db:
                prediction = PredictionHistory(
                    model_version=result["model_version"],
                    inference_time_ms=result["inference_time_ms"],
                    product_weight_kg=request.product_weight_kg,
                    dimensions_cm=request.dimensions_cm,
                    category=request.category,
                    sub_category=request.sub_category,
                    fragile=request.fragile,
                    food_grade_required=request.food_grade_required,
                    max_packaging_cost=request.max_packaging_cost,
                    preferred_material_type=request.preferred_material_type,
                    sustainability_priority=request.sustainability_priority
                )
                db.add(prediction)
                db.flush()  # To get the prediction.id
                
                for rec in result["recommendations"]:
                    db_rec = RecommendationResult(
                        prediction_id=prediction.id,
                        rank=rec["rank"],
                        material_id=rec["material_id"],
                        material_name=rec["material_name"],
                        overall_score=rec["overall_score"],
                        confidence=rec["confidence"],
                        predicted_cost_per_kg=rec["predicted_cost_per_kg"],
                        predicted_co2_kg=rec["predicted_co2_kg"],
                        strength_score=rec["strength_score"],
                        sustainability_rating=rec["sustainability_rating"]
                    )
                    db.add(db_rec)
                
                db.commit()
        except Exception as e:
            logger.error(f"Failed to save prediction history to DB: {e}", exc_info=True)

    @staticmethod
    def _generate_reason(row) -> str:
        reasons = []
        if row['co2_emission_kg'] <= 0.8:
            reasons.append("Very low carbon footprint")
        elif row['co2_emission_kg'] <= 1.5:
            reasons.append("Moderate carbon footprint")
        if row['strength_score'] >= 8.0:
            reasons.append("Excellent structural strength")
        elif row['strength_score'] >= 6.0:
            reasons.append("Good structural strength")
        if row['cost_per_kg'] <= 1.5:
            reasons.append("Cost-effective material")
        if row['_biodegradability'] >= 0.9:
            reasons.append("Highly biodegradable")
        if row['_recyclability'] >= 90:
            reasons.append("Highly recyclable")
        if row['sustainability_rating'] == 'A':
            reasons.append("Top sustainability rating (A)")
        return "; ".join(reasons) if reasons else "Balanced trade-off across all criteria"
