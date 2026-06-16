"""
Integration tests for Admin Order Endpoints
"""

from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.models import User, UserRole
from app.models.categoria import Categoria
from app.models.detalle_pedido import DetallePedido
from app.models.estado_pedido import EstadoPedido
from app.models.forma_pago import FormaPago
from app.models.historial_estado_pedido import HistorialEstadoPedido
from app.models.pedido import Pedido
from app.models.producto import Producto

client = TestClient(app)


@pytest.fixture
def auth_tokens(db: Session):
    """Create test users with different roles and get their tokens"""
    from app.core.security import create_access_token

    # Create estado pedido
    for idx, codigo in enumerate(["PENDIENTE", "CONFIRMADO", "CANCELADO"]):
        db.add(
            EstadoPedido(
                codigo=codigo,
                descripcion=codigo,
                orden=idx + 1,
                es_terminal=(codigo == "CANCELADO"),
            )
        )
    db.commit()

    # Create users
    admin_user = User(
        id=UUID("00000000-0000-0000-0000-000000000010"),
        email="admin@test.com",
        hashed_password="$2b$12$" + "a" * 53,  # Valid bcrypt hash format
        full_name="Admin",
    )
    client_user = User(
        id=UUID("00000000-0000-0000-0000-000000000020"),
        email="client@test.com",
        hashed_password="$2b$12$" + "b" * 53,
        full_name="Client",
    )
    pedidos_user = User(
        id=UUID("00000000-0000-0000-0000-000000000030"),
        email="pedidos@test.com",
        hashed_password="$2b$12$" + "c" * 53,
        full_name="Pedidos",
    )

    db.add(admin_user)
    db.add(client_user)
    db.add(pedidos_user)
    db.commit()

    # Assign roles
    admin_role = UserRole(user_id=admin_user.id, role="ADMIN")
    client_role = UserRole(user_id=client_user.id, role="CLIENT")
    pedidos_role = UserRole(user_id=pedidos_user.id, role="PEDIDOS")

    db.add(admin_role)
    db.add(client_role)
    db.add(pedidos_role)
    db.commit()

    # Generate tokens
    admin_token = create_access_token({"sub": str(admin_user.id)})
    client_token = create_access_token({"sub": str(client_user.id)})
    pedidos_token = create_access_token({"sub": str(pedidos_user.id)})

    return {
        "admin_token": admin_token,
        "client_token": client_token,
        "pedidos_token": pedidos_token,
        "admin_user": admin_user,
        "client_user": client_user,
    }


@pytest.fixture
def setup_endpoint_test_data(db: Session, auth_tokens):
    """Setup test data for endpoint tests"""
    data = auth_tokens

    # Create forma pago
    db.add(FormaPago(codigo="TARJETA", nombre="Tarjeta", habilitado=True))
    db.commit()

    # Create categoria and producto
    categoria = Categoria(id=UUID("30000000-0000-0000-0000-000000000001"), nombre="Test")
    db.add(categoria)
    db.commit()

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

    # Create orders
    pedido1 = Pedido(
        id=UUID("50000000-0000-0000-0000-000000000001"),
        usuario_id=data["client_user"].id,
        estado_codigo="PENDIENTE",
        forma_pago_codigo="TARJETA",
        subtotal=100.0,
        costo_envio=50.0,
        total=150.0,
    )
    pedido2 = Pedido(
        id=UUID("50000000-0000-0000-0000-000000000002"),
        usuario_id=data["client_user"].id,
        estado_codigo="CONFIRMADO",
        forma_pago_codigo="TARJETA",
        subtotal=200.0,
        costo_envio=50.0,
        total=250.0,
    )

    db.add(pedido1)
    db.add(pedido2)
    db.commit()

    # Add detalles
    for pedido in [pedido1, pedido2]:
        detalle = DetallePedido(
            pedido_id=pedido.id,
            producto_id=producto.id,
            nombre_snapshot="Producto Test",
            precio_snapshot=100.0,
            cantidad=1,
            subtotal=100.0,
        )
        db.add(detalle)

        historial = HistorialEstadoPedido(
            pedido_id=pedido.id,
            estado_desde=None,
            estado_nuevo=pedido.estado_codigo,
            actor_id=data["client_user"].id,
        )
        db.add(historial)

    db.commit()

    data["pedido1"] = pedido1
    data["pedido2"] = pedido2
    data["producto"] = producto

    return data


def test_get_orders_list_without_token(db: Session):
    """Test 401 without token"""
    response = client.get("/api/v1/admin/pedidos")
    assert response.status_code == 403  # No credentials


def test_get_orders_list_with_admin_token(setup_endpoint_test_data):
    """Test 200 with admin token"""
    data = setup_endpoint_test_data
    headers = {"Authorization": f"Bearer {data['admin_token']}"}

    response = client.get("/api/v1/admin/pedidos", headers=headers)
    assert response.status_code == 200

    result = response.json()
    assert "items" in result
    assert "total" in result
    assert "page" in result
    assert "pages" in result


