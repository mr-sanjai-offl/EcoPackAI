"""
Database Configuration (Step 2)

Sets up SQLAlchemy for database connectivity.
For this portfolio project, we default to SQLite so it runs anywhere without Docker,
but the architecture is 100% compatible with PostgreSQL in production.

Why we use a Session generator (`get_db`):
In FastAPI, we use dependency injection (`Depends(get_db)`) to give each API request
its own database session. When the request finishes, the session is automatically closed,
preventing connection leaks.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import get_settings

settings = get_settings()

# Default to SQLite if no DATABASE_URL is provided in env
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    f"sqlite:///{os.path.join(settings.PROJECT_ROOT, 'data', 'analytics.db')}"
)

# Connect args specific to SQLite (prevent thread sharing issues)
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """Dependency for providing a database session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
