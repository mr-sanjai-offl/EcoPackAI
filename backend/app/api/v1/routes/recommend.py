"""
Recommendation Route (Step 5)

POST /api/v1/recommend

This route contains ZERO business logic.
It only handles HTTP concerns:
1. Accept the request
2. Delegate to RecommendationService
3. Return the response

This separation means the RecommendationService can be
unit-tested WITHOUT starting a web server.
"""
from fastapi import APIRouter
from app.schemas.request import ProductRequest
from app.schemas.response import RecommendationResponse, ErrorResponse
from app.services.recommendation_service import RecommendationService

router = APIRouter()


@router.post(
    "/recommend",
    response_model=RecommendationResponse,
    responses={
        422: {"model": ErrorResponse, "description": "Validation Error"},
        500: {"model": ErrorResponse, "description": "Inference Error"}
    },
    summary="Get Packaging Recommendations",
    description="Submit product details and receive top-N eco-friendly packaging material recommendations ranked by ML suitability score."
)
async def recommend(request: ProductRequest):
    """Generate AI-powered packaging recommendations."""
    result = RecommendationService.recommend(request)
    return RecommendationResponse(
        status="success",
        model_version=result["model_version"],
        inference_time_ms=result["inference_time_ms"],
        total_materials_evaluated=result["total_materials_evaluated"],
        recommendations=result["recommendations"]
    )
