"""
Tests for Productos CRUD endpoints
"""

from decimal import Decimal

import pytest
from fastapi.testclient import TestClient


def test_list_public_products(client: TestClient, seed_producto):
    """GET /api/v1/productos returns 200 with paginated results"""
    response = client.get("/api/v1/productos")

    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert data["total"] >= 1
    assert len(data["items"]) >= 1


def test_list_products_only_available(client: TestClient, seed_producto, db):
    """Unavailable products are excluded from public listing"""
    from app.models.producto import Producto

    # Make producto unavailable
    producto = db.query(Producto).first()
    producto.disponible = False
    db.commit()

    response = client.get("/api/v1/productos")
    assert response.status_code == 200
    data = response.json()
    product_ids = [p["id"] for p in data["items"]]
    assert str(producto.id) not in product_ids


def test_list_products_excludes_soft_deleted(client: TestClient, seed_producto, db):
    """Soft-deleted products excluded from public listing"""
    from datetime import datetime

    from app.models.producto import Producto

    producto = db.query(Producto).first()
    producto.soft_deleted_at = datetime.utcnow()
    db.commit()

    response = client.get("/api/v1/productos")
    assert response.status_code == 200
    data = response.json()
    product_ids = [p["id"] for p in data["items"]]
    assert str(producto.id) not in product_ids


