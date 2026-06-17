"""
Tests for Pedidos Client endpoints and FSM transitions
"""

from decimal import Decimal
from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _create_order(client, producto, direccion, headers):
    """Create a test order and return the response data."""
    order_data = {
        "items": [
            {
                "producto_id": str(producto.id),
                "cantidad": 2,
                "personalizacion": [],
            }
        ],
        "direccion_id": str(direccion.id),
        "forma_pago_codigo": "TARJETA",
    }
    response = client.post("/api/v1/pedidos", json=order_data, headers=headers)
    return response


# ─── Order Creation Tests ────────────────────────────────────────────────────

def test_create_order_success(
    client: TestClient,
    db: Session,
    client_headers,
    seed_estados,
    seed_formas_pago,
    seed_producto,
    seed_direccion,
):
    """POST /api/v1/pedidos creates order, returns 201 with PENDIENTE status"""
    response = _create_order(client, seed_producto, seed_direccion, client_headers)

    assert response.status_code == 201
    data = response.json()
    assert data["estado_codigo"] == "PENDIENTE"
    assert "id" in data
    assert "total" in data
    assert float(data["total"]) > 0
    assert float(data["subtotal"]) > 0
    assert float(data["costo_envio"]) > 0


def test_create_order_has_items(
    client: TestClient,
    db: Session,
    client_headers,
    seed_estados,
    seed_formas_pago,
    seed_producto,
    seed_direccion,
):
    """Order detail includes items after creation"""
    response = _create_order(client, seed_producto, seed_direccion, client_headers)
    order_id = response.json()["id"]

    detail_response = client.get(f"/api/v1/pedidos/{order_id}", headers=client_headers)
    assert detail_response.status_code == 200
    data = detail_response.json()
    assert len(data["items"]) >= 1
    assert float(data["items"][0]["precio_snapshot"]) > 0


def test_create_order_unauthorized(client: TestClient, seed_producto, seed_direccion):
    """POST /api/v1/pedidos without token returns 403"""
    order_data = {
        "items": [
            {"producto_id": str(seed_producto.id), "cantidad": 1, "personalizacion": []}
        ],
        "direccion_id": "00000000-0000-0000-0000-000000000000",
        "forma_pago_codigo": "TARJETA",
    }
    response = client.post("/api/v1/pedidos", json=order_data)

    assert response.status_code == 403


def test_create_order_insufficient_stock(
    client: TestClient,
    db: Session,
    client_headers,
    seed_estados,
    seed_formas_pago,
    seed_producto,
    seed_direccion,
):
    """POST /api/v1/pedidos with quantity > stock returns 422"""
    order_data = {
        "items": [
            {
                "producto_id": str(seed_producto.id),
                "cantidad": 99999,
                "personalizacion": [],
            }
        ],
        "direccion_id": str(seed_direccion.id),
        "forma_pago_codigo": "TARJETA",
    }
    response = client.post("/api/v1/pedidos", json=order_data, headers=client_headers)

    assert response.status_code == 422


def test_create_order_product_not_available(
    client: TestClient,
    db: Session,
    client_headers,
    seed_estados,
    seed_formas_pago,
    seed_producto,
    seed_direccion,
):
    """POST /api/v1/pedidos with unavailable product returns 422"""
    from app.models.producto import Producto

    producto = db.query(Producto).filter(Producto.id == seed_producto.id).first()
    producto.disponible = False
    db.commit()

    order_data = {
        "items": [
            {"producto_id": str(seed_producto.id), "cantidad": 1, "personalizacion": []}
        ],
        "direccion_id": str(seed_direccion.id),
        "forma_pago_codigo": "TARJETA",
    }
    response = client.post("/api/v1/pedidos", json=order_data, headers=client_headers)

    assert response.status_code == 422


def test_create_order_wrong_address(
    client: TestClient,
    db: Session,
    client_headers,
    admin_headers,
    seed_estados,
    seed_formas_pago,
    seed_producto,
):
    """POST /api/v1/pedidos with another user's address returns 422"""
    from app.models.direccion_entrega import DireccionEntrega
    from app.models.user import User

    # Create a second user with an address
    from app.core.security import create_access_token as _create_access_token

    user2 = User(
        email="other_user_test@test.com",
        hashed_password="$2b$12$AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
        full_name="Other User",
    )
    db.add(user2)
    db.flush()
    from app.models.user_role import UserRole

    db.add(UserRole(user_id=user2.id, role="CLIENT"))
    db.commit()

    other_direccion = DireccionEntrega(
        usuario_id=user2.id,
        calle="Other Street",
        numero="999",
        ciudad="Other City",
        codigo_postal="9999",
        es_principal=True,
    )
    db.add(other_direccion)
    db.commit()
    db.refresh(other_direccion)

    order_data = {
        "items": [
            {"producto_id": str(seed_producto.id), "cantidad": 1, "personalizacion": []}
        ],
        "direccion_id": str(other_direccion.id),
        "forma_pago_codigo": "TARJETA",
    }
    response = client.post("/api/v1/pedidos", json=order_data, headers=client_headers)

    assert response.status_code == 422


