"""
Tests for Checkout validation endpoint
"""

from decimal import Decimal
from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


def test_validate_valid_items(client: TestClient, seed_producto):
    """POST /api/v1/checkout/validar with valid items returns 200"""
    payload = {
        "items": [
            {
                "producto_id": str(seed_producto.id),
                "cantidad": 2,
                "precio_snapshot": str(seed_producto.precio_base),
                "personalizacion": [],
            }
        ]
    }
    response = client.post("/api/v1/checkout/validar", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["valido"] is True
    assert len(data["errores"]) == 0
    assert len(data["detalles"]) == 1
    assert data["detalles"][0]["nombre"] == seed_producto.nombre


def test_validate_product_not_found(client: TestClient):
    """POST /api/v1/checkout/validar with non-existent product returns errors"""
    payload = {
        "items": [
            {
                "producto_id": "00000000-0000-0000-0000-000000000000",
                "cantidad": 1,
                "precio_snapshot": "100.00",
                "personalizacion": [],
            }
        ]
    }
    response = client.post("/api/v1/checkout/validar", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["valido"] is False
    assert len(data["errores"]) >= 1


def test_validate_product_unavailable(client: TestClient, seed_producto, db):
    """POST /api/v1/checkout/validar with unavailable product returns errors"""
    from app.models.producto import Producto

    producto = db.query(Producto).filter(Producto.id == seed_producto.id).first()
    producto.disponible = False
    db.commit()

    payload = {
        "items": [
            {
                "producto_id": str(seed_producto.id),
                "cantidad": 1,
                "precio_snapshot": str(seed_producto.precio_base),
                "personalizacion": [],
            }
        ]
    }
    response = client.post("/api/v1/checkout/validar", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["valido"] is False
    assert len(data["errores"]) >= 1


def test_validate_insufficient_stock(client: TestClient, seed_producto):
    """POST /api/v1/checkout/validar with quantity > stock returns errors"""
    payload = {
        "items": [
            {
                "producto_id": str(seed_producto.id),
                "cantidad": 99999,
                "precio_snapshot": str(seed_producto.precio_base),
                "personalizacion": [],
            }
        ]
    }
    response = client.post("/api/v1/checkout/validar", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["valido"] is False
    assert any("stock" in err.lower() for err in data["errores"])


def test_validate_price_changed(client: TestClient, seed_producto):
    """POST /api/v1/checkout/validar with wrong price returns warnings"""
    wrong_price = seed_producto.precio_base + Decimal("100.00")
    payload = {
        "items": [
            {
                "producto_id": str(seed_producto.id),
                "cantidad": 1,
                "precio_snapshot": str(wrong_price),
                "personalizacion": [],
            }
        ]
    }
    response = client.post("/api/v1/checkout/validar", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert len(data["advertencias"]) >= 1
    assert "precio" in data["advertencias"][0].lower()


def test_validate_empty_cart(client: TestClient):
    """POST /api/v1/checkout/validar with empty items list"""
    payload = {"items": []}
    response = client.post("/api/v1/checkout/validar", json=payload)

    assert response.status_code == 200
    data = response.json()
    # Empty cart should be valid (no errors) since there's nothing to validate
    assert data["valido"] is True


def test_validate_duplicate_items(client: TestClient, seed_producto):
    """POST /api/v1/checkout/validar with duplicate items aggregates quantity"""
    payload = {
        "items": [
            {
                "producto_id": str(seed_producto.id),
                "cantidad": 1,
                "precio_snapshot": str(seed_producto.precio_base),
                "personalizacion": [],
            },
            {
                "producto_id": str(seed_producto.id),
                "cantidad": 2,
                "precio_snapshot": str(seed_producto.precio_base),
                "personalizacion": [],
            },
        ]
    }
    response = client.post("/api/v1/checkout/validar", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["valido"] is True
    # Items should be aggregated into one detail entry
    assert len(data["detalles"]) == 1


def test_validate_multiple_products(client: TestClient, admin_headers, seed_producto):
    """POST /api/v1/checkout/validar with multiple different products"""
    # Create a second product
    product_data = {
        "nombre": "Second Product",
        "precio_base": 500.00,
        "stock_cantidad": 10,
    }
    create_resp = client.post("/api/v1/productos", json=product_data, headers=admin_headers)
    product2 = create_resp.json()

    payload = {
        "items": [
            {
                "producto_id": str(seed_producto.id),
                "cantidad": 1,
                "precio_snapshot": str(seed_producto.precio_base),
                "personalizacion": [],
            },
            {
                "producto_id": product2["id"],
                "cantidad": 1,
                "precio_snapshot": product2["precio_base"],
                "personalizacion": [],
            },
        ]
    }
    response = client.post("/api/v1/checkout/validar", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["valido"] is True
    assert len(data["detalles"]) == 2


def test_validate_non_autenticated_ok(client: TestClient, seed_producto):
    """POST /api/v1/checkout/validar works without authentication (public)"""
    payload = {
        "items": [
            {
                "producto_id": str(seed_producto.id),
                "cantidad": 1,
                "precio_snapshot": str(seed_producto.precio_base),
                "personalizacion": [],
            }
        ]
    }
    response = client.post("/api/v1/checkout/validar", json=payload)
    # Checkout validation is public - no authentication required
    assert response.status_code == 200
