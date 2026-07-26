"""Tests for the BI Analytics endpoints."""


def test_analytics_endpoints_empty(client):
    """Test analytics endpoints when DB is empty."""
    # Overview
    r = client.get("/api/v1/analytics/overview")
    assert r.status_code == 200
    assert r.json()["total_predictions"] >= 0
    
    # Materials
    r = client.get("/api/v1/analytics/materials")
    assert r.status_code == 200
    assert isinstance(r.json(), list)
    
    # Categories
    r = client.get("/api/v1/analytics/categories")
    assert r.status_code == 200
    assert isinstance(r.json(), list)
    
    # Trends
    r = client.get("/api/v1/analytics/trends")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_analytics_with_data(client, sample_product):
    """Generate a prediction and verify analytics picks it up."""
    # 1. Generate prediction
    res = client.post("/api/v1/recommend", json=sample_product)
    assert res.status_code == 200
    
    # Note: The database save happens in a BackgroundTask. 
    # FastAPI's TestClient runs BackgroundTasks synchronously before returning!
    # So the DB is guaranteed to be updated here.
    
    # 2. Check overview
    r = client.get("/api/v1/analytics/overview")
    assert r.status_code == 200
    data = r.json()
    assert data["total_predictions"] > 0
    
    # 3. Check materials
    r = client.get("/api/v1/analytics/materials")
    assert r.status_code == 200
    mats = r.json()
    assert len(mats) > 0
    assert "material_name" in mats[0]
    assert "count" in mats[0]
    
    # 4. Check categories
    r = client.get("/api/v1/analytics/categories")
    assert r.status_code == 200
    cats = r.json()
    assert len(cats) > 0
    assert cats[0]["category"] == sample_product["category"]
    
    # 5. Check trends
    r = client.get("/api/v1/analytics/trends")
    assert r.status_code == 200
    assert len(r.json()) > 0
    
    # 6. Check export
    r = client.get("/api/v1/analytics/export")
    assert r.status_code == 200
    assert r.headers["content-type"] == "text/csv; charset=utf-8"
    assert "Date,Product Category,Weight (kg),Recommended Material" in r.text
    assert len(r.text.splitlines()) > 1  # Header + at least one row
