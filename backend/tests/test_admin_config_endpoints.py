"""
Integration tests for admin config endpoints.

Tests: GET /api/v1/admin/configuracion, PUT /api/v1/admin/configuracion
"""

import uuid
from datetime import datetime

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


def _create_admin(client: TestClient, email: str) -> tuple[dict, dict]:
    """Register a user via API, make them admin via DB, return (user_dict, headers)."""
    password = "AdminPass123!"
    resp = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password, "full_name": "Admin Test"},
    )
    assert resp.status_code == 201, f"Register failed: {resp.json()}"
    user_data = resp.json()

    login_resp = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert login_resp.status_code == 200, f"Login failed: {login_resp.json()}"
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    return user_data, headers


def _make_admin(db: Session, user_id: str):
    """Assign ADMIN role to a user in DB."""
    from app.models.user_role import UserRole

    db.add(UserRole(user_id=uuid.UUID(user_id), role="ADMIN"))
    db.commit()


def _seed_config(db: Session, clave: str, valor: str, updated_by=None):
    """Insert a system config row directly in DB."""
    from app.models.system_config import SystemConfig

    row = SystemConfig(
        clave=clave, valor=valor, updated_by=updated_by, updated_at=datetime.utcnow()
    )
    db.add(row)
    db.commit()
    return row


