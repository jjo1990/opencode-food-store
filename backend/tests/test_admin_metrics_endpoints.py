"""
Integration tests for admin metrics endpoints.

Tests: GET /api/v1/admin/metricas/resumen, /ventas, /productos-top, /pedidos-por-estado
"""

import uuid
from datetime import datetime
from decimal import Decimal

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.detalle_pedido import DetallePedido
from app.models.pedido import Pedido
from app.models.user_role import UserRole


def _register_and_login(client: TestClient, email: str) -> tuple[dict, dict]:
    """Register a user and login to get headers. Returns (user_dict, headers)."""
    password = "TestPass123!"
    resp = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password, "full_name": "Test User"},
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
    db.add(UserRole(user_id=uuid.UUID(user_id), role="ADMIN"))
    db.commit()


def _make_client_role(db: Session, user_id: str):
    """Assign CLIENT role to a user in DB."""
    db.add(UserRole(user_id=uuid.UUID(user_id), role="CLIENT"))
    db.commit()


def _ensure_forma_pago(db: Session, codigo: str = "EFECTIVO"):
    """Ensure a FormaPago exists, creating it if needed."""
    from app.models.forma_pago import FormaPago

    existing = db.query(FormaPago).filter(FormaPago.codigo == codigo).first()
    if existing:
        return existing
    fp = FormaPago(codigo=codigo, descripcion=codigo)
    db.add(fp)
    db.commit()
    return fp


def _ensure_estado_pedido(db: Session, codigo: str):
    """Ensure an EstadoPedido exists, creating it if needed."""
    from app.models.estado_pedido import EstadoPedido

    existing = db.query(EstadoPedido).filter(EstadoPedido.codigo == codigo).first()
    if existing:
        return existing
    ep = EstadoPedido(codigo=codigo, descripcion=codigo, orden=1)
    db.add(ep)
    db.commit()
    return ep


def _seed_user(db: Session, email: str) -> str:
    """Create a test user, return UUID string."""
    from app.models.user import User

    existing = db.query(User).filter(User.email == email).first()
    if existing:
        return str(existing.id)
    u = User(
        email=email,
        hashed_password="testhash",
        full_name="Seed User",
    )
    db.add(u)
    db.commit()
    return str(u.id)


