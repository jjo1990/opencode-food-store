"""
Tests for token refresh endpoint
"""

from fastapi.testclient import TestClient


def test_refresh_success(client: TestClient, test_user_data: dict):
    """Test successful token refresh"""

    # Register and login
    client.post("/api/v1/auth/register", json=test_user_data)
    response = client.post(
        "/api/v1/auth/login",
        json={"email": test_user_data["email"], "password": test_user_data["password"]},
    )

    old_refresh_token = response.json()["refresh_token"]
    response.json()["access_token"]

    # Refresh
    response = client.post("/api/v1/auth/refresh", json={"refresh_token": old_refresh_token})

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "Bearer"

    # Refresh token should be different (new token generated)
    assert data["refresh_token"] != old_refresh_token


def test_refresh_new_tokens_are_valid(client: TestClient, test_user_data: dict):
    """Test that new tokens from refresh are valid JWTs"""
    # Register and login
    client.post("/api/v1/auth/register", json=test_user_data)
    response = client.post(
        "/api/v1/auth/login",
        json={"email": test_user_data["email"], "password": test_user_data["password"]},
    )

    refresh_token = response.json()["refresh_token"]

    # Refresh
    response = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})

    data = response.json()

    # New tokens should have 3 parts (header.payload.signature)
    assert data["access_token"].count(".") == 2
    assert data["refresh_token"].count(".") == 2


def test_refresh_invalid_token(client: TestClient):
    """Test refresh fails with invalid token"""
    response = client.post("/api/v1/auth/refresh", json={"refresh_token": "invalid.token.here"})

    assert response.status_code == 401


def test_refresh_revoked_token(client: TestClient, test_user_data: dict):
    """Test refresh fails with revoked token"""
    # Register and login
    client.post("/api/v1/auth/register", json=test_user_data)
    response = client.post(
        "/api/v1/auth/login",
        json={"email": test_user_data["email"], "password": test_user_data["password"]},
    )

    refresh_token = response.json()["refresh_token"]

    # Refresh once to get new tokens and revoke the old one
    response1 = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert response1.status_code == 200

    # Try to refresh with the old revoked token
    response2 = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})

    assert response2.status_code == 401
    assert "no autorizado" in response2.json()["detail"].lower()


def test_refresh_revokes_previous_token(client: TestClient, test_user_data: dict, db):
    """Test that refresh revokes the previous token"""
    from app.core.security import hash_refresh_token
    from app.models import RefreshToken

    # Register and login
    client.post("/api/v1/auth/register", json=test_user_data)
    response = client.post(
        "/api/v1/auth/login",
        json={"email": test_user_data["email"], "password": test_user_data["password"]},
    )

    old_refresh_token = response.json()["refresh_token"]
    old_token_hash = hash_refresh_token(old_refresh_token)

    # Check token is active
    db_token = db.query(RefreshToken).filter(RefreshToken.token_hash == old_token_hash).first()
    assert db_token.revoked_at is None

    # Refresh
    response = client.post("/api/v1/auth/refresh", json={"refresh_token": old_refresh_token})

    assert response.status_code == 200

    # Check old token is revoked
    db.refresh(db_token)
    assert db_token.revoked_at is not None


def test_refresh_replay_attack_detection(client: TestClient, test_user_data: dict, db):
    """Test replay attack detection revokes all family tokens"""
    from app.models import RefreshToken

    # Register and login
    client.post("/api/v1/auth/register", json=test_user_data)
    response = client.post(
        "/api/v1/auth/login",
        json={"email": test_user_data["email"], "password": test_user_data["password"]},
    )

    refresh_token = response.json()["refresh_token"]

    # First refresh - should work
    response1 = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert response1.status_code == 200

    # Try to refresh with old token again - REPLAY ATTACK
    response2 = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})

    assert response2.status_code == 401
    assert "no autorizado" in response2.json()["detail"].lower()

    # Check that ALL tokens in family are revoked
    from app.models import User

    user = db.query(User).filter(User.email == test_user_data["email"]).first()
    tokens = db.query(RefreshToken).filter(RefreshToken.user_id == user.id).all()

    # All tokens should be revoked
    assert all(token.revoked_at is not None for token in tokens)
