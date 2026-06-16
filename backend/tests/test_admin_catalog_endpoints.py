"""
Integration tests for admin catalog endpoints.

Tests: GET /api/v1/admin/productos, /categorias, /ingredientes
Also tests incluir_eliminados on public /api/v1/productos
"""

import uuid
from datetime import datetime
from decimal import Decimal

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.categoria import Categoria
from app.models.ingrediente import Ingrediente
from app.models.producto import Producto


def _create_admin(client: TestClient, email: str) -> tuple[dict, dict]:
    """Register a user via API, make them admin via DB, return (user_dict, headers)."""
    password = "AdminPass123!"
    resp = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password, "full_name": "Admin Test"},
    )
    assert resp.status_code == 201, f"Register failed: {resp.json()}"
    user_data = resp.json()

    # Login to get token
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


def _make_stock(db: Session, user_id: str):
    """Assign STOCK role to a user in DB."""
    from app.models.user_role import UserRole

    db.add(UserRole(user_id=uuid.UUID(user_id), role="STOCK"))
    db.commit()


def _seed_producto(
    db: Session,
    nombre: str,
    disponible: bool = True,
    deleted: bool = False,
    precio: float = 10.0,
    stock: int = 5,
) -> Producto:
    p = Producto(
        nombre=nombre,
        descripcion=f"Desc {nombre}",
        precio_base=Decimal(str(precio)),
        stock_cantidad=stock,
        disponible=disponible,
        soft_deleted_at=datetime.utcnow() if deleted else None,
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


def _seed_categoria(db: Session, nombre: str, deleted: bool = False) -> Categoria:
    c = Categoria(
        nombre=nombre,
        soft_deleted_at=datetime.utcnow() if deleted else None,
    )
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


def _seed_ingrediente(
    db: Session, nombre: str, es_alergeno: bool = False, deleted: bool = False
) -> Ingrediente:
    i = Ingrediente(
        nombre=nombre,
        es_alergeno=es_alergeno,
        soft_deleted_at=datetime.utcnow() if deleted else None,
    )
    db.add(i)
    db.commit()
    db.refresh(i)
    return i


# ─── Productos ──────────────────────────────────────────────────────────────


class TestAdminProductos:
    """Tests for GET /api/v1/admin/productos"""

    def test_unauthorized_no_token(self, client: TestClient):
        resp = client.get("/api/v1/admin/productos")
        assert resp.status_code == 403

    def test_forbidden_client_role(self, client: TestClient, db: Session):
        user, headers = _create_admin(client, "client1@test.com")
        resp = client.get("/api/v1/admin/productos", headers=headers)
        assert resp.status_code == 403

    def test_admin_can_list_productos(self, client: TestClient, db: Session):
        user, headers = _create_admin(client, "admin1@test.com")
        _make_admin(db, user["id"])
        # Re-login to get fresh token with ADMIN role
        login_resp = client.post(
            "/api/v1/auth/login", json={"email": "admin1@test.com", "password": "AdminPass123!"}
        )
        headers = {"Authorization": f"Bearer {login_resp.json()['access_token']}"}

        _seed_producto(db, "Pizza")
        resp = client.get("/api/v1/admin/productos", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] >= 1
        assert len(data["items"]) >= 1
        assert data["page"] == 1
        assert "size" in data
        assert "pages" in data

    def test_admin_sees_deleted_productos(self, client: TestClient, db: Session):
        user, headers = _create_admin(client, "admin2@test.com")
        _make_admin(db, user["id"])
        login_resp = client.post(
            "/api/v1/auth/login", json={"email": "admin2@test.com", "password": "AdminPass123!"}
        )
        headers = {"Authorization": f"Bearer {login_resp.json()['access_token']}"}

        _seed_producto(db, "Active", deleted=False)
        _seed_producto(db, "Deleted", deleted=True)
        resp = client.get("/api/v1/admin/productos", headers=headers)
        assert resp.status_code == 200
        items = resp.json()["items"]
        names = [i["nombre"] for i in items]
        assert "Active" in names
        assert "Deleted" in names

    def test_filter_eliminado_true(self, client: TestClient, db: Session):
        user, headers = _create_admin(client, "admin3@test.com")
        _make_admin(db, user["id"])
        login_resp = client.post(
            "/api/v1/auth/login", json={"email": "admin3@test.com", "password": "AdminPass123!"}
        )
        headers = {"Authorization": f"Bearer {login_resp.json()['access_token']}"}

        _seed_producto(db, "Active", deleted=False)
        _seed_producto(db, "Deleted", deleted=True)
        resp = client.get("/api/v1/admin/productos?eliminado=true", headers=headers)
        assert resp.status_code == 200
        items = resp.json()["items"]
        names = [i["nombre"] for i in items]
        assert "Deleted" in names
        assert "Active" not in names

    def test_filter_eliminado_false(self, client: TestClient, db: Session):
        user, headers = _create_admin(client, "admin3b@test.com")
        _make_admin(db, user["id"])
        login_resp = client.post(
            "/api/v1/auth/login", json={"email": "admin3b@test.com", "password": "AdminPass123!"}
        )
        headers = {"Authorization": f"Bearer {login_resp.json()['access_token']}"}

        _seed_producto(db, "Active", deleted=False)
        _seed_producto(db, "Deleted", deleted=True)
        resp = client.get("/api/v1/admin/productos?eliminado=false", headers=headers)
        assert resp.status_code == 200
        items = resp.json()["items"]
        names = [i["nombre"] for i in items]
        assert "Active" in names
        assert "Deleted" not in names

    def test_filter_disponible(self, client: TestClient, db: Session):
        user, headers = _create_admin(client, "admin4@test.com")
        _make_admin(db, user["id"])
        login_resp = client.post(
            "/api/v1/auth/login", json={"email": "admin4@test.com", "password": "AdminPass123!"}
        )
        headers = {"Authorization": f"Bearer {login_resp.json()['access_token']}"}

        _seed_producto(db, "Available", disponible=True)
        _seed_producto(db, "Unavailable", disponible=False)
        resp = client.get("/api/v1/admin/productos?disponible=false", headers=headers)
        assert resp.status_code == 200
        items = resp.json()["items"]
        names = [i["nombre"] for i in items]
        assert "Unavailable" in names
        assert "Available" not in names

    def test_search_by_name(self, client: TestClient, db: Session):
        user, headers = _create_admin(client, "admin5@test.com")
        _make_admin(db, user["id"])
        login_resp = client.post(
            "/api/v1/auth/login", json={"email": "admin5@test.com", "password": "AdminPass123!"}
        )
        headers = {"Authorization": f"Bearer {login_resp.json()['access_token']}"}

        _seed_producto(db, "Pizza Margherita")
        _seed_producto(db, "Hamburguesa")
        resp = client.get("/api/v1/admin/productos?search=pizza", headers=headers)
        assert resp.status_code == 200
        items = resp.json()["items"]
        names = [i["nombre"] for i in items]
        assert any("pizza" in n.lower() for n in names)
        assert not any("hamburguesa" in n.lower() for n in names)

    def test_pagination(self, client: TestClient, db: Session):
        user, headers = _create_admin(client, "admin6@test.com")
        _make_admin(db, user["id"])
        login_resp = client.post(
            "/api/v1/auth/login", json={"email": "admin6@test.com", "password": "AdminPass123!"}
        )
        headers = {"Authorization": f"Bearer {login_resp.json()['access_token']}"}

        for i in range(5):
            _seed_producto(db, f"Producto {i}")
        resp = client.get("/api/v1/admin/productos?page=1&size=3", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["items"]) == 3
        assert data["total"] >= 5
        assert data["pages"] >= 2

    def test_stock_role_can_access(self, client: TestClient, db: Session):
        user, headers = _create_admin(client, "stock1@test.com")
        _make_stock(db, user["id"])
        login_resp = client.post(
            "/api/v1/auth/login", json={"email": "stock1@test.com", "password": "AdminPass123!"}
        )
        headers = {"Authorization": f"Bearer {login_resp.json()['access_token']}"}

        _seed_producto(db, "Pizza")
        resp = client.get("/api/v1/admin/productos", headers=headers)
        assert resp.status_code == 200

    def test_producto_has_required_fields(self, client: TestClient, db: Session):
        user, headers = _create_admin(client, "admin7@test.com")
        _make_admin(db, user["id"])
        login_resp = client.post(
            "/api/v1/auth/login", json={"email": "admin7@test.com", "password": "AdminPass123!"}
        )
        headers = {"Authorization": f"Bearer {login_resp.json()['access_token']}"}

        _seed_producto(db, "Test Product", precio=15.5, stock=10)
        resp = client.get("/api/v1/admin/productos", headers=headers)
        assert resp.status_code == 200
        item = resp.json()["items"][0]
        assert "id" in item
        assert "nombre" in item
        assert "precio_base" in item
        assert "stock_cantidad" in item
        assert "disponible" in item
        assert "eliminado" in item
        assert "soft_deleted_at" in item
        assert "created_at" in item
        assert "categorias" in item

    def test_filter_by_categoria_id(self, client: TestClient, db: Session):
        user, headers = _create_admin(client, "admin8@test.com")
        _make_admin(db, user["id"])
        login_resp = client.post(
            "/api/v1/auth/login", json={"email": "admin8@test.com", "password": "AdminPass123!"}
        )
        headers = {"Authorization": f"Bearer {login_resp.json()['access_token']}"}

        cat = _seed_categoria(db, "Bebidas")
        from app.models.producto_categoria import ProductoCategoria

        p1 = _seed_producto(db, "Coca Cola")
        _seed_producto(db, "Pizza")  # not in categoria — should be excluded
        db.add(ProductoCategoria(producto_id=p1.id, categoria_id=cat.id))
        db.commit()

        resp = client.get(f"/api/v1/admin/productos?categoria_id={cat.id}", headers=headers)
        assert resp.status_code == 200
        items = resp.json()["items"]
        names = [i["nombre"] for i in items]
        assert "Coca Cola" in names
        assert "Pizza" not in names


# ─── Categorias ─────────────────────────────────────────────────────────────


class TestAdminCategorias:
    """Tests for GET /api/v1/admin/categorias"""

    def test_unauthorized_no_token(self, client: TestClient):
        resp = client.get("/api/v1/admin/categorias")
        assert resp.status_code == 403

    def test_forbidden_client_role(self, client: TestClient, db: Session):
        user, headers = _create_admin(client, "client2@test.com")
        resp = client.get("/api/v1/admin/categorias", headers=headers)
        assert resp.status_code == 403

    def test_admin_can_list_categorias(self, client: TestClient, db: Session):
        user, headers = _create_admin(client, "admin9@test.com")
        _make_admin(db, user["id"])
        login_resp = client.post(
            "/api/v1/auth/login", json={"email": "admin9@test.com", "password": "AdminPass123!"}
        )
        headers = {"Authorization": f"Bearer {login_resp.json()['access_token']}"}

        _seed_categoria(db, "Bebidas")
        resp = client.get("/api/v1/admin/categorias", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] >= 1
        assert len(data["items"]) >= 1

    def test_admin_sees_deleted_categorias(self, client: TestClient, db: Session):
        user, headers = _create_admin(client, "admin10@test.com")
        _make_admin(db, user["id"])
        login_resp = client.post(
            "/api/v1/auth/login", json={"email": "admin10@test.com", "password": "AdminPass123!"}
        )
        headers = {"Authorization": f"Bearer {login_resp.json()['access_token']}"}

        _seed_categoria(db, "Active")
        _seed_categoria(db, "Deleted Cat", deleted=True)
        resp = client.get("/api/v1/admin/categorias", headers=headers)
        assert resp.status_code == 200
        items = resp.json()["items"]
        names = [i["nombre"] for i in items]
        assert "Active" in names
        assert "Deleted Cat" in names

    def test_filter_eliminado_categorias(self, client: TestClient, db: Session):
        user, headers = _create_admin(client, "admin11@test.com")
        _make_admin(db, user["id"])
        login_resp = client.post(
            "/api/v1/auth/login", json={"email": "admin11@test.com", "password": "AdminPass123!"}
        )
        headers = {"Authorization": f"Bearer {login_resp.json()['access_token']}"}

        _seed_categoria(db, "Active")
        _seed_categoria(db, "Deleted Cat", deleted=True)
        resp = client.get("/api/v1/admin/categorias?eliminado=true", headers=headers)
        assert resp.status_code == 200
        items = resp.json()["items"]
        names = [i["nombre"] for i in items]
        assert "Deleted Cat" in names
        assert "Active" not in names

    def test_categoria_has_required_fields(self, client: TestClient, db: Session):
        user, headers = _create_admin(client, "admin12@test.com")
        _make_admin(db, user["id"])
        login_resp = client.post(
            "/api/v1/auth/login", json={"email": "admin12@test.com", "password": "AdminPass123!"}
        )
        headers = {"Authorization": f"Bearer {login_resp.json()['access_token']}"}

        _seed_categoria(db, "Test Cat")
        resp = client.get("/api/v1/admin/categorias", headers=headers)
        assert resp.status_code == 200
        item = resp.json()["items"][0]
        assert "id" in item
        assert "nombre" in item
        assert "parent_id" in item
        assert "eliminado" in item
        assert "soft_deleted_at" in item
        assert "created_at" in item


# ─── Ingredientes ───────────────────────────────────────────────────────────


class TestAdminIngredientes:
    """Tests for GET /api/v1/admin/ingredientes"""

    def test_unauthorized_no_token(self, client: TestClient):
        resp = client.get("/api/v1/admin/ingredientes")
        assert resp.status_code == 403

    def test_forbidden_client_role(self, client: TestClient, db: Session):
        user, headers = _create_admin(client, "client3@test.com")
        resp = client.get("/api/v1/admin/ingredientes", headers=headers)
        assert resp.status_code == 403

    def test_admin_can_list_ingredientes(self, client: TestClient, db: Session):
        user, headers = _create_admin(client, "admin13@test.com")
        _make_admin(db, user["id"])
        login_resp = client.post(
            "/api/v1/auth/login", json={"email": "admin13@test.com", "password": "AdminPass123!"}
        )
        headers = {"Authorization": f"Bearer {login_resp.json()['access_token']}"}

        _seed_ingrediente(db, "Tomate")
        resp = client.get("/api/v1/admin/ingredientes", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] >= 1
        assert len(data["items"]) >= 1

    def test_admin_sees_deleted_ingredientes(self, client: TestClient, db: Session):
        user, headers = _create_admin(client, "admin14@test.com")
        _make_admin(db, user["id"])
        login_resp = client.post(
            "/api/v1/auth/login", json={"email": "admin14@test.com", "password": "AdminPass123!"}
        )
        headers = {"Authorization": f"Bearer {login_resp.json()['access_token']}"}

        _seed_ingrediente(db, "Active Ing")
        _seed_ingrediente(db, "Deleted Ing", deleted=True)
        resp = client.get("/api/v1/admin/ingredientes", headers=headers)
        assert resp.status_code == 200
        items = resp.json()["items"]
        names = [i["nombre"] for i in items]
        assert "Active Ing" in names
        assert "Deleted Ing" in names

    def test_filter_es_alergeno(self, client: TestClient, db: Session):
        user, headers = _create_admin(client, "admin15@test.com")
        _make_admin(db, user["id"])
        login_resp = client.post(
            "/api/v1/auth/login", json={"email": "admin15@test.com", "password": "AdminPass123!"}
        )
        headers = {"Authorization": f"Bearer {login_resp.json()['access_token']}"}

        _seed_ingrediente(db, "Tomate", es_alergeno=False)
        _seed_ingrediente(db, "Maní", es_alergeno=True)
        resp = client.get("/api/v1/admin/ingredientes?es_alergeno=true", headers=headers)
        assert resp.status_code == 200
        items = resp.json()["items"]
        names = [i["nombre"] for i in items]
        assert "Maní" in names
        assert "Tomate" not in names

    def test_filter_eliminado_ingredientes(self, client: TestClient, db: Session):
        user, headers = _create_admin(client, "admin16@test.com")
        _make_admin(db, user["id"])
        login_resp = client.post(
            "/api/v1/auth/login", json={"email": "admin16@test.com", "password": "AdminPass123!"}
        )
        headers = {"Authorization": f"Bearer {login_resp.json()['access_token']}"}

        _seed_ingrediente(db, "Active Ing")
        _seed_ingrediente(db, "Deleted Ing", deleted=True)
        resp = client.get("/api/v1/admin/ingredientes?eliminado=true", headers=headers)
        assert resp.status_code == 200
        items = resp.json()["items"]
        names = [i["nombre"] for i in items]
        assert "Deleted Ing" in names
        assert "Active Ing" not in names

    def test_ingrediente_has_required_fields(self, client: TestClient, db: Session):
        user, headers = _create_admin(client, "admin17@test.com")
        _make_admin(db, user["id"])
        login_resp = client.post(
            "/api/v1/auth/login", json={"email": "admin17@test.com", "password": "AdminPass123!"}
        )
        headers = {"Authorization": f"Bearer {login_resp.json()['access_token']}"}

        _seed_ingrediente(db, "Test Ing", es_alergeno=True)
        resp = client.get("/api/v1/admin/ingredientes", headers=headers)
        assert resp.status_code == 200
        item = resp.json()["items"][0]
        assert "id" in item
        assert "nombre" in item
        assert "es_alergeno" in item
        assert "eliminado" in item
        assert "soft_deleted_at" in item
        assert "created_at" in item

    def test_pagination_ingredientes(self, client: TestClient, db: Session):
        user, headers = _create_admin(client, "admin18@test.com")
        _make_admin(db, user["id"])
        login_resp = client.post(
            "/api/v1/auth/login", json={"email": "admin18@test.com", "password": "AdminPass123!"}
        )
        headers = {"Authorization": f"Bearer {login_resp.json()['access_token']}"}

        for i in range(5):
            _seed_ingrediente(db, f"Ingrediente {i}")
        resp = client.get("/api/v1/admin/ingredientes?page=1&size=3", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["items"]) == 3
        assert data["total"] >= 5
        assert data["pages"] >= 2


# ─── Incluir Eliminados ────────────────────────────────────────────────────


class TestIncluirEliminados:
    """Tests for incluir_eliminados query param on public /api/v1/productos"""

    def test_admin_incluir_eliminados(self, client: TestClient, db: Session):
        user, headers = _create_admin(client, "admin19@test.com")
        _make_admin(db, user["id"])
        login_resp = client.post(
            "/api/v1/auth/login", json={"email": "admin19@test.com", "password": "AdminPass123!"}
        )
        headers = {"Authorization": f"Bearer {login_resp.json()['access_token']}"}

        _seed_producto(db, "Active", deleted=False)
        _seed_producto(db, "Deleted Prod", deleted=True)
        resp = client.get("/api/v1/productos?incluir_eliminados=true", headers=headers)
        assert resp.status_code == 200
        items = resp.json()["items"]
        names = [i["nombre"] for i in items]
        assert "Active" in names
        assert "Deleted Prod" in names

    def test_client_ignores_incluir_eliminados(self, client: TestClient, db: Session):
        _seed_producto(db, "Active", deleted=False)
        _seed_producto(db, "Deleted Prod", deleted=True)

        # Public endpoint, no auth or client token
        resp = client.get("/api/v1/productos?incluir_eliminados=true")
        assert resp.status_code == 200
        items = resp.json()["items"]
        names = [i["nombre"] for i in items]
        assert "Active" in names
        assert "Deleted Prod" not in names

    def test_unauthenticated_ignores_incluir_eliminados(self, client: TestClient, db: Session):
        _seed_producto(db, "Active", deleted=False)
        _seed_producto(db, "Deleted Prod", deleted=True)

        resp = client.get("/api/v1/productos?incluir_eliminados=true")
        assert resp.status_code == 200
        items = resp.json()["items"]
        names = [i["nombre"] for i in items]
        assert "Active" in names
        assert "Deleted Prod" not in names