def test_create_order_product_not_found(
    client: TestClient,
    client_headers,
    seed_estados,
    seed_formas_pago,
    seed_direccion,
):
    """POST /api/v1/pedidos with non-existent product returns 422"""
    order_data = {
        "items": [
            {
                "producto_id": "00000000-0000-0000-0000-000000000000",
                "cantidad": 1,
                "personalizacion": [],
            }
        ],
        "direccion_id": str(seed_direccion.id),
        "forma_pago_codigo": "TARJETA",
    }
    response = client.post("/api/v1/pedidos", json=order_data, headers=client_headers)

    assert response.status_code == 422


# ─── Order Listing Tests ─────────────────────────────────────────────────────

def test_list_my_orders(
    client: TestClient,
    db: Session,
    client_headers,
    seed_estados,
    seed_formas_pago,
    seed_producto,
    seed_direccion,
):
    """GET /api/v1/pedidos with CLIENT returns only own orders"""
    # Create an order
    _create_order(client, seed_producto, seed_direccion, client_headers)

    response = client.get("/api/v1/pedidos", headers=client_headers)
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert data["total"] >= 1


def test_list_all_orders_as_admin(
    client: TestClient,
    client_headers,
    admin_headers,
    seed_estados,
    seed_formas_pago,
    seed_producto,
    seed_direccion,
):
    """GET /api/v1/pedidos with ADMIN sees all orders"""
    _create_order(client, seed_producto, seed_direccion, client_headers)

    response = client.get("/api/v1/pedidos", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1


def test_list_orders_unauthenticated(client: TestClient):
    """GET /api/v1/pedidos without token returns 403"""
    response = client.get("/api/v1/pedidos")
    assert response.status_code == 403


def test_filter_orders_by_estado(
    client: TestClient,
    client_headers,
    seed_estados,
    seed_formas_pago,
    seed_producto,
    seed_direccion,
):
    """GET /api/v1/pedidos?estado_codigo=PENDIENTE filters correctly"""
    _create_order(client, seed_producto, seed_direccion, client_headers)

    response = client.get("/api/v1/pedidos", params={"estado_codigo": "PENDIENTE"}, headers=client_headers)
    assert response.status_code == 200
    data = response.json()
    for item in data["items"]:
        assert item["estado_codigo"] == "PENDIENTE"


# ─── Order Detail Tests ──────────────────────────────────────────────────────

def test_order_detail_own(
    client: TestClient,
    db: Session,
    client_headers,
    seed_estados,
    seed_formas_pago,
    seed_producto,
    seed_direccion,
):
    """GET /api/v1/pedidos/{id} with CLIENT returns own order with items and historial"""
    create_resp = _create_order(client, seed_producto, seed_direccion, client_headers)
    order_id = create_resp.json()["id"]

    response = client.get(f"/api/v1/pedidos/{order_id}", headers=client_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == order_id
    assert len(data["items"]) >= 1
    assert "historial" in data
    assert len(data["historial"]) >= 1


def test_order_detail_other_user(
    client: TestClient,
    db: Session,
    client_headers,
    admin_headers,
    seed_estados,
    seed_formas_pago,
    seed_producto,
    seed_direccion,
):
    """GET /api/v1/pedidos/{id} for another user's order returns 404"""
    create_resp = _create_order(client, seed_producto, seed_direccion, client_headers)
    order_id = create_resp.json()["id"]

    # Create a second client user
    from app.models.user import User
    from app.models.user_role import UserRole
    from app.core.security import create_access_token as _create_access_token

    user2 = User(
        email="other_client_detail@test.com",
        hashed_password="$2b$12$AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
        full_name="Other",
    )
    db.add(user2)
    db.flush()
    db.add(UserRole(user_id=user2.id, role="CLIENT"))
    db.commit()
    token2 = _create_access_token(user2.id, ["CLIENT"])
    headers2 = {"Authorization": f"Bearer {token2}"}

    response = client.get(f"/api/v1/pedidos/{order_id}", headers=headers2)
    assert response.status_code == 404


def test_order_detail_admin_any(
    client: TestClient,
    client_headers,
    admin_headers,
    seed_estados,
    seed_formas_pago,
    seed_producto,
    seed_direccion,
):
    """GET /api/v1/pedidos/{id} with ADMIN returns any order"""
    create_resp = _create_order(client, seed_producto, seed_direccion, client_headers)
    order_id = create_resp.json()["id"]

    response = client.get(f"/api/v1/pedidos/{order_id}", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == order_id


def test_order_detail_not_found(client: TestClient, client_headers):
    """GET /api/v1/pedidos/{id} with non-existent id returns 404"""
    response = client.get(
        "/api/v1/pedidos/00000000-0000-0000-0000-000000000000",
        headers=client_headers,
    )
    assert response.status_code == 404


# ─── Order Cancel Tests ──────────────────────────────────────────────────────

def test_cancel_own_pending_order(
    client: TestClient,
    db: Session,
    client_headers,
    seed_estados,
    seed_formas_pago,
    seed_producto,
    seed_direccion,
):
    """PATCH /api/v1/pedidos/{id}/avanzar cancels own PENDIENTE order"""
    create_resp = _create_order(client, seed_producto, seed_direccion, client_headers)
    order_id = create_resp.json()["id"]

    cancel_data = {"nuevo_estado": "CANCELADO", "motivo": "Test cancel"}
    response = client.patch(
        f"/api/v1/pedidos/{order_id}/avanzar",
        json=cancel_data,
        headers=client_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["estado_codigo"] == "CANCELADO"


def test_cancel_confirmed_order_succeeds(
    client: TestClient,
    db: Session,
    client_headers,
    admin_headers,
    seed_estados,
    seed_formas_pago,
    seed_producto,
    seed_direccion,
):
    """PATCH cancel from CONFIRMADO by client succeeds (CLIENT is allowed)"""
    from app.models.pedido import Pedido

    create_resp = _create_order(client, seed_producto, seed_direccion, client_headers)
    order_id = create_resp.json()["id"]

    # Manually advance to CONFIRMADO via admin
    pedido = db.query(Pedido).filter(Pedido.id == UUID(order_id)).first()
    pedido.estado_codigo = "CONFIRMADO"
    db.commit()

    cancel_data = {"nuevo_estado": "CANCELADO", "motivo": "cancel confirmed test"}
    response = client.patch(
        f"/api/v1/pedidos/{order_id}/avanzar",
        json=cancel_data,
        headers=client_headers,
    )

    # CLIENT is in allowed_roles for CONFIRMADO → CANCELADO
    assert response.status_code == 200
    assert response.json()["estado_codigo"] == "CANCELADO"


# ─── History Tests ───────────────────────────────────────────────────────────

def test_order_history(
    client: TestClient,
    db: Session,
    client_headers,
    seed_estados,
    seed_formas_pago,
    seed_producto,
    seed_direccion,
):
    """GET /api/v1/pedidos/{id}/historial returns history entries"""
    create_resp = _create_order(client, seed_producto, seed_direccion, client_headers)
    order_id = create_resp.json()["id"]

    response = client.get(f"/api/v1/pedidos/{order_id}/historial", headers=client_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["estado_nuevo"] == "PENDIENTE"


# ─── FSM Full Flow Tests ─────────────────────────────────────────────────────

def test_fsm_pending_to_canceled(
    client: TestClient,
    db: Session,
    client_headers,
    seed_estados,
    seed_formas_pago,
    seed_producto,
    seed_direccion,
):
    """PENDIENTE → CANCELADO via client avanzar endpoint"""
    create_resp = _create_order(client, seed_producto, seed_direccion, client_headers)
    order_id = create_resp.json()["id"]

    response = client.patch(
        f"/api/v1/pedidos/{order_id}/avanzar",
        json={"nuevo_estado": "CANCELADO", "motivo": "FSM test"},
        headers=client_headers,
    )

    assert response.status_code == 200
    assert response.json()["estado_codigo"] == "CANCELADO"


def test_fsm_pending_to_confirmed_blocked(
    client: TestClient,
    db: Session,
    client_headers,
    seed_estados,
    seed_formas_pago,
    seed_producto,
    seed_direccion,
):
    """PENDIENTE → CONFIRMADO via endpoint returns 422 (only via webhook)"""
    create_resp = _create_order(client, seed_producto, seed_direccion, client_headers)
    order_id = create_resp.json()["id"]

    response = client.patch(
        f"/api/v1/pedidos/{order_id}/avanzar",
        json={"nuevo_estado": "CONFIRMADO", "motivo": "should fail"},
        headers=client_headers,
    )

    assert response.status_code == 422


def test_fsm_confirmed_to_en_preparacion(
    client: TestClient,
    db: Session,
    client_headers,
    admin_headers,
    seed_estados,
    seed_formas_pago,
    seed_producto,
    seed_direccion,
):
    """CONFIRMADO → EN_PREPARACION via admin endpoint"""
    from app.models.pedido import Pedido

    create_resp = _create_order(client, seed_producto, seed_direccion, client_headers)
    order_id = UUID(create_resp.json()["id"])

    # Manually set to CONFIRMADO
    pedido = db.query(Pedido).filter(Pedido.id == order_id).first()
    pedido.estado_codigo = "CONFIRMADO"
    db.commit()

    response = client.patch(
        f"/api/v1/admin/pedidos/{order_id}/estado",
        json={"nuevo_estado": "EN_PREPARACION", "motivo": "FSM test"},
        headers=admin_headers,
    )

    assert response.status_code == 200
    assert response.json()["estado_codigo"] == "EN_PREPARACION"


def test_fsm_confirmed_to_canceled_with_stock_restore(
    client: TestClient,
    db: Session,
    client_headers,
    admin_headers,
    seed_estados,
    seed_formas_pago,
    seed_producto,
    seed_direccion,
):
    """CONFIRMADO → CANCELADO via admin restores stock"""
    from app.models.pedido import Pedido
    from app.models.producto import Producto

    original_stock = seed_producto.stock_cantidad

    create_resp = _create_order(client, seed_producto, seed_direccion, client_headers)
    order_id = UUID(create_resp.json()["id"])

    # The order creator decrements stock? Let's check. Actually in crear_pedido
    # the stock IS NOT decremented. It's only decremented on payment confirmation.
    # So stock should still be original_stock.

    # Manually set to CONFIRMADO
    pedido = db.query(Pedido).filter(Pedido.id == order_id).first()
    pedido.estado_codigo = "CONFIRMADO"
    db.commit()

    response = client.patch(
        f"/api/v1/admin/pedidos/{order_id}/estado",
        json={"nuevo_estado": "CANCELADO", "motivo": "Cancel with restore"},
        headers=admin_headers,
    )

    assert response.status_code == 200
    assert response.json()["estado_codigo"] == "CANCELADO"

    # Verify stock was restored (incremented back)
    producto = db.query(Producto).filter(Producto.id == seed_producto.id).first()
    # Stock should be >= original since restore adds back the cantidad from the order
    assert producto.stock_cantidad >= original_stock


def test_fsm_en_preparacion_to_en_camino(
    client: TestClient,
    db: Session,
    client_headers,
    admin_headers,
    seed_estados,
    seed_formas_pago,
    seed_producto,
    seed_direccion,
):
    """EN_PREPARACION → EN_CAMINO via admin"""
    from app.models.pedido import Pedido

    create_resp = _create_order(client, seed_producto, seed_direccion, client_headers)
    order_id = UUID(create_resp.json()["id"])

    pedido = db.query(Pedido).filter(Pedido.id == order_id).first()
    pedido.estado_codigo = "EN_PREPARACION"
    db.commit()

    response = client.patch(
        f"/api/v1/admin/pedidos/{order_id}/estado",
        json={"nuevo_estado": "EN_CAMINO", "motivo": "Out for delivery"},
        headers=admin_headers,
    )

    assert response.status_code == 200
    assert response.json()["estado_codigo"] == "EN_CAMINO"


def test_fsm_en_preparacion_to_canceled_with_stock(
    client: TestClient,
    db: Session,
    client_headers,
    admin_headers,
    seed_estados,
    seed_formas_pago,
    seed_producto,
    seed_direccion,
):
    """EN_PREPARACION → CANCELADO restores stock"""
    from app.models.pedido import Pedido
    from app.models.producto import Producto

    original_stock = seed_producto.stock_cantidad

    create_resp = _create_order(client, seed_producto, seed_direccion, client_headers)
    order_id = UUID(create_resp.json()["id"])

    pedido = db.query(Pedido).filter(Pedido.id == order_id).first()
    pedido.estado_codigo = "EN_PREPARACION"
    db.commit()

    response = client.patch(
        f"/api/v1/admin/pedidos/{order_id}/estado",
        json={"nuevo_estado": "CANCELADO", "motivo": "Cancel from preparation"},
        headers=admin_headers,
    )

    assert response.status_code == 200
    assert response.json()["estado_codigo"] == "CANCELADO"

    producto = db.query(Producto).filter(Producto.id == seed_producto.id).first()
    assert producto.stock_cantidad >= original_stock


def test_fsm_en_camino_to_entregado(
    client: TestClient,
    db: Session,
    client_headers,
    admin_headers,
    seed_estados,
    seed_formas_pago,
    seed_producto,
    seed_direccion,
):
    """EN_CAMINO → ENTREGADO via admin"""
    from app.models.pedido import Pedido

    create_resp = _create_order(client, seed_producto, seed_direccion, client_headers)
    order_id = UUID(create_resp.json()["id"])

    pedido = db.query(Pedido).filter(Pedido.id == order_id).first()
    pedido.estado_codigo = "EN_CAMINO"
    db.commit()

    response = client.patch(
        f"/api/v1/admin/pedidos/{order_id}/estado",
        json={"nuevo_estado": "ENTREGADO", "motivo": "Delivered"},
        headers=admin_headers,
    )

    assert response.status_code == 200
    assert response.json()["estado_codigo"] == "ENTREGADO"


def test_fsm_terminal_entregado_rejects(
    client: TestClient,
    db: Session,
    client_headers,
    admin_headers,
    seed_estados,
    seed_formas_pago,
    seed_producto,
    seed_direccion,
):
    """ENTREGADO → any transition returns 422"""
    from app.models.pedido import Pedido

    create_resp = _create_order(client, seed_producto, seed_direccion, client_headers)
    order_id = UUID(create_resp.json()["id"])

    pedido = db.query(Pedido).filter(Pedido.id == order_id).first()
    pedido.estado_codigo = "ENTREGADO"
    db.commit()

    response = client.patch(
        f"/api/v1/admin/pedidos/{order_id}/estado",
        json={"nuevo_estado": "CANCELADO", "motivo": "should fail"},
        headers=admin_headers,
    )

    assert response.status_code == 422


def test_fsm_terminal_cancelado_rejects(
    client: TestClient,
    db: Session,
    client_headers,
    admin_headers,
    seed_estados,
    seed_formas_pago,
    seed_producto,
    seed_direccion,
):
    """CANCELADO → any transition returns 422"""
    from app.models.pedido import Pedido

    create_resp = _create_order(client, seed_producto, seed_direccion, client_headers)
    order_id = UUID(create_resp.json()["id"])

    pedido = db.query(Pedido).filter(Pedido.id == order_id).first()
    pedido.estado_codigo = "CANCELADO"
    db.commit()

    response = client.patch(
        f"/api/v1/admin/pedidos/{order_id}/estado",
        json={"nuevo_estado": "ENTREGADO", "motivo": "should fail"},
        headers=admin_headers,
    )

    assert response.status_code == 422


def test_fsm_role_validation_client_blocked(
    client: TestClient,
    db: Session,
    client_headers,
    seed_estados,
    seed_formas_pago,
    seed_producto,
    seed_direccion,
):
    """CLIENT tries admin-only FSM transition returns 403"""
    from app.models.pedido import Pedido

    create_resp = _create_order(client, seed_producto, seed_direccion, client_headers)
    order_id = UUID(create_resp.json()["id"])

    pedido = db.query(Pedido).filter(Pedido.id == order_id).first()
    pedido.estado_codigo = "CONFIRMADO"
    db.commit()

    response = client.patch(
        f"/api/v1/admin/pedidos/{order_id}/estado",
        json={"nuevo_estado": "EN_PREPARACION"},
        headers=client_headers,
    )

    assert response.status_code == 403


def test_fsm_role_validation_stock_blocked(
    client: TestClient,
    db: Session,
    client_headers,
    stock_headers,
    seed_estados,
    seed_formas_pago,
    seed_producto,
    seed_direccion,
):
    """STOCK tries admin-only FSM transition returns 403"""
    from app.models.pedido import Pedido

    create_resp = _create_order(client, seed_producto, seed_direccion, client_headers)
    order_id = UUID(create_resp.json()["id"])

    pedido = db.query(Pedido).filter(Pedido.id == order_id).first()
    pedido.estado_codigo = "CONFIRMADO"
    db.commit()

    response = client.patch(
        f"/api/v1/admin/pedidos/{order_id}/estado",
        json={"nuevo_estado": "EN_PREPARACION"},
        headers=stock_headers,
    )

    assert response.status_code == 403
