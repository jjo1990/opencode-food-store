"""
Tests for RBAC and protected routes
"""
import pytest
from fastapi.testclient import TestClient


def test_protected_route_without_token(client: TestClient):
    """Test that protected route returns 401 without token"""
    response = client.put("/api/v1/admin/users/550e8400-e29b-41d4-a716-446655440000/roles", json={"roles": ["ADMIN"]})
    
    assert response.status_code == 403  # Depends on how FastAPI handles missing auth


def test_protected_route_client_role_forbidden(client: TestClient, test_user_data: dict):
    """Test that CLIENT user gets 403 on ADMIN-only route"""
    # Register and login as CLIENT
    client.post("/api/v1/auth/register", json=test_user_data)
    response = client.post("/api/v1/auth/login", json={
        "email": test_user_data["email"],
        "password": test_user_data["password"]
    })
    
    access_token = response.json()["access_token"]
    
    # Try to access admin endpoint
    response = client.put(
        "/api/v1/admin/users/550e8400-e29b-41d4-a716-446655440000/roles",
        json={"roles": ["ADMIN"]},
        headers={"Authorization": f"Bearer {access_token}"}
    )
    
    assert response.status_code == 403


def test_admin_can_assign_roles(client: TestClient, test_user_data: dict, db):
    """Test ADMIN can assign roles to users"""
    from app.models import User, UserRole
    
    # Create an ADMIN user
    admin_data = {
        "email": "admin@example.com",
        "password": "AdminPassword123",
        "full_name": "Admin User"
    }
    client.post("/api/v1/auth/register", json=admin_data)
    
    # Manually assign ADMIN role
    admin_user = db.query(User).filter(User.email == "admin@example.com").first()
    admin_user.roles.append(UserRole(role="ADMIN"))
    db.commit()
    
    # Login as ADMIN
    response = client.post("/api/v1/auth/login", json={
        "email": admin_data["email"],
        "password": admin_data["password"]
    })
    
    admin_token = response.json()["access_token"]
    
    # Create another user
    user2_data = {
        "email": "user2@example.com",
        "password": "Password123",
        "full_name": "User 2"
    }
    client.post("/api/v1/auth/register", json=user2_data)
    user2 = db.query(User).filter(User.email == "user2@example.com").first()
    
    # ADMIN assigns role to user2
    response = client.put(
        f"/api/v1/admin/users/{user2.id}/roles",
        json={"roles": ["CLIENT", "STOCK"]},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "CLIENT" in data["roles"]
    assert "STOCK" in data["roles"]


def test_cannot_remove_last_admin(client: TestClient, db):
    """Test that last ADMIN cannot be removed"""
    from app.models import User, UserRole
    
    # Create ADMIN user
    admin_data = {
        "email": "admin@example.com",
        "password": "AdminPassword123",
        "full_name": "Admin User"
    }
    import hashlib
    from argon2 import PasswordHasher
    
    pwd_context = PasswordHasher()
    admin = User(
        email=admin_data["email"],
        hashed_password=pwd_context.hash(admin_data["password"]),
        full_name=admin_data["full_name"]
    )
    db.add(admin)
    db.commit()
    
    admin.roles.append(UserRole(role="ADMIN"))
    db.commit()
    
    # Login as ADMIN
    response = client.post("/api/v1/auth/login", json={
        "email": admin_data["email"],
        "password": admin_data["password"]
    })
    
    admin_token = response.json()["access_token"]
    
    # Try to remove ADMIN role from self
    response = client.put(
        f"/api/v1/admin/users/{admin.id}/roles",
        json={"roles": ["CLIENT"]},  # Removing ADMIN
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 403
    assert "único administrador" in response.json()["detail"].lower()


def test_roles_in_jwt_payload(client: TestClient, test_user_data: dict, db):
    """Test that roles are included in JWT payload"""
    import jwt
    from app.core.config import JWT_SECRET_KEY, JWT_ALGORITHM
    from app.models import User, UserRole
    
    # Register user
    client.post("/api/v1/auth/register", json=test_user_data)
    user = db.query(User).filter(User.email == test_user_data["email"]).first()
    
    # Assign STOCK role
    user.roles.append(UserRole(role="STOCK"))
    db.commit()
    
    # Login
    response = client.post("/api/v1/auth/login", json={
        "email": test_user_data["email"],
        "password": test_user_data["password"]
    })
    
    access_token = response.json()["access_token"]
    
    # Decode JWT
    payload = jwt.decode(access_token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    
    assert "roles" in payload
    assert "CLIENT" in payload["roles"]
    assert "STOCK" in payload["roles"]