class TestAdminConfiguracion:
    """Tests for GET/PUT /api/v1/admin/configuracion"""

    def test_get_config_unauthorized_no_token(self, client: TestClient):
        resp = client.get("/api/v1/admin/configuracion")
        assert resp.status_code == 403

    def test_get_config_forbidden_client_role(self, client: TestClient, db: Session):
        user, headers = _create_admin(client, "client1@test.com")
        resp = client.get("/api/v1/admin/configuracion", headers=headers)
        assert resp.status_code == 403

    def test_get_config_admin_returns_config(self, client: TestClient, db: Session):
        user, headers = _create_admin(client, "admin_config1@test.com")
        _make_admin(db, user["id"])
        login_resp = client.post(
            "/api/v1/auth/login",
            json={"email": "admin_config1@test.com", "password": "AdminPass123!"},
        )
        headers = {"Authorization": f"Bearer {login_resp.json()['access_token']}"}

        _seed_config(db, "horario_apertura", "08:00")
        resp = client.get("/api/v1/admin/configuracion", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "configuracion" in data
        assert "auditoria" in data
        assert data["configuracion"]["horario_apertura"] == "08:00"

    def test_get_config_returns_seeded_keys(self, client: TestClient, db: Session):
        user, headers = _create_admin(client, "admin_config2@test.com")
        _make_admin(db, user["id"])
        login_resp = client.post(
            "/api/v1/auth/login",
            json={"email": "admin_config2@test.com", "password": "AdminPass123!"},
        )
        headers = {"Authorization": f"Bearer {login_resp.json()['access_token']}"}

        _seed_config(db, "horario_apertura", "08:00")
        _seed_config(db, "horario_cierre", "22:00")
        _seed_config(db, "zona_entrega", '{"lat": -34.6037, "lng": -58.3816, "radio_km": 5}')
        _seed_config(db, "costo_envio", "150.00")
        _seed_config(db, "mensaje_bienvenida", "Bienvenido!")
        resp = client.get("/api/v1/admin/configuracion", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        configuracion = data["configuracion"]
        assert len(configuracion) == 5
        assert configuracion["horario_apertura"] == "08:00"
        assert configuracion["horario_cierre"] == "22:00"
        assert configuracion["zona_entrega"] == '{"lat": -34.6037, "lng": -58.3816, "radio_km": 5}'
        assert configuracion["costo_envio"] == "150.00"
        assert configuracion["mensaje_bienvenida"] == "Bienvenido!"

    def test_get_config_has_auditoria_fields(self, client: TestClient, db: Session):
        user, headers = _create_admin(client, "admin_config3@test.com")
        _make_admin(db, user["id"])
        login_resp = client.post(
            "/api/v1/auth/login",
            json={"email": "admin_config3@test.com", "password": "AdminPass123!"},
        )
        headers = {"Authorization": f"Bearer {login_resp.json()['access_token']}"}

        admin_uuid = uuid.UUID(user["id"])
        _seed_config(db, "horario_apertura", "08:00", updated_by=admin_uuid)
        resp = client.get("/api/v1/admin/configuracion", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        auditoria = data["auditoria"]
        assert "horario_apertura" in auditoria
        audit_item = auditoria["horario_apertura"]
        assert "updated_by" in audit_item
        assert "updated_by_name" in audit_item
        assert "updated_at" in audit_item
        assert audit_item["updated_by"] == str(admin_uuid)
        assert audit_item["updated_by_name"] == "Admin Test"

    def test_put_config_unauthorized_no_token(self, client: TestClient):
        resp = client.put("/api/v1/admin/configuracion", json={"configuracion": {}})
        assert resp.status_code == 403

    def test_put_config_forbidden_client_role(self, client: TestClient, db: Session):
        user, headers = _create_admin(client, "client2@test.com")
        resp = client.put(
            "/api/v1/admin/configuracion", json={"configuracion": {}}, headers=headers
        )
        assert resp.status_code == 403

    def test_put_config_updates_existing_key(self, client: TestClient, db: Session):
        user, headers = _create_admin(client, "admin_config4@test.com")
        _make_admin(db, user["id"])
        login_resp = client.post(
            "/api/v1/auth/login",
            json={"email": "admin_config4@test.com", "password": "AdminPass123!"},
        )
        headers = {"Authorization": f"Bearer {login_resp.json()['access_token']}"}

        _seed_config(db, "horario_apertura", "08:00")
        resp = client.put(
            "/api/v1/admin/configuracion",
            json={"configuracion": {"horario_apertura": "09:00"}},
            headers=headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["configuracion"]["horario_apertura"] == "09:00"
        assert data["auditoria"]["horario_apertura"]["updated_by"] == user["id"]

    def test_put_config_creates_new_key(self, client: TestClient, db: Session):
        user, headers = _create_admin(client, "admin_config5@test.com")
        _make_admin(db, user["id"])
        login_resp = client.post(
            "/api/v1/auth/login",
            json={"email": "admin_config5@test.com", "password": "AdminPass123!"},
        )
        headers = {"Authorization": f"Bearer {login_resp.json()['access_token']}"}

        resp = client.put(
            "/api/v1/admin/configuracion",
            json={"configuracion": {"nuevo_key": "nuevo_valor"}},
            headers=headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["configuracion"]["nuevo_key"] == "nuevo_valor"

    def test_put_config_sets_updated_by(self, client: TestClient, db: Session):
        user, headers = _create_admin(client, "admin_config6@test.com")
        _make_admin(db, user["id"])
        login_resp = client.post(
            "/api/v1/auth/login",
            json={"email": "admin_config6@test.com", "password": "AdminPass123!"},
        )
        headers = {"Authorization": f"Bearer {login_resp.json()['access_token']}"}

        _seed_config(db, "test_key", "old_value")
        resp = client.put(
            "/api/v1/admin/configuracion",
            json={"configuracion": {"test_key": "new_value"}},
            headers=headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["auditoria"]["test_key"]["updated_by"] == user["id"]

    def test_put_config_updates_updated_at(self, client: TestClient, db: Session):
        user, headers = _create_admin(client, "admin_config7@test.com")
        _make_admin(db, user["id"])
        login_resp = client.post(
            "/api/v1/auth/login",
            json={"email": "admin_config7@test.com", "password": "AdminPass123!"},
        )
        headers = {"Authorization": f"Bearer {login_resp.json()['access_token']}"}

        _seed_config(db, "test_key", "old_value")
        resp = client.put(
            "/api/v1/admin/configuracion",
            json={"configuracion": {"test_key": "new_value"}},
            headers=headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["auditoria"]["test_key"]["updated_at"] is not None

    def test_put_config_partial_update(self, client: TestClient, db: Session):
        user, headers = _create_admin(client, "admin_config8@test.com")
        _make_admin(db, user["id"])
        login_resp = client.post(
            "/api/v1/auth/login",
            json={"email": "admin_config8@test.com", "password": "AdminPass123!"},
        )
        headers = {"Authorization": f"Bearer {login_resp.json()['access_token']}"}

        _seed_config(db, "key1", "value1")
        _seed_config(db, "key2", "value2")
        resp = client.put(
            "/api/v1/admin/configuracion",
            json={"configuracion": {"key1": "new_value1"}},
            headers=headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["configuracion"]["key1"] == "new_value1"
        assert data["configuracion"]["key2"] == "value2"

    def test_put_config_multiple_keys(self, client: TestClient, db: Session):
        user, headers = _create_admin(client, "admin_config9@test.com")
        _make_admin(db, user["id"])
        login_resp = client.post(
            "/api/v1/auth/login",
            json={"email": "admin_config9@test.com", "password": "AdminPass123!"},
        )
        headers = {"Authorization": f"Bearer {login_resp.json()['access_token']}"}

        _seed_config(db, "key_a", "old_a")
        _seed_config(db, "key_b", "old_b")
        resp = client.put(
            "/api/v1/admin/configuracion",
            json={"configuracion": {"key_a": "new_a", "key_b": "new_b"}},
            headers=headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["configuracion"]["key_a"] == "new_a"
        assert data["configuracion"]["key_b"] == "new_b"
