"""
Unit tests for main FastAPI app
"""


def test_health_endpoint(test_client):
    """Test that health endpoint returns 200"""
    response = test_client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_root_endpoint(test_client):
    """Test that root endpoint returns welcome message"""
    response = test_client.get("/")
    assert response.status_code == 200
    assert "Food Store API" in response.json()["message"]
