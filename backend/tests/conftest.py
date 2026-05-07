"""
Shared fixtures for backend tests
"""
import pytest


@pytest.fixture
def test_client():
    """Create a test client for FastAPI tests"""
    from fastapi.testclient import TestClient

    from app.main import app

    return TestClient(app)


@pytest.fixture
def test_user():
    """Return a test user dict"""
    return {"id": "test-user-1", "email": "test@example.com", "name": "Test User"}
