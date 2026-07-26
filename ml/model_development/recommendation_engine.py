"""
Step 7: EcoPackAI Recommendation Engine

This is the HEART of the project. It combines:
  Stage 1: Rule-based hard filtering (physics & compliance)
  Stage 2: ML-based scoring and ranking (XGBoost predictions)

Input:  A product's properties (weight, dimensions, category, fragility, etc.)
Output: Top-5 ranked eco-friendly packaging materials with scores and explanations.
"""
import os
import json
import joblib
import pandas as pd
import numpy as np


class EcoPackRecommender:
    """Production-grade recommendation engine for sustainable packaging."""
    
    def __init__(self, artifacts_dir: str, processed_dir: str):
        """Load all production artifacts needed for inference.
        
        Args:
            artifacts_dir: Path to serialized model and preprocessor.
            processed_dir: Path to processed materials CSV.
        """
        self.model = joblib.load(os.path.join(artifacts_dir, 'trained_model.joblib'))
        self.preprocessor = joblib.load(os.path.join(artifacts_dir, 'preprocessor.joblib'))
        self.materials = pd.read_csv(os.path.join(processed_dir, 'processed_materials.csv'))
        
    def recommend(self, product: dict, top_n: int = 5) -> list[dict]:
        """Generate top-N packaging recommendations for a given product.
        
        Args:
            product: Dictionary of product features (from API request or CSV row).
            top_n: Number of recommendations to return.
            
        Returns:
            List of recommendation dictionaries, ranked by predicted suitability.
        """
        # Parse dimensions if provided as string
        if 'dimensions_cm' in product and isinstance(product['dimensions_cm'], str):
            parts = product['dimensions_cm'].split('x')
            product['length_cm'] = float(parts[0])
            product['width_cm'] = float(parts[1])
            product['height_cm'] = float(parts[2])
        
        # Calculate engineered features
        product['volume_cm3'] = product['length_cm'] * product['width_cm'] * product['height_cm']
        product['density_index'] = product['product_weight_kg'] / (product['volume_cm3'] / 1000)
        
        # ---- STAGE 1: Hard Filtering (Rule-Based) ----
        valid_materials = self.materials.copy()
        
        # Physics constraint: material must support the product weight
        valid_materials = valid_materials[
            valid_materials['weight_capacity_kg'] >= product['product_weight_kg']
        ]
        
        # Compliance constraint: food products need food-safe materials
        if product.get('food_grade_required', False):
            valid_materials = valid_materials[valid_materials['food_safe'] == True]
        
        if len(valid_materials) == 0:
            return [{"error": "No suitable materials found for this product."}]
        
        # ---- STAGE 2: ML Scoring ----
        # Create (product, material) pair rows for each valid material
        pairs = []
        for _, mat in valid_materials.iterrows():
            pair = {}
            # Product features
            for key in ['product_weight_kg', 'volume_cm3', 'density_index',
                        'category', 'sub_category', 'preferred_material_type',
                        'sustainability_priority', 'max_packaging_cost',
                        'fragile', 'food_grade_required', 'moisture_sensitive',
                        'temperature_sensitive']:
                pair[key] = product.get(key)
            # Material features
            for key in ['strength_score', 'weight_capacity_kg', 'co2_emission_kg',
                        'cost_per_kg', 'material_efficiency', 'material_type',
                        'water_resistance', 'industry_usage', 'sustainability_rating',
                        'food_safe']:
                pair[key] = mat[key]
            # Store material metadata for output
            pair['_material_id'] = mat['material_id']
            pair['_material_name'] = mat['material_name']
            pair['_biodegradability'] = mat.get('biodegradability_score', 0)
            pair['_recyclability'] = mat.get('recyclability_percent', 0)
            pairs.append(pair)
        
        df_pairs = pd.DataFrame(pairs)
        
        # Separate metadata columns from feature columns
        meta_cols = [c for c in df_pairs.columns if c.startswith('_')]
        feature_cols = [c for c in df_pairs.columns if not c.startswith('_')]
        
        X_inference = df_pairs[feature_cols]
        X_processed = self.preprocessor.transform(X_inference)
        
        # ML prediction
        scores = self.model.predict(X_processed)
        df_pairs['predicted_score'] = scores
        
        # ---- STAGE 3: Ranking & Output ----
        df_pairs = df_pairs.sort_values('predicted_score', ascending=False).head(top_n)
        
        recommendations = []
        for rank, (_, row) in enumerate(df_pairs.iterrows(), 1):
            rec = {
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
                "reason": self._generate_reason(row)
            }
            recommendations.append(rec)
        
        return recommendations
    
    def _generate_reason(self, row) -> str:
        """Generate a human-readable explanation for why this material was recommended."""
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


def demo_recommendation():
    """Run a demo recommendation to verify the engine works."""
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    artifacts_dir = os.path.join(base_dir, 'data', 'artifacts')
    processed_dir = os.path.join(base_dir, 'data', 'processed')
    
    engine = EcoPackRecommender(artifacts_dir, processed_dir)
    
    # Test with a real product from our dataset
    test_product = {
        "product_weight_kg": 0.19,
        "dimensions_cm": "15x7x1",
        "category": "Electronics",
        "sub_category": "Mobile Devices",
        "preferred_material_type": "Paper-Based",
        "sustainability_priority": "High",
        "max_packaging_cost": 2.5,
        "fragile": True,
        "food_grade_required": False,
        "moisture_sensitive": True,
        "temperature_sensitive": True
    }
    
    print("=" * 60)
    print("EcoPackAI Recommendation Engine Demo")
    print("=" * 60)
    print(f"\nProduct: iPhone 15 Pro")
    print(f"Weight: {test_product['product_weight_kg']} kg")
    print(f"Dimensions: {test_product['dimensions_cm']}")
    print(f"Category: {test_product['category']}")
    print(f"Fragile: {test_product['fragile']}")
    print(f"Sustainability Priority: {test_product['sustainability_priority']}")
    print("\n" + "-" * 60)
    print("TOP 5 RECOMMENDED PACKAGING MATERIALS:")
    print("-" * 60)
    
    results = engine.recommend(test_product)
    
    for rec in results:
        print(f"\n  #{rec['rank']}  {rec['material_name']}")
        print(f"      Score: {rec['overall_score']}/100  |  Confidence: {rec['confidence']}")
        print(f"      Cost: ${rec['predicted_cost_per_kg']}/kg  |  CO2: {rec['predicted_co2_kg']} kg")
        print(f"      Strength: {rec['strength_score']}/10  |  Rating: {rec['sustainability_rating']}")
        print(f"      Reason: {rec['reason']}")
    
    # Save results as JSON for portfolio
    results_path = os.path.join(base_dir, 'data', 'reports', 'demo_recommendation.json')
    os.makedirs(os.path.dirname(results_path), exist_ok=True)
    with open(results_path, 'w') as f:
        json.dump({"product": test_product, "recommendations": results}, f, indent=4)
    print(f"\nResults saved to {results_path}")


if __name__ == "__main__":
    demo_recommendation()
