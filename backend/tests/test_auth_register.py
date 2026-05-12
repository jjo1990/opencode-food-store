"""
Tests for user registration endpoint
"""
import pytest
from fastapi.testclient import TestClient


def test_register_success(client: TestClient, test_user_data: dict):
    """Test successful user registration"""
    response = client.post("/api/v1/auth/register", json=test_user_data)
    
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == test_user_data["email"]
    assert data["full_name"] == test_user_data["full_name"]
    assert "id" in data
    assert "CLIENT" in data["roles"]
    assert "hashed_password" not in data


def test_register_duplicate_email(client: TestClient, test_user_data: dict):
    """Test registration fails with duplicate email"""
    # First registration
    client.post("/api/v1/auth/register", json=test_user_data)
    
    # Second registration with same email
    response = client.post("/api/v1/auth/register", json=test_user_data)
    
    assert response.status_code == 409
    assert "ya está registrado" in response.json()["detail"].lower()


def test_register_weak_password(client: TestClient, test_user_data: dict):
    """Test registration fails with weak password"""
    test_user_data["password"] = "short"
    response = client.post("/api/v1/auth/register", json=test_user_data)
    
    assert response.status_code == 422


def test_register_invalid_email(client: TestClient, test_user_data: dict):
    """Test registration fails with invalid email"""
    test_user_data["email"] = "notanemail"
    response = client.post("/api/v1/auth/register", json=test_user_data)
    
    assert response.status_code == 422


def test_register_user_has_client_role(client: TestClient, test_user_data: dict, db):
    """Test that registered user automatically gets CLIENT role"""
    response = client.post("/api/v1/auth/register", json=test_user_data)
    
    assert response.status_code == 201
    data = response.json()
    assert "CLIENT" in data["roles"]
    assert len(data["roles"]) == 1


def test_register_password_is_hashed(client: TestClient, test_user_data: dict, db):
    """Test that password is properly hashed"""
    from app.models import User
    
    response = client.post("/api/v1/auth/register", json=test_user_data)
    assert response.status_code == 201
    
    # Check in database
    user = db.query(User).filter(User.email == test_user_data["email"]).first()
    assert user is not None
    assert user.hashed_password != test_user_data["password"]
    # Argon2 hashes start with $argon2
    assert user.hashed_password.startswith("$argon2")