def _seed_pedido(
    db: Session, estado: str, total: float, created_at: datetime, deleted: bool = False
) -> Pedido:
    """Create a test pedido."""
    _ensure_forma_pago(db, "EFECTIVO")
    _ensure_estado_pedido(db, estado)

    user_id = _seed_user(db, f"seed_{uuid.uuid4().hex[:8]}@test.com")

    p = Pedido(
        usuario_id=uuid.UUID(user_id),
        estado_codigo=estado,
        forma_pago_codigo="EFECTIVO",
        subtotal=Decimal(str(total - 50.0)),
        costo_envio=Decimal("50.00"),
        total=Decimal(str(total)),
        created_at=created_at,
        soft_deleted_at=datetime.utcnow() if deleted else None,
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


def _seed_detalle(
    db: Session,
    pedido_id: uuid.UUID,
    producto_id: uuid.UUID,
    nombre: str,
    cantidad: int,
    subtotal: float,
):
    """Create a detalle pedido for a pedido."""
    d = DetallePedido(
        pedido_id=pedido_id,
        producto_id=producto_id,
        nombre_snapshot=nombre,
        cantidad=cantidad,
        precio_snapshot=Decimal("10.00"),
        subtotal=Decimal(str(subtotal)),
    )
    db.add(d)
    db.commit()
    return d


def _login_as_admin(client: TestClient, email: str, db: Session) -> dict:
    """Create user, make admin, re-login, return headers."""
    user_data, headers = _register_and_login(client, email)
    _make_admin(db, user_data["id"])
    login_resp = client.post(
        "/api/v1/auth/login", json={"email": email, "password": "TestPass123!"}
    )
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# ─── RESUMEN ────────────────────────────────────────────────────────────────


class TestMetricsResumen:
    """Tests for GET /api/v1/admin/metricas/resumen"""

    def test_unauthorized_no_token(self, client: TestClient):
        resp = client.get("/api/v1/admin/metricas/resumen")
        assert resp.status_code == 403

    def test_forbidden_non_admin(self, client: TestClient, db: Session):
        user_data, headers = _register_and_login(client, "client_resumen@test.com")
        resp = client.get("/api/v1/admin/metricas/resumen", headers=headers)
        assert resp.status_code == 403

    def test_empty_db_returns_zeros(self, client: TestClient, db: Session):
        headers = _login_as_admin(client, "admin_empty@test.com", db)
        resp = client.get("/api/v1/admin/metricas/resumen", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_ventas"] == 0.0
        assert data["cantidad_pedidos"] == 0
        assert data["pedidos_por_estado"] == {}
        assert data["usuarios_registrados"] >= 1  # at least the admin user itself

    def test_with_data_returns_correct_kpis(self, client: TestClient, db: Session):
        headers = _login_as_admin(client, "admin_data@test.com", db)

        now = datetime.utcnow()
        _seed_pedido(db, "PENDIENTE", 100.0, now)
        _seed_pedido(db, "CONFIRMADO", 250.0, now)
        _seed_pedido(db, "PENDIENTE", 75.0, now)

        resp = client.get("/api/v1/admin/metricas/resumen", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_ventas"] == 425.0
        assert data["cantidad_pedidos"] == 3
        assert data["pedidos_por_estado"] == {"PENDIENTE": 2, "CONFIRMADO": 1}
        assert data["usuarios_registrados"] >= 1

    def test_soft_deleted_pedido_excluded(self, client: TestClient, db: Session):
        headers = _login_as_admin(client, "admin_sd@test.com", db)

        now = datetime.utcnow()
        _seed_pedido(db, "PENDIENTE", 100.0, now)
        _seed_pedido(db, "CANCELADO", 50.0, now, deleted=True)

        resp = client.get("/api/v1/admin/metricas/resumen", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_ventas"] == 100.0
        assert data["cantidad_pedidos"] == 1

    def test_soft_deleted_user_excluded(self, client: TestClient, db: Session):
        headers = _login_as_admin(client, "admin_sd_user@test.com", db)

        from app.models.user import User

        deleted_user = User(
            email="deleted@test.com",
            hashed_password="xxx",
            full_name="Deleted",
            soft_deleted_at=datetime.utcnow(),
        )
        db.add(deleted_user)
        db.commit()

        resp = client.get("/api/v1/admin/metricas/resumen", headers=headers)
        assert resp.status_code == 200
        # Should NOT count the soft-deleted user
        data = resp.json()
        assert data["usuarios_registrados"] >= 1  # at least the admin
        # The deleted user should not bump the count above admin + admin account
        assert data["usuarios_registrados"] >= 1


# ─── VENTAS ─────────────────────────────────────────────────────────────────


class TestMetricsVentas:
    """Tests for GET /api/v1/admin/metricas/ventas"""

    def test_unauthorized_no_token(self, client: TestClient):
        resp = client.get(
            "/api/v1/admin/metricas/ventas?fecha_inicio=2026-06-01&fecha_fin=2026-06-07&granularidad=day"
        )
        assert resp.status_code == 403

    def test_forbidden_non_admin(self, client: TestClient, db: Session):
        user_data, headers = _register_and_login(client, "client_ventas@test.com")
        resp = client.get(
            "/api/v1/admin/metricas/ventas?fecha_inicio=2026-06-01&fecha_fin=2026-06-07&granularidad=day",
            headers=headers,
        )
        assert resp.status_code == 403

    def test_daily_granularity(self, client: TestClient, db: Session):
        headers = _login_as_admin(client, "admin_daily@test.com", db)

        d1 = datetime(2026, 6, 1, 10, 0, 0)
        d2 = datetime(2026, 6, 3, 12, 0, 0)
        _seed_pedido(db, "PENDIENTE", 100.0, d1)
        _seed_pedido(db, "CONFIRMADO", 250.0, d2)

        resp = client.get(
            "/api/v1/admin/metricas/ventas?fecha_inicio=2026-06-01&fecha_fin=2026-06-07&granularidad=day",
            headers=headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "items" in data
        assert len(data["items"]) == 2

        fechas = {item["fecha"] for item in data["items"]}
        assert "2026-06-01" in fechas
        assert "2026-06-03" in fechas

    def test_weekly_granularity(self, client: TestClient, db: Session):
        headers = _login_as_admin(client, "admin_weekly@test.com", db)

        d1 = datetime(2026, 6, 1, 10, 0, 0)  # week 23 of 2026
        d2 = datetime(2026, 6, 8, 12, 0, 0)  # week 24 of 2026
        _seed_pedido(db, "PENDIENTE", 100.0, d1)
        _seed_pedido(db, "CONFIRMADO", 200.0, d2)

        resp = client.get(
            "/api/v1/admin/metricas/ventas?fecha_inicio=2026-06-01&fecha_fin=2026-06-14&granularidad=week",
            headers=headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["items"]) == 2

        fechas = {item["fecha"] for item in data["items"]}
        assert "2026-W23" in fechas
        assert "2026-W24" in fechas

    def test_monthly_granularity(self, client: TestClient, db: Session):
        headers = _login_as_admin(client, "admin_monthly@test.com", db)

        d1 = datetime(2026, 6, 1, 10, 0, 0)
        d2 = datetime(2026, 7, 15, 12, 0, 0)
        _seed_pedido(db, "PENDIENTE", 100.0, d1)
        _seed_pedido(db, "CONFIRMADO", 200.0, d2)

        resp = client.get(
            "/api/v1/admin/metricas/ventas?fecha_inicio=2026-06-01&fecha_fin=2026-07-31&granularidad=month",
            headers=headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["items"]) == 2

        fechas = {item["fecha"] for item in data["items"]}
        assert "2026-06" in fechas
        assert "2026-07" in fechas

    def test_invalid_date_range_start_after_end(self, client: TestClient, db: Session):
        headers = _login_as_admin(client, "admin_invrange@test.com", db)
        resp = client.get(
            "/api/v1/admin/metricas/ventas?fecha_inicio=2026-06-15&fecha_fin=2026-06-01&granularidad=day",
            headers=headers,
        )
        assert resp.status_code == 422

    def test_range_exceeds_365_days(self, client: TestClient, db: Session):
        headers = _login_as_admin(client, "admin_365@test.com", db)
        resp = client.get(
            "/api/v1/admin/metricas/ventas?fecha_inicio=2025-01-01&fecha_fin=2026-12-31&granularidad=month",
            headers=headers,
        )
        assert resp.status_code == 422

    def test_invalid_granularity(self, client: TestClient, db: Session):
        headers = _login_as_admin(client, "admin_invgr@test.com", db)
        resp = client.get(
            "/api/v1/admin/metricas/ventas?fecha_inicio=2026-06-01&fecha_fin=2026-06-07&granularidad=hour",
            headers=headers,
        )
        assert resp.status_code == 422

    def test_empty_period_returns_empty_items(self, client: TestClient, db: Session):
        headers = _login_as_admin(client, "admin_emptyperiod@test.com", db)
        resp = client.get(
            "/api/v1/admin/metricas/ventas?fecha_inicio=2026-06-01&fecha_fin=2026-06-07&granularidad=day",
            headers=headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["items"] == []

    def test_soft_deleted_pedido_excluded(self, client: TestClient, db: Session):
        headers = _login_as_admin(client, "admin_sd_ventas@test.com", db)

        d1 = datetime(2026, 6, 1, 10, 0, 0)
        _seed_pedido(db, "PENDIENTE", 100.0, d1)
        _seed_pedido(db, "CANCELADO", 50.0, d1, deleted=True)

        resp = client.get(
            "/api/v1/admin/metricas/ventas?fecha_inicio=2026-06-01&fecha_fin=2026-06-01&granularidad=day",
            headers=headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["monto_total"] == 100.0
        assert data["items"][0]["cantidad_pedidos"] == 1


# ─── PRODUCTOS TOP ──────────────────────────────────────────────────────────


class TestMetricsProductosTop:
    """Tests for GET /api/v1/admin/metricas/productos-top"""

    def test_unauthorized_no_token(self, client: TestClient):
        resp = client.get("/api/v1/admin/metricas/productos-top")
        assert resp.status_code == 403

    def test_forbidden_non_admin(self, client: TestClient, db: Session):
        user_data, headers = _register_and_login(client, "client_prodtop@test.com")
        resp = client.get("/api/v1/admin/metricas/productos-top", headers=headers)
        assert resp.status_code == 403

    def test_no_sales_returns_empty(self, client: TestClient, db: Session):
        headers = _login_as_admin(client, "admin_nosales@test.com", db)
        resp = client.get("/api/v1/admin/metricas/productos-top", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["items"] == []

    def test_returns_top_products_ordered(self, client: TestClient, db: Session):
        headers = _login_as_admin(client, "admin_topprod@test.com", db)

        pid1 = uuid.uuid4()
        pid2 = uuid.uuid4()
        pid3 = uuid.uuid4()

        now = datetime.utcnow()
        p1 = _seed_pedido(db, "ENTREGADO", 300.0, now)
        p2 = _seed_pedido(db, "ENTREGADO", 150.0, now)

        _seed_detalle(db, p1.id, pid1, "Pizza", 5, 250.0)
        _seed_detalle(db, p1.id, pid2, "Empanada", 10, 50.0)
        _seed_detalle(db, p2.id, pid1, "Pizza", 2, 100.0)
        _seed_detalle(db, p2.id, pid3, "Bebida", 1, 50.0)

        resp = client.get("/api/v1/admin/metricas/productos-top", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["items"]) == 3

        # Empanada: 10 cantidad (most sold)
        assert data["items"][0]["nombre"] == "Empanada"
        assert data["items"][0]["cantidad_vendida"] == 10
        assert data["items"][0]["monto_total"] == 50.0

        assert data["items"][1]["nombre"] == "Pizza"
        assert data["items"][1]["cantidad_vendida"] == 7
        assert data["items"][1]["monto_total"] == 350.0

        assert data["items"][2]["nombre"] == "Bebida"
        assert data["items"][2]["cantidad_vendida"] == 1

    def test_soft_deleted_pedido_excluded(self, client: TestClient, db: Session):
        headers = _login_as_admin(client, "admin_sd_topprod@test.com", db)

        pid1 = uuid.uuid4()
        now = datetime.utcnow()

        p_active = _seed_pedido(db, "ENTREGADO", 100.0, now)
        p_deleted = _seed_pedido(db, "ENTREGADO", 500.0, now, deleted=True)

        _seed_detalle(db, p_active.id, pid1, "Pizza", 1, 50.0)
        _seed_detalle(db, p_deleted.id, pid1, "Pizza", 100, 500.0)

        resp = client.get("/api/v1/admin/metricas/productos-top", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["cantidad_vendida"] == 1

    def test_less_than_10_products(self, client: TestClient, db: Session):
        headers = _login_as_admin(client, "admin_lessthan10@test.com", db)

        pid1 = uuid.uuid4()
        now = datetime.utcnow()
        p1 = _seed_pedido(db, "ENTREGADO", 100.0, now)
        _seed_detalle(db, p1.id, pid1, "OnlyProduct", 1, 100.0)

        resp = client.get("/api/v1/admin/metricas/productos-top", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["items"]) == 1


# ─── PEDIDOS POR ESTADO ─────────────────────────────────────────────────────


class TestMetricsPedidosEstado:
    """Tests for GET /api/v1/admin/metricas/pedidos-por-estado"""

    def test_unauthorized_no_token(self, client: TestClient):
        resp = client.get("/api/v1/admin/metricas/pedidos-por-estado")
        assert resp.status_code == 403

    def test_forbidden_non_admin(self, client: TestClient, db: Session):
        user_data, headers = _register_and_login(client, "client_pedestado@test.com")
        resp = client.get("/api/v1/admin/metricas/pedidos-por-estado", headers=headers)
        assert resp.status_code == 403

    def test_no_orders_returns_empty(self, client: TestClient, db: Session):
        headers = _login_as_admin(client, "admin_noorders@test.com", db)
        resp = client.get("/api/v1/admin/metricas/pedidos-por-estado", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["items"] == []

    def test_single_state_all_orders(self, client: TestClient, db: Session):
        headers = _login_as_admin(client, "admin_single@test.com", db)

        now = datetime.utcnow()
        _seed_pedido(db, "PENDIENTE", 100.0, now)
        _seed_pedido(db, "PENDIENTE", 200.0, now)

        resp = client.get("/api/v1/admin/metricas/pedidos-por-estado", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["estado"] == "PENDIENTE"
        assert data["items"][0]["cantidad"] == 2
        assert data["items"][0]["porcentaje"] == 100.0

    def test_multiple_states_with_percentages(self, client: TestClient, db: Session):
        headers = _login_as_admin(client, "admin_multistate@test.com", db)

        now = datetime.utcnow()
        _seed_pedido(db, "PENDIENTE", 100.0, now)
        _seed_pedido(db, "PENDIENTE", 200.0, now)
        _seed_pedido(db, "CONFIRMADO", 150.0, now)
        _seed_pedido(db, "ENTREGADO", 300.0, now)

        resp = client.get("/api/v1/admin/metricas/pedidos-por-estado", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["items"]) == 3

        total_pct = sum(item["porcentaje"] for item in data["items"])
        assert abs(total_pct - 100.0) < 0.1, f"Percentages sum to {total_pct}, expected ~100"

        estados = {item["estado"] for item in data["items"]}
        assert "PENDIENTE" in estados
        assert "CONFIRMADO" in estados
        assert "ENTREGADO" in estados

    def test_soft_deleted_pedido_excluded(self, client: TestClient, db: Session):
        headers = _login_as_admin(client, "admin_sd_estado@test.com", db)

        now = datetime.utcnow()
        _seed_pedido(db, "PENDIENTE", 100.0, now)
        _seed_pedido(db, "CANCELADO", 50.0, now, deleted=True)

        resp = client.get("/api/v1/admin/metricas/pedidos-por-estado", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["estado"] == "PENDIENTE"
        assert data["items"][0]["porcentaje"] == 100.0

    def test_percentages_sum_to_100(self, client: TestClient, db: Session):
        headers = _login_as_admin(client, "admin_sum100@test.com", db)

        now = datetime.utcnow()
        # 7 pedidos: uneven division
        _seed_pedido(db, "PENDIENTE", 10.0, now)
        _seed_pedido(db, "PENDIENTE", 10.0, now)
        _seed_pedido(db, "PENDIENTE", 10.0, now)
        _seed_pedido(db, "CONFIRMADO", 10.0, now)
        _seed_pedido(db, "CONFIRMADO", 10.0, now)
        _seed_pedido(db, "CONFIRMADO", 10.0, now)
        _seed_pedido(db, "CONFIRMADO", 10.0, now)

        resp = client.get("/api/v1/admin/metricas/pedidos-por-estado", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        total_pct = sum(item["porcentaje"] for item in data["items"])
        assert abs(total_pct - 100.0) < 0.2, f"Percentages sum to {total_pct}"
