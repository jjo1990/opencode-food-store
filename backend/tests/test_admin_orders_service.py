"""
Tests for Admin Order Service
"""

from datetime import datetime
from uuid import UUID

import pytest
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.admin.schemas import AdminChangeStateRequest
from app.admin.service import AdminService
from app.models import User, UserRole
from app.models.pedido import Pedido
from app.models.estado_pedido import EstadoPedido
from app.models.forma_pago import FormaPago
from app.models.producto import Producto
from app.models.detalle_pedido import DetallePedido
from app.models.historial_estado_pedido import HistorialEstadoPedido
from app.models.categoria import Categoria


@pytest.fixture
def setup_order_test_data(db: Session):
    """Setup test data for order state change tests"""
    # Create estado pedido
    for idx, codigo in enumerate(["PENDIENTE", "CONFIRMADO", "EN_PREPARACION", "EN_CAMINO", "ENTREGADO", "CANCELADO"]):
        es_terminal = codigo in ["ENTREGADO", "CANCELADO"]
        db.add(EstadoPedido(codigo=codigo, descripcion=codigo, orden=idx+1, es_terminal=es_terminal))
    db.commit()

    # Create forma pago
    db.add(FormaPago(codigo="TARJETA", nombre="Tarjeta", habilitado=True))
    db.commit()

    # Create users
    admin_user = User(
        id=UUID("00000000-0000-0000-0000-000000000010"),
        email="admin@test.com",
        hashed_password="hash_admin",
        full_name="Admin User",
    )
    client_user = User(
        id=UUID("00000000-0000-0000-0000-000000000020"),
        email="client@test.com",
        hashed_password="hash_client",
        full_name="Client User",
    )
    db.add(admin_user)
    db.add(client_user)
    db.commit()

    # Add ADMIN role to admin_user
    admin_role = UserRole(user_id=admin_user.id, role="ADMIN")
    db.add(admin_role)
    db.commit()

    # Create categoria for products
    categoria = Categoria(id=UUID("30000000-0000-0000-0000-000000000001"), nombre="Test")
    db.add(categoria)
    db.commit()

    # Create producto
    producto = Producto(
        id=UUID("40000000-0000-0000-0000-000000000001"),
        nombre="Producto Test",
        categoria_id=categoria.id,
        precio_base=100.0,
        stock_cantidad=50,
        disponible=True,
    )
    db.add(producto)
    db.commit()

    # Create pedido in PENDIENTE state
    pedido = Pedido(
        id=UUID("50000000-0000-0000-0000-000000000001"),
        usuario_id=client_user.id,
        estado_codigo="PENDIENTE",
        forma_pago_codigo="TARJETA",
        subtotal=100.0,
        costo_envio=50.0,
        total=150.0,
    )
    db.add(pedido)
    db.commit()

    # Add detalle
    detalle = DetallePedido(
        pedido_id=pedido.id,
        producto_id=producto.id,
        nombre_snapshot="Producto Test",
        precio_snapshot=100.0,
        cantidad=1,
        subtotal=100.0,
    )
    db.add(detalle)
    db.commit()

    # Add historial entry
    historial = HistorialEstadoPedido(
        pedido_id=pedido.id,
        estado_desde=None,
        estado_nuevo="PENDIENTE",
        actor_id=client_user.id,
    )
    db.add(historial)
    db.commit()

    return {
        "admin_user": admin_user,
        "client_user": client_user,
        "pedido": pedido,
        "producto": producto,
    }


def test_change_order_state_valid_transition(db: Session, setup_order_test_data):
    """Test valid state transition"""
    data = setup_order_test_data
    service = AdminService(db)

    request = AdminChangeStateRequest(nuevo_estado="CONFIRMADO", motivo="Auto approved")
    result = service.change_order_state_admin(
        data["pedido"].id, request, data["admin_user"]
    )

    assert result.estado_codigo == "CONFIRMADO"
    assert result.id == data["pedido"].id


