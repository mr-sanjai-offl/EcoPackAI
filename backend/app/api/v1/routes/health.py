"""
Health & Monitoring Routes (Step 6)

GET /health  - Is the server running?
GET /ready   - Is the ML model loaded and ready for inference?
GET /version - What model version is deployed?
GET /metrics - How is the service performing?

Why these exist:
- Kubernetes uses /health for liveness probes (restart if dead)
- Kubernetes uses /ready for readiness probes (don't send traffic until model is loaded)
- CI/CD pipelines use /version to verify correct deployment
- Grafana/Prometheus scrape /metrics for dashboards
"""
from fastapi import APIRouter
from app.schemas.response import HealthResponse, VersionResponse, MetricsResponse
from app.services.model_service import model_service
from app.services.recommendation_service import RecommendationService
from app.core.config import get_settings

router = APIRouter()


@router.get("/health", response_model=HealthResponse, summary="Health Check")
async def health():
    """Check if the service and all dependencies are operational."""
    settings = get_settings()
    return HealthResponse(
        status="healthy" if model_service.is_ready else "degraded",
        model_loaded=model_service.is_ready and model_service.model is not None,
        preprocessor_loaded=model_service.is_ready and model_service.preprocessor is not None,
        materials_loaded=model_service.is_ready and model_service.materials is not None,
        model_version=model_service.model_version
    )


@router.get("/ready", summary="Readiness Check")
async def ready():
    """Check if the service is ready to accept inference requests."""
    if model_service.is_ready:
        return {"status": "ready", "model_version": model_service.model_version}
    return {"status": "not_ready", "reason": "ML model has not finished loading."}


@router.get("/version", response_model=VersionResponse, summary="Version Info")
async def version():
    """Return application and model version information."""
    settings = get_settings()
    return VersionResponse(
        app_name=settings.APP_NAME,
        app_version=settings.APP_VERSION,
        model_version=model_service.model_version,
        model_hash=model_service.model_hash,
        algorithm=model_service.registry.get("algorithm", "unknown") if model_service.is_ready else "not_loaded"
    )


@router.get("/metrics", response_model=MetricsResponse, summary="Inference Metrics")
async def metrics():
    """Return inference performance metrics."""
    total = RecommendationService.total_requests
    avg_latency = (
        RecommendationService.total_latency_ms / total if total > 0 else 0.0
    )
    return MetricsResponse(
        total_requests=total,
        average_latency_ms=round(avg_latency, 2),
        model_version=model_service.model_version,
        model_r2=model_service.metrics.get("r2", 0.0) if model_service.is_ready else 0.0,
        model_rmse=model_service.metrics.get("rmse", 0.0) if model_service.is_ready else 0.0
    )
