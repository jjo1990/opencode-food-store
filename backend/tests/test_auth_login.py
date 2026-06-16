"""
Tests for user login endpoint
"""

from datetime import UTC

from fastapi.testclient import TestClient


def test_login_success(client: TestClient, test_user_data: dict):
    """Test successful login"""
    # Register first
    client.post("/api/v1/auth/register", json=test_user_data)

    # Login
    login_data = {"email": test_user_data["email"], "password": test_user_data["password"]}
    response = client.post("/api/v1/auth/login", json=login_data)

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "Bearer"
    assert data["expires_in"] == 1800  # 30 minutes


def test_login_nonexistent_email(client: TestClient):
    """Test login fails with non-existent email"""
    login_data = {"email": "nonexistent@example.com", "password": "SomePassword123"}
    response = client.post("/api/v1/auth/login", json=login_data)

    assert response.status_code == 401
    assert "inválidas" in response.json()["detail"].lower()


def test_login_wrong_password(client: TestClient, test_user_data: dict):
    """Test login fails with wrong password"""
    # Register first
    client.post("/api/v1/auth/register", json=test_user_data)

    # Login with wrong password
    login_data = {"email": test_user_data["email"], "password": "WrongPassword123"}
    response = client.post("/api/v1/auth/login", json=login_data)

    assert response.status_code == 401
    assert "inválidas" in response.json()["detail"].lower()


def test_login_generic_error_message(client: TestClient, test_user_data: dict):
    """Test that login gives generic error for both email and password errors"""
    # Register first
    client.post("/api/v1/auth/register", json=test_user_data)

    # Try with wrong password
    response1 = client.post(
        "/api/v1/auth/login",
        json={"email": test_user_data["email"], "password": "WrongPassword123"},
    )

    # Try with wrong email
    response2 = client.post(
        "/api/v1/auth/login",
        json={"email": "wrong@example.com", "password": test_user_data["password"]},
    )

    # Both should have same error message
    assert response1.status_code == 401
    assert response2.status_code == 401
    assert response1.json()["detail"] == response2.json()["detail"]


def test_login_tokens_in_response(client: TestClient, test_user_data: dict):
    """Test that tokens are present in login response"""
    client.post("/api/v1/auth/register", json=test_user_data)

    response = client.post(
        "/api/v1/auth/login",
        json={"email": test_user_data["email"], "password": test_user_data["password"]},
    )

    assert response.status_code == 200
    data = response.json()

    # Check tokens are JWT-like
    assert data["access_token"].count(".") == 2  # JWT has 3 parts
    assert data["refresh_token"].count(".") == 2  # JWT has 3 parts


def test_login_access_token_expiry(client: TestClient, test_user_data: dict):
    """Test that access token expires in 30 minutes"""
    from datetime import datetime

    import jwt

    from app.core.config import JWT_ALGORITHM, JWT_SECRET_KEY

    client.post("/api/v1/auth/register", json=test_user_data)

    response = client.post(
        "/api/v1/auth/login",
        json={"email": test_user_data["email"], "password": test_user_data["password"]},
    )

    access_token = response.json()["access_token"]

    # Decode and check expiry
    payload = jwt.decode(access_token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])

    exp_time = datetime.fromtimestamp(payload["exp"], tz=UTC)
    now = datetime.now(UTC)

    # Should expire in approximately 30 minutes (1800 seconds)
    time_diff = (exp_time - now).total_seconds()
    assert 1700 < time_diff < 1900  # Allow some variance


def test_login_refresh_token_stored_as_hash(client: TestClient, test_user_data: dict, db):
    """Test that refresh token is stored as hash in database"""
    from app.models import RefreshToken

    client.post("/api/v1/auth/register", json=test_user_data)

    response = client.post(
        "/api/v1/auth/login",
        json={"email": test_user_data["email"], "password": test_user_data["password"]},
    )

    refresh_token = response.json()["refresh_token"]

    # Check in database - token should be hashed
    db_token = db.query(RefreshToken).first()
    assert db_token is not None
    assert db_token.token_hash != refresh_token
    # Token hash should be SHA256 (64 chars hex)
    assert len(db_token.token_hash) == 64
