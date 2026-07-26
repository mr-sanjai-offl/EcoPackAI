"""Tests for the recommendation endpoint."""


def test_recommend_success(client, sample_product):
    response = client.post("/api/v1/recommend", json=sample_product)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "model_version" in data
    assert "inference_time_ms" in data
    assert len(data["recommendations"]) == 5
    
    # Verify recommendation structure
    rec = data["recommendations"][0]
    assert rec["rank"] == 1
    assert "material_name" in rec
    assert "overall_score" in rec
    assert "confidence" in rec
    assert "predicted_cost_per_kg" in rec
    assert "predicted_co2_kg" in rec
    assert "reason" in rec


def test_recommend_invalid_weight(client):
    payload = {
        "product_weight_kg": -1,
        "dimensions_cm": "15x7x1",
        "category": "Electronics",
        "sub_category": "Mobile Devices"
    }
    response = client.post("/api/v1/recommend", json=payload)
    assert response.status_code == 422


def test_recommend_invalid_dimensions(client):
    payload = {
        "product_weight_kg": 1.0,
        "dimensions_cm": "invalid",
        "category": "Electronics",
        "sub_category": "Mobile Devices"
    }
    response = client.post("/api/v1/recommend", json=payload)
    assert response.status_code == 422


def test_recommend_missing_required_fields(client):
    payload = {"product_weight_kg": 1.0}
    response = client.post("/api/v1/recommend", json=payload)
    assert response.status_code == 422


def test_recommend_custom_top_n(client, sample_product):
    sample_product["top_n"] = 3
    response = client.post("/api/v1/recommend", json=sample_product)
    assert response.status_code == 200
    data = response.json()
    assert len(data["recommendations"]) == 3


def test_recommend_heavy_product(client):
    """Test with a heavy product to verify filtering."""
    payload = {
        "product_weight_kg": 4.5,
        "dimensions_cm": "40x40x25",
        "category": "Home",
        "sub_category": "Kitchenware",
        "fragile": True,
        "food_grade_required": True,
        "moisture_sensitive": False,
        "temperature_sensitive": False,
        "preferred_material_type": "Mushroom-Based",
        "sustainability_priority": "High",
        "max_packaging_cost": 8.5,
        "top_n": 5
    }
    response = client.post("/api/v1/recommend", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"


def test_request_id_header(client, sample_product):
    """Verify X-Request-ID is returned in response headers."""
    response = client.post("/api/v1/recommend", json=sample_product)
    assert "x-request-id" in response.headers
