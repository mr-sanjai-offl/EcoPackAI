"""
Test fixtures shared across all test modules.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture(scope="module")
def client():
    """Create a test client that triggers the lifespan (model loading)."""
    with TestClient(app) as c:
        yield c


@pytest.fixture
def sample_product():
    """A valid product request payload."""
    return {
        "product_weight_kg": 0.19,
        "dimensions_cm": "15x7x1",
        "category": "Electronics",
        "sub_category": "Mobile Devices",
        "fragile": True,
        "food_grade_required": False,
        "moisture_sensitive": True,
        "temperature_sensitive": True,
        "preferred_material_type": "Paper-Based",
        "sustainability_priority": "High",
        "max_packaging_cost": 2.5,
        "top_n": 5
    }