def test_change_order_state_invalid_transition(db: Session, setup_order_test_data):
    """Test invalid state transition raises 422"""
    data = setup_order_test_data
    service = AdminService(db)

    # PENDIENTE -> EN_CAMINO is not valid (must go through CONFIRMADO, EN_PREPARACION)
    request = AdminChangeStateRequest(nuevo_estado="EN_CAMINO")

    with pytest.raises(HTTPException) as exc:
        service.change_order_state_admin(
            data["pedido"].id, request, data["admin_user"]
        )

    assert exc.value.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_change_order_state_terminal_state(db: Session, setup_order_test_data, db_session):
    """Test cannot transition from terminal state"""
    data = setup_order_test_data

    # Set order to terminal state ENTREGADO
    data["pedido"].estado_codigo = "ENTREGADO"
    db_session.commit()

    service = AdminService(db_session)
    request = AdminChangeStateRequest(nuevo_estado="CANCELADO")

    with pytest.raises(HTTPException) as exc:
        service.change_order_state_admin(
            data["pedido"].id, request, data["admin_user"]
        )

    assert exc.value.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_change_order_state_order_not_found(db: Session, setup_order_test_data):
    """Test 404 when order not found"""
    data = setup_order_test_data
    service = AdminService(db)

    fake_id = UUID("99999999-9999-9999-9999-999999999999")
    request = AdminChangeStateRequest(nuevo_estado="CONFIRMADO")

    with pytest.raises(HTTPException) as exc:
        service.change_order_state_admin(fake_id, request, data["admin_user"])

    assert exc.value.status_code == status.HTTP_404_NOT_FOUND


def test_change_order_state_creates_audit_entry(db: Session, setup_order_test_data):
    """Test that state change creates HistorialEstadoPedido entry"""
    data = setup_order_test_data
    service = AdminService(db)

    request = AdminChangeStateRequest(nuevo_estado="CONFIRMADO", motivo="Manual approval")
    service.change_order_state_admin(
        data["pedido"].id, request, data["admin_user"]
    )

    # Verify historial entry was created
    historial_entries = db.query(HistorialEstadoPedido).filter_by(
        pedido_id=data["pedido"].id
    ).all()

    assert len(historial_entries) == 2  # Initial + new transition
    latest = historial_entries[-1]
    assert latest.estado_desde == "PENDIENTE"
    assert latest.estado_nuevo == "CONFIRMADO"
    assert latest.actor_id == data["admin_user"].id
    assert latest.motivo == "Manual approval"


def test_change_order_state_role_unauthorized(db: Session, setup_order_test_data):
    """Test 403 when user lacks required role"""
    data = setup_order_test_data
    service = AdminService(db)

    # Create CLIENT role user (not authorized for EN_PREPARACION)
    otro_user = User(
        id=UUID("00000000-0000-0000-0000-000000000030"),
        email="otro@test.com",
        hashed_password="hash",
        full_name="Otro",
    )
    db.add(otro_user)
    client_role = UserRole(user_id=otro_user.id, role="CLIENT")
    db.add(client_role)
    db.commit()

    # Transition to CONFIRMADO first
    data["pedido"].estado_codigo = "CONFIRMADO"
    db.commit()

    # Try EN_PREPARACION (requires ADMIN or PEDIDOS)
    request = AdminChangeStateRequest(nuevo_estado="EN_PREPARACION")

    with pytest.raises(HTTPException) as exc:
        service.change_order_state_admin(
            data["pedido"].id, request, otro_user
        )

    assert exc.value.status_code == status.HTTP_403_FORBIDDEN


def test_list_orders_admin(db: Session, setup_order_test_data):
    """Test list_orders_admin service method"""
    service = AdminService(db)
    result = service.list_orders_admin(page=1, size=20)

    assert result.total >= 1
    assert len(result.items) >= 1
    assert result.page == 1
    assert result.pages >= 1


def test_list_orders_admin_with_filters(db: Session, setup_order_test_data):
    """Test list_orders_admin with filters"""
    data = setup_order_test_data
    service = AdminService(db)

    result = service.list_orders_admin(
        estado_codigo="PENDIENTE",
        usuario_id=data["client_user"].id,
    )

    assert result.total >= 1
    assert all(item.estado_codigo == "PENDIENTE" for item in result.items)
    assert all(item.usuario_id == data["client_user"].id for item in result.items)
