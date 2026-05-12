"""
Tests for logout endpoint
"""
import pytest
from fastapi.testclient import TestClient


def test_logout_success(client: TestClient, test_user_data: dict):
    """Test successful logout"""
    # Register and login
    client.post("/api/v1/auth/register", json=test_user_data)
    response = client.post("/api/v1/auth/login", json={
        "email": test_user_data["email"],
        "password": test_user_data["password"]
    })
    
    access_token = response.json()["access_token"]
    refresh_token = response.json()["refresh_token"]
    
    # Logout
    response = client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": refresh_token},
        headers={"Authorization": f"Bearer {access_token}"}
    )
    
    assert response.status_code == 204


def test_logout_revokes_token(client: TestClient, test_user_data: dict, db):
    """Test that logout revokes the refresh token"""
    from app.models import RefreshToken
    from app.core.security import hash_refresh_token
    
    # Register and login
    client.post("/api/v1/auth/register", json=test_user_data)
    response = client.post("/api/v1/auth/login", json={
        "email": test_user_data["email"],
        "password": test_user_data["password"]
    })
    
    access_token = response.json()["access_token"]
    refresh_token = response.json()["refresh_token"]
    token_hash = hash_refresh_token(refresh_token)
    
    # Check token is active
    db_token = db.query(RefreshToken).filter(
        RefreshToken.token_hash == token_hash
    ).first()
    assert db_token.revoked_at is None
    
    # Logout
    client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": refresh_token},
        headers={"Authorization": f"Bearer {access_token}"}
    )
    
    # Check token is revoked
    db.refresh(db_token)
    assert db_token.revoked_at is not None


def test_logout_prevents_token_reuse(client: TestClient, test_user_data: dict):
    """Test that logout prevents using the token again"""
    # Register and login
    client.post("/api/v1/auth/register", json=test_user_data)
    response = client.post("/api/v1/auth/login", json={
        "email": test_user_data["email"],
        "password": test_user_data["password"]
    })
    
    access_token = response.json()["access_token"]
    refresh_token = response.json()["refresh_token"]
    
    # Logout
    client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": refresh_token},
        headers={"Authorization": f"Bearer {access_token}"}
    )
    
    # Try to refresh with the revoked token
    response = client.post("/api/v1/auth/refresh", json={
        "refresh_token": refresh_token
    })
    
    assert response.status_code == 401
