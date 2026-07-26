"""
Analytics ORM Models (Step 2)

These models define the SQL tables that store inference history.

Why two tables?
Normalization. One Prediction (the product) has many Recommendations (top 5 materials).
If we stored this in one table, we'd duplicate the product details 5 times per request,
wasting space and making aggregations messy.

By separating them:
1. prediction_history: Tracks WHAT the user asked for.
2. recommendation_results: Tracks WHAT the AI suggested.
"""
from datetime import datetime
import uuid
from sqlalchemy import Column, String, Float, Integer, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base


def generate_uuid():
    return str(uuid.uuid4())


class PredictionHistory(Base):
    """Stores the input features of every recommendation request."""
    __tablename__ = "prediction_history"

    id = Column(String, primary_key=True, default=generate_uuid)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Request metadata
    model_version = Column(String, index=True)
    inference_time_ms = Column(Float)
    
    # Input product features
    product_weight_kg = Column(Float)
    dimensions_cm = Column(String)
    volume_cm3 = Column(Float)
    category = Column(String, index=True)
    sub_category = Column(String)
    fragile = Column(Boolean)
    food_grade_required = Column(Boolean)
    max_packaging_cost = Column(Float)
    preferred_material_type = Column(String)
    sustainability_priority = Column(String)
    
    # Relationship to the generated recommendations
    recommendations = relationship(
        "RecommendationResult", 
        back_populates="prediction",
        cascade="all, delete-orphan"
    )


class RecommendationResult(Base):
    """Stores the Top-N AI recommendations generated for a specific prediction."""
    __tablename__ = "recommendation_results"

    id = Column(String, primary_key=True, default=generate_uuid)
    prediction_id = Column(String, ForeignKey("prediction_history.id"), index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Recommendation details
    rank = Column(Integer)
    material_id = Column(Integer, index=True)
    material_name = Column(String)
    
    # ML Scores
    overall_score = Column(Float)
    confidence = Column(Float)
    
    # Business Metrics predicted by the system
    predicted_cost_per_kg = Column(Float)
    predicted_co2_kg = Column(Float)
    strength_score = Column(Float)
    sustainability_rating = Column(String, index=True)
    
    # Relationship back to the prediction
    prediction = relationship("PredictionHistory", back_populates="recommendations")
