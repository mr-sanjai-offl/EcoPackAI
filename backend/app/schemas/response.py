"""
Response Schemas (Step 5)

Standardized response models that every endpoint returns.
This ensures the API contract is consistent and predictable.

Why response models matter:
- Frontend developers can auto-generate TypeScript types from OpenAPI spec
- API consumers know exactly what fields to expect
- FastAPI uses these to generate Swagger documentation automatically
"""
from pydantic import BaseModel
from typing import Optional


class MaterialRecommendation(BaseModel):
    """A single packaging material recommendation."""
    rank: int
    material_id: int
    material_name: str
    overall_score: float
    confidence: float
    predicted_cost_per_kg: float
    predicted_co2_kg: float
    strength_score: float
    sustainability_rating: str
    biodegradability: float
    recyclability_percent: float
    reason: str


class RecommendationResponse(BaseModel):
    """Full recommendation API response with metadata."""
    status: str = "success"
    model_version: str
    inference_time_ms: float
    total_materials_evaluated: int
    recommendations: list[MaterialRecommendation]


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    model_loaded: bool
    preprocessor_loaded: bool
    materials_loaded: bool
    model_version: str


class VersionResponse(BaseModel):
    """Version info response."""
    app_name: str
    app_version: str
    model_version: str
    model_hash: str
    algorithm: str


class MetricsResponse(BaseModel):
    """Inference metrics response."""
    total_requests: int
    average_latency_ms: float
    model_version: str
    model_r2: float
    model_rmse: float


class ErrorResponse(BaseModel):
    """Standardized error response."""
    status: str = "error"
    error_code: str
    message: str
    detail: Optional[str] = None
