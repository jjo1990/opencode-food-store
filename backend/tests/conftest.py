"""
Conftest for pytest configuration
"""

import os

os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["MP_ACCESS_TOKEN"] = "TEST_MP_ACCESS_TOKEN"
os.environ["MP_WEBHOOK_SECRET"] = "TEST_WEBHOOK_SECRET"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.auth.router import limiter

limiter.enabled = False

# Use in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """Create a test database session"""
    from app.models import Base

    # Create tables
    Base.metadata.create_all(bind=engine)

    db_session = TestingSessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()
        # Clean up
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db: Session):
    """Create a test client"""
    from app.core.database import get_db
    from app.main import app

    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def test_user_data():
    """Test user data"""
    return {
        "email": "testuser@example.com",
        "password": "SecurePassword123",
        "full_name": "Test User",
    }


# ─── Pre-authenticated role header fixtures ─────────────────────────────────

def _create_user_with_role(db, email, full_name, role_name):
    """Helper: create a user with a role and return (user, token)."""
    from uuid import UUID as _UUID

    from app.core.security import create_access_token
    from app.models.user import User
    from app.models.user_role import UserRole

    user = User(
        email=email,
        hashed_password="$2b$12$AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
        full_name=full_name,
    )
    db.add(user)
    db.flush()

    user_role = UserRole(user_id=user.id, role=role_name)
    db.add(user_role)
    db.commit()
    db.refresh(user)

    token = create_access_token(user.id, [role_name])
    return user, token


@pytest.fixture
def admin_headers(db):
    """Return auth headers for an ADMIN user."""
    _, token = _create_user_with_role(db, "admin_fixture@test.com", "Admin Fixture", "ADMIN")
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def client_headers(db):
    """Return auth headers for a CLIENT user."""
    _, token = _create_user_with_role(db, "client_fixture@test.com", "Client Fixture", "CLIENT")
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def stock_headers(db):
    """Return auth headers for a STOCK user."""
    _, token = _create_user_with_role(db, "stock_fixture@test.com", "Stock Fixture", "STOCK")
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def pedidos_headers(db):
    """Return auth headers for a PEDIDOS user."""
    _, token = _create_user_with_role(db, "pedidos_fixture@test.com", "Pedidos Fixture", "PEDIDOS")
    return {"Authorization": f"Bearer {token}"}


# ─── Seed data fixtures ──────────────────────────────────────────────────────

@pytest.fixture
def seed_estados(db):
    """Seed the 6 order states (idempotent). Returns list of estado objects."""
    from app.models.estado_pedido import EstadoPedido

    estados_data = [
        ("PENDIENTE", "Pendiente", 1, False),
        ("CONFIRMADO", "Confirmado", 2, False),
        ("EN_PREPARACION", "En Preparación", 3, False),
        ("EN_CAMINO", "En Camino", 4, False),
        ("ENTREGADO", "Entregado", 5, True),
        ("CANCELADO", "Cancelado", 6, True),
    ]
    estados = []
    for codigo, descripcion, orden, es_terminal in estados_data:
        existing = db.query(EstadoPedido).filter(EstadoPedido.codigo == codigo).first()
        if not existing:
            estado = EstadoPedido(codigo=codigo, descripcion=descripcion, orden=orden, es_terminal=es_terminal)
            db.add(estado)
            estados.append(estado)
        else:
            estados.append(existing)
    db.commit()
    return estados


@pytest.fixture
def seed_formas_pago(db):
    """Seed the payment methods (idempotent). Returns list of forma_pago objects."""
    from app.models.forma_pago import FormaPago

    formas_data = [
        ("TARJETA", "Tarjeta", True),
        ("RAPIPAGO", "Rapipago", True),
        ("PAGOFACIL", "Pago Fácil", True),
    ]
    formas = []
    for codigo, descripcion, habilitado_val in formas_data:
        existing = db.query(FormaPago).filter(FormaPago.codigo == codigo).first()
        if not existing:
            forma = FormaPago(codigo=codigo, descripcion=descripcion, habilitado=habilitado_val)
            db.add(forma)
            formas.append(forma)
        else:
            formas.append(existing)
    db.commit()
    return formas


@pytest.fixture
def seed_producto(db):
    """Create a test product with stock and return it."""
    from app.models.producto import Producto

    producto = Producto(
        nombre="Pizza Test",
        descripcion="Pizza de prueba",
        precio_base=1500.00,
        stock_cantidad=50,
        disponible=True,
    )
    db.add(producto)
    db.commit()
    db.refresh(producto)
    return producto


@pytest.fixture
def seed_categoria(db):
    """Create a test category and return it."""
    from app.models.categoria import Categoria

    categoria = Categoria(nombre="Pizzas", slug="pizzas")
    db.add(categoria)
    db.commit()
    db.refresh(categoria)
    return categoria


@pytest.fixture
def seed_ingrediente(db):
    """Create a test ingredient and return it."""
    from app.models.ingrediente import Ingrediente

    ingrediente = Ingrediente(nombre="Queso", es_alergeno=True)
    db.add(ingrediente)
    db.commit()
    db.refresh(ingrediente)
    return ingrediente


@pytest.fixture
def seed_direccion(db, client_headers, client):
    """Create a test address for the CLIENT user. Returns DireccionEntrega object."""
    from uuid import UUID as _UUID

    from app.models.direccion_entrega import DireccionEntrega

    response = client.get("/api/v1/usuarios/me", headers=client_headers)
    assert response.status_code == 200
    user_data = response.json()

    direccion = DireccionEntrega(
        usuario_id=_UUID(user_data["id"]),
        calle="Calle Test 456",
        numero="123",
        ciudad="Ciudad Test",
        codigo_postal="1234",
        es_principal=True,
    )
    db.add(direccion)
    db.commit()
    db.refresh(direccion)
    return direccion