def test_get_orders_list_with_pedidos_token(setup_endpoint_test_data):
    """Test 200 with PEDIDOS role token"""
    data = setup_endpoint_test_data
    headers = {"Authorization": f"Bearer {data['pedidos_token']}"}

    response = client.get("/api/v1/admin/pedidos", headers=headers)
    assert response.status_code == 200


def test_get_orders_list_with_client_token(setup_endpoint_test_data):
    """Test 403 with CLIENT role token"""
    data = setup_endpoint_test_data
    headers = {"Authorization": f"Bearer {data['client_token']}"}

    response = client.get("/api/v1/admin/pedidos", headers=headers)
    assert response.status_code == 403


def test_get_orders_list_with_filters(setup_endpoint_test_data):
    """Test filters work end-to-end"""
    data = setup_endpoint_test_data
    headers = {"Authorization": f"Bearer {data['admin_token']}"}

    response = client.get(
        "/api/v1/admin/pedidos",
        params={"estado_codigo": "PENDIENTE"},
        headers=headers,
    )
    assert response.status_code == 200

    result = response.json()
    assert all(item["estado_codigo"] == "PENDIENTE" for item in result["items"])


def test_get_orders_list_pagination(setup_endpoint_test_data):
    """Test pagination works"""
    data = setup_endpoint_test_data
    headers = {"Authorization": f"Bearer {data['admin_token']}"}

    response = client.get(
        "/api/v1/admin/pedidos",
        params={"page": 1, "size": 1},
        headers=headers,
    )
    assert response.status_code == 200

    result = response.json()
    assert len(result["items"]) <= 1
    assert result["page"] == 1


def test_change_order_state_valid(setup_endpoint_test_data):
    """Test valid state change returns 200"""
    data = setup_endpoint_test_data
    headers = {"Authorization": f"Bearer {data['admin_token']}"}

    payload = {"nuevo_estado": "CONFIRMADO", "motivo": "Manual approval"}
    response = client.patch(
        f"/api/v1/admin/pedidos/{data['pedido1'].id}/estado",
        json=payload,
        headers=headers,
    )

    assert response.status_code == 200
    result = response.json()
    assert result["estado_codigo"] == "CONFIRMADO"


def test_change_order_state_invalid_transition(setup_endpoint_test_data):
    """Test invalid transition returns 422"""
    data = setup_endpoint_test_data
    headers = {"Authorization": f"Bearer {data['admin_token']}"}

    # CONFIRMADO -> PENDIENTE is not valid
    payload = {"nuevo_estado": "PENDIENTE"}
    response = client.patch(
        f"/api/v1/admin/pedidos/{data['pedido2'].id}/estado",
        json=payload,
        headers=headers,
    )

    assert response.status_code == 422


def test_change_order_state_not_found(setup_endpoint_test_data):
    """Test 404 for non-existent order"""
    data = setup_endpoint_test_data
    headers = {"Authorization": f"Bearer {data['admin_token']}"}

    fake_id = "99999999-9999-9999-9999-999999999999"
    payload = {"nuevo_estado": "CONFIRMADO"}
    response = client.patch(
        f"/api/v1/admin/pedidos/{fake_id}/estado",
        json=payload,
        headers=headers,
    )

    assert response.status_code == 404


def test_change_order_state_wrong_role(setup_endpoint_test_data):
    """Test 403 when user lacks required role"""
    data = setup_endpoint_test_data
    headers = {"Authorization": f"Bearer {data['client_token']}"}

    payload = {"nuevo_estado": "CONFIRMADO"}
    response = client.patch(
        f"/api/v1/admin/pedidos/{data['pedido1'].id}/estado",
        json=payload,
        headers=headers,
    )

    assert response.status_code == 403


def test_get_order_detail(setup_endpoint_test_data):
    """Test GET /admin/pedidos/{id} returns PedidoDetail"""
    data = setup_endpoint_test_data
    headers = {"Authorization": f"Bearer {data['admin_token']}"}

    response = client.get(
        f"/api/v1/admin/pedidos/{data['pedido1'].id}",
        headers=headers,
    )

    assert response.status_code == 200
    result = response.json()
    assert result["id"] == str(data["pedido1"].id)
    assert "items" in result
    assert "historial" in result


def test_get_order_detail_not_found(setup_endpoint_test_data):
    """Test 404 for non-existent order detail"""
    data = setup_endpoint_test_data
    headers = {"Authorization": f"Bearer {data['admin_token']}"}

    fake_id = "99999999-9999-9999-9999-999999999999"
    response = client.get(
        f"/api/v1/admin/pedidos/{fake_id}",
        headers=headers,
    )

    assert response.status_code == 404


def test_get_order_detail_wrong_role(setup_endpoint_test_data):
    """Test 403 for non-admin user accessing order detail"""
    data = setup_endpoint_test_data
    headers = {"Authorization": f"Bearer {data['client_token']}"}

    response = client.get(
        f"/api/v1/admin/pedidos/{data['pedido1'].id}",
        headers=headers,
    )

    assert response.status_code == 403
