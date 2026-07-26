"""
Configuration Management (Step 2)

Uses Pydantic Settings to read configuration from environment variables.
Why: Hardcoded paths break when deploying to different environments
(dev laptop vs staging server vs production Kubernetes pod).
Pydantic Settings automatically reads from .env files or OS env vars.
"""
import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # App metadata
    APP_NAME: str = "EcoPackAI"
    APP_VERSION: str = "1.0.0"
    API_PREFIX: str = "/api/v1"
    DEBUG: bool = False
    
    # ML artifact paths (relative to project root)
    PROJECT_ROOT: str = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "..")
    )
    ARTIFACTS_DIR: str = ""
    PROCESSED_DIR: str = ""
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # CORS
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    def model_post_init(self, __context) -> None:
        """Compute derived paths after initialization."""
        if not self.ARTIFACTS_DIR:
            self.ARTIFACTS_DIR = os.path.join(self.PROJECT_ROOT, "data", "artifacts")
        if not self.PROCESSED_DIR:
            self.PROCESSED_DIR = os.path.join(self.PROJECT_ROOT, "data", "processed")
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache()
def get_settings() -> Settings:
    """Cached singleton for settings. Loaded once, reused everywhere."""
    return Settings()
