"""
Tests for user profile endpoints
"""

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import User, UserRole


def _register_and_login(
    client: TestClient,
    email: str = "test@example.com",
    password: str = "SecurePass123",
    full_name: str = "Test User",
) -> dict:
    """Helper to register and login a user, returning token data."""
    client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": password,
            "full_name": full_name,
        },
    )
    resp = client.post(
        "/api/v1/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )
    assert resp.status_code == 200
    return resp.json()


def test_get_profile_authenticated(client: TestClient):
    """Test that authenticated user can get their profile."""
    token_data = _register_and_login(client)
    token = token_data["access_token"]

    response = client.get(
        "/api/v1/usuarios/me",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["full_name"] == "Test User"
    assert data["telefono"] is None
    assert "CLIENT" in data["roles"]
    assert "id" in data
    assert "created_at" in data


def test_get_profile_unauthenticated(client: TestClient):
    """Test that unauthenticated request returns 403 (HTTPBearer default)."""
    response = client.get("/api/v1/usuarios/me")
    assert response.status_code == 403


def test_update_profile(client: TestClient):
    """Test updating full_name and telefono."""
    token_data = _register_and_login(client)
    token = token_data["access_token"]

    response = client.put(
        "/api/v1/usuarios/me",
        json={
            "full_name": "Nuevo Nombre",
            "telefono": "1234567890",
        },
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == "Nuevo Nombre"
    assert data["telefono"] == "1234567890"
    assert data["email"] == "test@example.com"


def test_update_profile_partial(client: TestClient):
    """Test updating only full_name, telefono stays unchanged."""
    token_data = _register_and_login(client)
    token = token_data["access_token"]

    # Set initial telefono
    client.put(
        "/api/v1/usuarios/me",
        json={
            "full_name": "Original",
            "telefono": "5555555555",
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    # Now update only full_name
    response = client.put(
        "/api/v1/usuarios/me",
        json={
            "full_name": "Solo Nombre",
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == "Solo Nombre"
    assert data["telefono"] == "5555555555"


def test_update_profile_short_name(client: TestClient):
    """Test that name shorter than 2 chars returns 422."""
    token_data = _register_and_login(client)
    token = token_data["access_token"]

    response = client.put(
        "/api/v1/usuarios/me",
        json={
            "full_name": "A",
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 422


def test_change_password(client: TestClient):
    """Test successful password change."""
    token_data = _register_and_login(client)
    token = token_data["access_token"]

    response = client.put(
        "/api/v1/usuarios/me/contrasena",
        json={
            "current_password": "SecurePass123",
            "new_password": "NuevaSegura456",
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Contraseña actualizada correctamente"

    # Login with new password should work
    login_resp = client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "NuevaSegura456",
        },
    )
    assert login_resp.status_code == 200

    # Login with old password should fail
    old_login = client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "SecurePass123",
        },
    )
    assert old_login.status_code == 401


def test_change_password_wrong_current(client: TestClient):
    """Test password change with wrong current password returns 401."""
    token_data = _register_and_login(client)
    token = token_data["access_token"]

    response = client.put(
        "/api/v1/usuarios/me/contrasena",
        json={
            "current_password": "WrongPassword1",
            "new_password": "NuevaSegura456",
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401
    assert "incorrecta" in response.json()["detail"].lower()


def test_change_password_short_new(client: TestClient):
    """Test password change with short new password returns 422."""
    token_data = _register_and_login(client)
    token = token_data["access_token"]

    response = client.put(
        "/api/v1/usuarios/me/contrasena",
        json={
            "current_password": "SecurePass123",
            "new_password": "short",
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 422


def test_delete_account_client(client: TestClient, db: Session):
    """Test that a CLIENT user can delete their account (soft delete)."""
    token_data = _register_and_login(client)
    token = token_data["access_token"]

    response = client.delete(
        "/api/v1/usuarios/me",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )
    assert response.status_code == 204

    # User should be soft-deleted in DB
    user = db.query(User).filter(User.email == "test@example.com").first()
    assert user is not None
    assert user.soft_deleted_at is not None

    # Login should fail
    login_resp = client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "SecurePass123",
        },
    )
    assert login_resp.status_code == 401


def test_delete_account_admin(client: TestClient, db: Session):
    """Test that an ADMIN-only user cannot self-delete (returns 403)."""
    from app.core.security import hash_password

    # Create user directly (bypass register which auto-assigns CLIENT)
    user = User(
        email="admin-only@test.com",
        hashed_password=hash_password("SecurePass123"),
        full_name="Admin Only",
    )
    db.add(user)
    db.flush()
    db.add(UserRole(user_id=user.id, role="ADMIN"))
    db.commit()

    login_resp = client.post(
        "/api/v1/auth/login",
        json={
            "email": "admin-only@test.com",
            "password": "SecurePass123",
        },
    )
    token = login_resp.json()["access_token"]

    response = client.delete(
        "/api/v1/usuarios/me",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )
    assert response.status_code == 403


def test_delete_account_unauthenticated(client: TestClient):
    """Test that unauthenticated delete returns 403 (HTTPBearer default)."""
    response = client.delete("/api/v1/usuarios/me")
    assert response.status_code == 403
