"""
Analytics Service (Step 3 & 5)

Contains complex database aggregations for Business Intelligence dashboards.

Industry Best Practice:
Never do this math in the frontend or inside the API route.
By isolating SQL aggregations here, we can cache them later (Step 8)
without rewriting business logic.
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, text
import pandas as pd
import io
from app.models.analytics import PredictionHistory, RecommendationResult
from app.utils.cache import analytics_cache


class AnalyticsService:
    
    @staticmethod
    def get_overview_kpis(db: Session):
        """Calculate high-level Business KPIs (Step 1 & 5)."""
        cache_key = "overview_kpis"
        cached = analytics_cache.get(cache_key)
        if cached: return cached
        
        # Total predictions served
        total_predictions = db.query(func.count(PredictionHistory.id)).scalar() or 0
        
        # We assume the #1 ranked item is the one "chosen" for KPI calculation purposes
        chosen_materials = db.query(RecommendationResult).filter(RecommendationResult.rank == 1).subquery()
        
        # Calculate totals from chosen materials
        stats = db.query(
            func.avg(chosen_materials.c.predicted_co2_kg).label("avg_co2"),
            func.avg(chosen_materials.c.predicted_cost_per_kg).label("avg_cost"),
        ).first()
        
        # Calculate savings against a baseline (e.g., standard plastic).
        baseline_co2 = 2.5
        baseline_cost = 4.0
        
        avg_co2 = stats.avg_co2 or 0.0
        avg_cost = stats.avg_cost or 0.0
        
        co2_saved_per_item = baseline_co2 - avg_co2 if avg_co2 > 0 else 0
        cost_saved_per_item = baseline_cost - avg_cost if avg_cost > 0 else 0
        
        result = {
            "total_predictions": total_predictions,
            "total_co2_saved_kg": round(co2_saved_per_item * total_predictions, 2),
            "total_cost_saved_usd": round(cost_saved_per_item * total_predictions, 2),
            "average_co2_per_package": round(avg_co2, 3),
            "average_cost_per_package": round(avg_cost, 2)
        }
        analytics_cache.set(cache_key, result)
        return result

    @staticmethod
    def get_material_frequency(db: Session, top_n: int = 10):
        """Count how many times each material was recommended in the Top 1."""
        cache_key = f"material_freq_{top_n}"
        cached = analytics_cache.get(cache_key)
        if cached: return cached
        
        results = db.query(
            RecommendationResult.material_name,
            func.count(RecommendationResult.id).label('frequency')
        ).filter(RecommendationResult.rank == 1)\
         .group_by(RecommendationResult.material_name)\
         .order_by(desc('frequency'))\
         .limit(top_n).all()
         
        result = [{"material_name": row[0], "count": row[1]} for row in results]
        analytics_cache.set(cache_key, result)
        return result

    @staticmethod
    def get_category_breakdown(db: Session):
        """Analyze prediction requests by product category."""
        cache_key = "category_breakdown"
        cached = analytics_cache.get(cache_key)
        if cached: return cached
        
        results = db.query(
            PredictionHistory.category,
            func.count(PredictionHistory.id).label('count')
        ).group_by(PredictionHistory.category)\
         .order_by(desc('count')).all()
         
        result = [{"category": row[0], "count": row[1]} for row in results]
        analytics_cache.set(cache_key, result)
        return result
    
    @staticmethod
    def get_daily_trend(db: Session):
        """Calculate moving usage trends (Step 5)."""
        cache_key = "daily_trend"
        cached = analytics_cache.get(cache_key)
        if cached: return cached
        
        # SQLite uses strftime, PostgreSQL uses date_trunc. 
        # For simplicity across DBs, we'll use a string conversion.
        results = db.query(
            func.strftime('%Y-%m-%d', PredictionHistory.created_at).label('date'),
            func.count(PredictionHistory.id).label('predictions')
        ).group_by('date').order_by('date').all()
        
        result = [{"date": row[0], "predictions": row[1]} for row in results]
        analytics_cache.set(cache_key, result)
        return result
        
    @staticmethod
    def export_sustainability_report_csv(db: Session) -> str:
        """Generate a CSV export of recent predictions for executives (Step 7)."""
        # Fetch the last 1000 predictions joined with their top recommendation
        query = db.query(
            PredictionHistory.created_at,
            PredictionHistory.category,
            PredictionHistory.product_weight_kg,
            RecommendationResult.material_name,
            RecommendationResult.predicted_cost_per_kg,
            RecommendationResult.predicted_co2_kg,
            RecommendationResult.sustainability_rating
        ).join(
            RecommendationResult, 
            PredictionHistory.id == RecommendationResult.prediction_id
        ).filter(
            RecommendationResult.rank == 1
        ).order_by(
            desc(PredictionHistory.created_at)
        ).limit(1000)
        
        # We can use pandas to quickly convert SQLAlchemy results to CSV string
        df = pd.read_sql(query.statement, query.session.bind)
        
        # Clean up column names for business readability
        df.columns = ["Date", "Product Category", "Weight (kg)", 
                      "Recommended Material", "Predicted Cost ($/kg)", 
                      "Predicted CO2 (kg)", "Sustainability Rating"]
        
        output = io.StringIO()
        df.to_csv(output, index=False)
        return output.getvalue()
