"""
Tests for Admin Order Repository
"""

from datetime import datetime, timedelta
from uuid import UUID

import pytest
from sqlalchemy.orm import Session

from app.admin.repository import AdminOrderRepository
from app.models import User, UserRole
from app.models.pedido import Pedido
from app.models.estado_pedido import EstadoPedido
from app.models.forma_pago import FormaPago


@pytest.fixture
def setup_test_data(db: Session):
    """Setup test data: users, orders with different states"""
    # Create estado pedido records
    db.add(EstadoPedido(codigo="PENDIENTE", descripcion="Pendiente", orden=1, es_terminal=False))
    db.add(EstadoPedido(codigo="CONFIRMADO", descripcion="Confirmado", orden=2, es_terminal=False))
    db.add(EstadoPedido(codigo="CANCELADO", descripcion="Cancelado", orden=6, es_terminal=True))
    db.commit()

    # Create forma pago
    db.add(FormaPago(codigo="TARJETA", nombre="Tarjeta", habilitado=True))
    db.commit()

    # Create users
    user1 = User(
        id=UUID("00000000-0000-0000-0000-000000000001"),
        email="user1@example.com",
        hashed_password="hash1",
        full_name="Juan García",
    )
    user2 = User(
        id=UUID("00000000-0000-0000-0000-000000000002"),
        email="user2@example.com",
        hashed_password="hash2",
        full_name="María López",
    )
    db.add(user1)
    db.add(user2)
    db.commit()

    # Create orders
    now = datetime.utcnow()
    order1 = Pedido(
        id=UUID("10000000-0000-0000-0000-000000000001"),
        usuario_id=user1.id,
        estado_codigo="PENDIENTE",
        forma_pago_codigo="TARJETA",
        subtotal=100.0,
        costo_envio=50.0,
        total=150.0,
        created_at=now,
    )
    order2 = Pedido(
        id=UUID("10000000-0000-0000-0000-000000000002"),
        usuario_id=user1.id,
        estado_codigo="CONFIRMADO",
        forma_pago_codigo="TARJETA",
        subtotal=200.0,
        costo_envio=50.0,
        total=250.0,
        created_at=now - timedelta(days=1),
    )
    order3 = Pedido(
        id=UUID("10000000-0000-0000-0000-000000000003"),
        usuario_id=user2.id,
        estado_codigo="CANCELADO",
        forma_pago_codigo="TARJETA",
        subtotal=300.0,
        costo_envio=50.0,
        total=350.0,
        created_at=now - timedelta(days=2),
    )
    db.add(order1)
    db.add(order2)
    db.add(order3)
    db.commit()

    return {
        "user1": user1,
        "user2": user2,
        "order1": order1,
        "order2": order2,
        "order3": order3,
    }


def test_list_orders_admin_empty(db: Session):
    """Test listing orders when DB is empty"""
    repo = AdminOrderRepository(db)
    orders, total = repo.list_orders_admin(page=1, size=20)
    assert orders == []
    assert total == 0


def test_list_orders_admin_pagination(db: Session, setup_test_data):
    """Test pagination works correctly"""
    repo = AdminOrderRepository(db)
    
    # Get first page (size=2)
    orders_p1, total = repo.list_orders_admin(page=1, size=2)
    assert len(orders_p1) == 2
    assert total == 3
    
    # Get second page
    orders_p2, _ = repo.list_orders_admin(page=2, size=2)
    assert len(orders_p2) == 1


def test_list_orders_admin_estado_filter(db: Session, setup_test_data):
    """Test filtering by estado_codigo"""
    repo = AdminOrderRepository(db)
    
    orders, total = repo.list_orders_admin(estado_codigo="PENDIENTE")
    assert len(orders) == 1
    assert orders[0]["estado_codigo"] == "PENDIENTE"
    assert total == 1


def test_list_orders_admin_usuario_filter(db: Session, setup_test_data):
    """Test filtering by usuario_id"""
    repo = AdminOrderRepository(db)
    user1_id = UUID("00000000-0000-0000-0000-000000000001")
    
    orders, total = repo.list_orders_admin(usuario_id=user1_id)
    assert len(orders) == 2
    assert all(o["usuario_id"] == user1_id for o in orders)
    assert total == 2


def test_list_orders_admin_monto_filter(db: Session, setup_test_data):
    """Test filtering by amount range"""
    repo = AdminOrderRepository(db)
    
    # Min amount
    orders, total = repo.list_orders_admin(monto_min=250.0)
    assert len(orders) == 1
    assert orders[0]["total"] == 350.0
    
    # Max amount
    orders, total = repo.list_orders_admin(monto_max=200.0)
    assert len(orders) == 1
    assert orders[0]["total"] == 150.0
    
    # Range
    orders, total = repo.list_orders_admin(monto_min=150.0, monto_max=300.0)
    assert len(orders) == 2


def test_list_orders_admin_soft_deleted_excluded(db: Session, setup_test_data):
    """Test that soft-deleted orders are excluded"""
    data = setup_test_data
    
    # Soft-delete one order
    data["order1"].soft_deleted_at = datetime.utcnow()
    db.commit()
    
    repo = AdminOrderRepository(db)
    orders, total = repo.list_orders_admin()
    
    assert total == 2
    assert all(o["id"] != data["order1"].id for o in orders)


def test_list_orders_admin_user_names_joined(db: Session, setup_test_data):
    """Test that user full names are correctly joined"""
    repo = AdminOrderRepository(db)
    orders, _ = repo.list_orders_admin()
    
    # Find order from user1
    user1_orders = [o for o in orders if o["cliente_nombre"] == "Juan García"]
    assert len(user1_orders) == 2
    
    # Find order from user2
    user2_orders = [o for o in orders if o["cliente_nombre"] == "María López"]
    assert len(user2_orders) == 1


def test_list_orders_admin_ordering(db: Session, setup_test_data):
    """Test that orders are ordered by created_at DESC"""
    repo = AdminOrderRepository(db)
    orders, _ = repo.list_orders_admin()
    
    # Should be ordered newest first
    created_times = [o["created_at"] for o in orders]
    assert created_times == sorted(created_times, reverse=True)


def test_list_orders_admin_multiple_filters(db: Session, setup_test_data):
    """Test combining multiple filters"""
    repo = AdminOrderRepository(db)
    user1_id = UUID("00000000-0000-0000-0000-000000000001")
    
    orders, total = repo.list_orders_admin(
        usuario_id=user1_id,
        estado_codigo="PENDIENTE",
        monto_min=100.0,
    )
    
    assert len(orders) == 1
    assert orders[0]["usuario_id"] == user1_id
    assert orders[0]["estado_codigo"] == "PENDIENTE"
    assert orders[0]["total"] == 150.0