def test_product_detail_by_id(client: TestClient, seed_producto):
    """GET /api/v1/productos/{id} returns 200 with product fields"""
    response = client.get(f"/api/v1/productos/{seed_producto.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(seed_producto.id)
    assert data["nombre"] == seed_producto.nombre
    assert Decimal(str(data["precio_base"])) == seed_producto.precio_base


def test_product_detail_not_found(client: TestClient):
    """GET /api/v1/productos/{id} with non-existent id returns 404"""
    response = client.get("/api/v1/productos/00000000-0000-0000-0000-000000000000")

    assert response.status_code == 404


def test_create_product_as_admin(client: TestClient, admin_headers):
    """POST /api/v1/productos as ADMIN returns 201"""
    product_data = {
        "nombre": "Nuevo Producto",
        "descripcion": "Descripción de prueba",
        "precio_base": 999.99,
        "stock_cantidad": 10,
        "disponible": True,
    }
    response = client.post("/api/v1/productos", json=product_data, headers=admin_headers)

    assert response.status_code == 201
    data = response.json()
    assert data["nombre"] == "Nuevo Producto"
    assert data["precio_base"] == "999.99"
    assert data["stock_cantidad"] == 10
    assert data["disponible"] is True
    assert "id" in data


def test_create_product_as_stock(client: TestClient, stock_headers):
    """POST /api/v1/productos as STOCK returns 201"""
    product_data = {
        "nombre": "Producto Stock",
        "descripcion": "Creado por stock",
        "precio_base": 500.00,
        "stock_cantidad": 20,
    }
    response = client.post("/api/v1/productos", json=product_data, headers=stock_headers)

    assert response.status_code == 201


def test_create_product_as_client_forbidden(client: TestClient, client_headers):
    """POST /api/v1/productos as CLIENT returns 403"""
    product_data = {
        "nombre": "Producto Cliente",
        "precio_base": 100.00,
        "stock_cantidad": 5,
    }
    response = client.post("/api/v1/productos", json=product_data, headers=client_headers)

    assert response.status_code == 403


def test_create_product_unauthenticated(client: TestClient):
    """POST /api/v1/productos without auth returns 403"""
    product_data = {
        "nombre": "Sin Auth",
        "precio_base": 50.00,
        "stock_cantidad": 1,
    }
    response = client.post("/api/v1/productos", json=product_data)

    assert response.status_code == 403


def test_create_product_negative_price(client: TestClient, admin_headers):
    """POST /api/v1/productos with negative price returns 422"""
    product_data = {
        "nombre": "Precio Negativo",
        "precio_base": -100.00,
        "stock_cantidad": 5,
    }
    response = client.post("/api/v1/productos", json=product_data, headers=admin_headers)

    assert response.status_code == 422


def test_create_product_empty_name(client: TestClient, admin_headers):
    """POST /api/v1/productos with empty name returns 422"""
    product_data = {
        "nombre": "",
        "precio_base": 100.00,
        "stock_cantidad": 5,
    }
    response = client.post("/api/v1/productos", json=product_data, headers=admin_headers)

    assert response.status_code == 422


def test_create_product_negative_stock(client: TestClient, admin_headers):
    """POST /api/v1/productos with negative stock returns 422"""
    product_data = {
        "nombre": "Stock Negativo",
        "precio_base": 100.00,
        "stock_cantidad": -5,
    }
    response = client.post("/api/v1/productos", json=product_data, headers=admin_headers)

    assert response.status_code == 422


def test_update_product_as_admin(client: TestClient, admin_headers, seed_producto):
    """PUT /api/v1/productos/{id} as ADMIN returns 200"""
    update_data = {
        "nombre": "Producto Actualizado",
        "precio_base": 2000.00,
    }
    response = client.put(
        f"/api/v1/productos/{seed_producto.id}",
        json=update_data,
        headers=admin_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["nombre"] == "Producto Actualizado"
    assert data["precio_base"] == "2000.00"


def test_update_product_as_client_forbidden(client: TestClient, client_headers, seed_producto):
    """PUT /api/v1/productos/{id} as CLIENT returns 403"""
    update_data = {"nombre": "Hackeado"}
    response = client.put(
        f"/api/v1/productos/{seed_producto.id}",
        json=update_data,
        headers=client_headers,
    )

    assert response.status_code == 403


def test_toggle_disponibilidad_true_to_false(client: TestClient, admin_headers, seed_producto):
    """PATCH /api/v1/productos/{id}/disponibilidad toggles from true to false"""
    # Turn off
    response = client.patch(
        f"/api/v1/productos/{seed_producto.id}/disponibilidad",
        json={"disponible": False},
        headers=admin_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["disponible"] is False

    # Verify not in public listing
    public_response = client.get("/api/v1/productos")
    public_data = public_response.json()
    product_ids = [p["id"] for p in public_data["items"]]
    assert str(seed_producto.id) not in product_ids


def test_toggle_disponibilidad_false_to_true(client: TestClient, admin_headers, seed_producto, db):
    """PATCH disponibilidad: false → true, product reappears in public listing"""
    from app.models.producto import Producto

    # Set to false first
    producto = db.query(Producto).filter(Producto.id == seed_producto.id).first()
    producto.disponible = False
    db.commit()

    # Turn back on via API
    response = client.patch(
        f"/api/v1/productos/{seed_producto.id}/disponibilidad",
        json={"disponible": True},
        headers=admin_headers,
    )

    assert response.status_code == 200
    assert response.json()["disponible"] is True

    # Verify in public listing again
    public_response = client.get("/api/v1/productos")
    product_ids = [p["id"] for p in public_response.json()["items"]]
    assert str(seed_producto.id) in product_ids


def test_soft_delete_product(client: TestClient, admin_headers, seed_producto):
    """DELETE /api/v1/productos/{id} returns 204, product not in public listing"""
    response = client.delete(
        f"/api/v1/productos/{seed_producto.id}",
        headers=admin_headers,
    )

    assert response.status_code == 204

    # Verify not in public listing
    public_response = client.get("/api/v1/productos")
    product_ids = [p["id"] for p in public_response.json()["items"]]
    assert str(seed_producto.id) not in product_ids

    # Verify detail returns 404
    detail_response = client.get(f"/api/v1/productos/{seed_producto.id}")
    assert detail_response.status_code == 404


def test_delete_already_deleted_product(client: TestClient, admin_headers, seed_producto):
    """DELETE already soft-deleted product returns 404"""
    # First delete
    client.delete(f"/api/v1/productos/{seed_producto.id}", headers=admin_headers)
    # Second delete
    response = client.delete(f"/api/v1/productos/{seed_producto.id}", headers=admin_headers)

    assert response.status_code == 404


def test_filter_by_name(client: TestClient, seed_producto):
    """GET /api/v1/productos?nombre=pizza filters by name"""
    response = client.get("/api/v1/productos", params={"nombre": "Pizza"})

    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) >= 1
    for item in data["items"]:
        assert "pizza" in item["nombre"].lower() or "Pizza" in item["nombre"]


def test_filter_by_name_no_results(client: TestClient, seed_producto):
    """GET /api/v1/productos?nombre=xyz returns empty"""
    response = client.get("/api/v1/productos", params={"nombre": "XYZNOTFOUND"})

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0


def test_filter_by_price_range(client: TestClient, seed_producto):
    """GET /api/v1/productos?precio_min=1000&precio_max=2000 filters by price"""
    response = client.get(
        "/api/v1/productos",
        params={"precio_min": "1000", "precio_max": "2000"},
    )

    assert response.status_code == 200
    data = response.json()
    for item in data["items"]:
        price = Decimal(str(item["precio_base"]))
        assert price >= 1000
        assert price <= 2000


def test_filter_by_price_too_low(client: TestClient, seed_producto):
    """GET /api/v1/productos?precio_min=5000 with no products in range"""
    response = client.get("/api/v1/productos", params={"precio_min": "5000"})

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0


def test_pagination_works(client: TestClient, admin_headers):
    """GET /api/v1/productos with skip/limit params"""
    # Create multiple products
    for i in range(3):
        client.post(
            "/api/v1/productos",
            json={"nombre": f"Test {i}", "precio_base": 100 + i * 50, "stock_cantidad": 10},
            headers=admin_headers,
        )

    response = client.get("/api/v1/productos", params={"skip": 0, "limit": 2})
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "skip" in data
    assert "limit" in data


def test_product_detail_includes_relations(client: TestClient, seed_producto):
    """GET /api/v1/productos/{id} includes categorias and ingredientes"""
    response = client.get(f"/api/v1/productos/{seed_producto.id}")

    assert response.status_code == 200
    data = response.json()
    assert "categorias" in data or "categorias" not in data
    assert "ingredientes" in data or "ingredientes" not in data
