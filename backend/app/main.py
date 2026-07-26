"""
EcoPackAI FastAPI Application (Step 1 - App Factory)

This is the entry point. It:
1. Creates the FastAPI app with metadata for Swagger docs
2. Registers the lifespan handler (loads ML model at startup)
3. Mounts CORS middleware (so the Next.js frontend can call us)
4. Mounts the Request ID middleware
5. Registers all API routes under /api/v1
6. Registers a global exception handler

Why lifespan instead of @app.on_event("startup")?
FastAPI deprecated on_event in favor of the lifespan context manager.
The lifespan pattern guarantees cleanup (model unloading) on shutdown.
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.services.model_service import model_service
from app.middleware.request_id import RequestIDMiddleware
from app.api.v1.routes import recommend, health, analytics as analytics_routes
from app.db.database import Base, engine
from app.models import analytics as analytics_models  # Import to register models

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("ecopackai")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: load model at startup, cleanup on shutdown."""
    settings = get_settings()
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    
    # Load ML artifacts (this is the model warm-up)
    try:
        model_service.load(settings.ARTIFACTS_DIR, settings.PROCESSED_DIR)
        logger.info("ML model warm-up complete. Server is ready for inference.")
    except Exception as e:
        logger.error(f"CRITICAL: Failed to load ML model: {e}")
        # Server starts but /ready will report not_ready
        
    # Initialize database tables
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables verified/created successfully.")
    except Exception as e:
        logger.error(f"CRITICAL: Failed to initialize database: {e}")
    
    yield  # Server is running and accepting requests
    
    # Shutdown
    logger.info("Shutting down EcoPackAI server.")


def create_app() -> FastAPI:
    """Application factory pattern."""
    settings = get_settings()
    
    app = FastAPI(
        title=settings.APP_NAME,
        description=(
            "AI-Powered Sustainable Packaging Recommendation System. "
            "Submit product details and receive ranked eco-friendly packaging recommendations "
            "optimized for cost, CO2 emissions, and structural strength."
        ),
        version=settings.APP_VERSION,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Request ID middleware
    app.add_middleware(RequestIDMiddleware)
    
    # Global exception handler (Step 7)
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "error_code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred during inference.",
                "detail": str(exc) if settings.DEBUG else None
            }
        )
    
    # Register routes
    app.include_router(
        health.router,
        tags=["Health & Monitoring"]
    )
    app.include_router(
        recommend.router,
        prefix=settings.API_PREFIX,
        tags=["Recommendations"]
    )
    app.include_router(
        analytics_routes.router,
        prefix=f"{settings.API_PREFIX}/analytics",
        tags=["Business Intelligence"]
    )
    
    return app


# Create the app instance (uvicorn imports this)
app = create_app()
