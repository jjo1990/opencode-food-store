## Context

Food Store tiene 152 tests existentes con 48% de cobertura total. Los dominios bien cubiertos son Auth (24 tests), Admin Orders (30 tests), Admin Metrics (29 tests), Admin Catalog (28 tests), Admin Config (13 tests), Users Profile (11 tests), y Logging/Middleware (11 tests). Los dominios críticos con cobertura baja o nula son:

| Dominio                    | Cobertura actual | Estado                                                 |
| -------------------------- | ---------------- | ------------------------------------------------------ |
| Productos (CRUD + público) | 19%              | Sin tests de create/update/delete/stock/disponibilidad |
| Pedidos (cliente)          | 18%              | Sin tests de creación atómica, cancelación, ownership  |
| Pagos (webhook MP)         | 13%              | CERO tests de webhook, preference, idempotency, retry  |
| Checkout                   | 12%              | CERO tests de validación                               |
| Categorías                 | ~25%             | Sin tests de CRUD ni listado público                   |
| Ingredientes               | ~25%             | Sin tests de CRUD ni listado público                   |

**Restricciones existentes:**

- Los tests corren con SQLite en memoria (sin PostgreSQL real)
- `conftest.py` provee fixtures `db` (Session), `client` (TestClient), `test_user_data` (dict)
- Rate limiting deshabilitado en tests (`limiter.enabled = False`)
- Las tablas se crean/dropean por test function (scope="function")
- Los tests existentes en `test_admin_orders_endpoints.py` ya crean usuarios con roles y tokens manualmente (patrón a seguir)
- La estructura de tests es flat: `backend/tests/test_*.py`, sin subdirectorios
- Patrón: funciones sueltas (no clases), docstring como descripción, `assert` directo sobre response

**Lo que NO existe:**

- Fixtures pre-autenticados reutilizables (cada test crea usuarios y tokens desde cero)
- Datos seed reutilizables (productos, categorías, estados, direcciones)
- Tests para POST/PUT/DELETE de productos
- Tests para creación de pedidos desde el cliente
- Tests para el FSM completo de 6 estados (solo PENDIENTE→CONFIRMADO testeado)
- Tests para webhook de MercadoPago
- Tests para idempotencia de pagos
- Tests para validación de checkout

## Goals / Non-Goals

**Goals:**

- Crear 4 archivos de test nuevos cubriendo los 4 dominios críticos
- Agregar 10 fixtures a `conftest.py` (clientes pre-autenticados + datos seed)
- Alcanzar ≥60% de cobertura total de statements
- Mantener el 100% de tests existentes pasando (sin regresión)
- Seguir el patrón de tests existentes (funciones sueltas, docstrings, asserts directos)
- Verificar comportamiento correcto del FSM completo de pedidos (6 estados, todas las transiciones)
- Verificar idempotencia en creación de pagos y webhook
- Verificar atomicidad en creación de pedidos (rollback si stock insuficiente)

**Non-Goals:**

- No modificar código de producción (routers, services, repositories, models)
- No crear tests de frontend (solo backend)
- No crear tests de integración con MercadoPago real (se mockea el webhook o se usan datos sintéticos)
- No crear tests de performance o carga
- No crear tests de Categorías e Ingredientes (son bonus opcionales; priorizar los 4 dominios core)
- No modificar la estructura de directorios de tests
- No agregar dependencias de test (pytest, httpx, coverage ya están instalados)

## Decisions

### 1. Fixtures Pre-autenticados — Crear usuarios + roles + tokens en el fixture

**Decision:** Cada fixture de cliente (`admin_client`, `client_client`, `stock_client`, `pedidos_client`) crea un usuario con UUID fijo, asigna el rol correspondiente, genera un JWT con `create_access_token`, y configura el header `Authorization` en el `TestClient`.

```python
@pytest.fixture
def admin_client(client: TestClient, db: Session):
    from app.models import User, UserRole
    from app.core.security import create_access_token

    user = User(
        id=UUID("a0000000-0000-0000-0000-000000000001"),
        email="admin@test.fixture",
        hashed_password="$2b$12$" + "x" * 53,
        full_name="Admin Fixture",
    )
    db.add(user)
    db.commit()

    role = UserRole(user_id=user.id, role="ADMIN")
    db.add(role)
    db.commit()

    token = create_access_token({"sub": str(user.id)})
    client.headers["Authorization"] = f"Bearer {token}"
    return client
```

**Rationale:** El patrón ya existe en `test_admin_orders_endpoints.py:25-80` (fixture `auth_tokens`), pero está duplicado en cada archivo de test y no configura el header automáticamente. Centralizar en `conftest.py` permite reuso. UUIDs fijos evitan colisiones entre fixtures. El token usa `create_access_token` real (sin mockear) para que los tests de RBAC sean genuinos. El `hashed_password` falso con bcrypt-format válido (aunque no matchea ninguna contraseña real) es suficiente porque los tests usan JWT, no login con contraseña.

**Alternativa considerada:** Usar `client.post("/api/v1/auth/login", ...)` para autenticar. Rechazada — agrega latencia innecesaria, requiere conocer la contraseña real, y acopla los fixtures al endpoint de login.

### 2. Datos Seed — Insertar en DB directamente, no vía API

**Decision:** Los fixtures de seed insertan registros directamente en la sesión de BD (`db.add()` + `db.commit()`), no a través de los endpoints de la API.

```python
@pytest.fixture
def seed_estados(db: Session):
    estados = []
    for idx, codigo in enumerate([
        ("PENDIENTE", False), ("CONFIRMADO", False),
        ("EN_PREPARACION", False), ("EN_CAMINO", False),
        ("ENTREGADO", True), ("CANCELADO", True),
    ]):
        estado = EstadoPedido(
            codigo=codigo[0], descripcion=codigo[0],
            orden=idx + 1, es_terminal=codigo[1],
        )
        db.add(estado)
        estados.append(estado)
    db.commit()
    return estados
```

**Rationale:** Insertar vía BD es más rápido y no acopla los fixtures a los endpoints (que podrían cambiar o tener bugs). Los seed fixtures son datos de referencia que los endpoints asumen que existen. Usar la sesión de BD directamente es consistente con cómo `test_admin_orders_endpoints.py` crea estados y usuarios. Retornar la lista de objetos permite a los tests referenciar `seed_estados[0]` (PENDIENTE), etc.

### 3. Archivos de Test — Organización por dominio, no por capa

**Decision:** 4 archivos nuevos en `backend/tests/`:

- `test_productos_crud.py` — CRUD de productos + listado público
- `test_pedidos_client.py` — Creación de pedidos + FSM completo
- `test_pagos.py` — Preferencia MP + webhook + idempotencia
- `test_checkout.py` — Validación de checkout

Cada archivo contiene funciones sueltas (no clases), siguiendo el patrón de `test_auth_register.py` y `test_admin_orders_endpoints.py`.

**Rationale:** La estructura flat existe y funciona. Agrupar por dominio (no por capa) es más intuitivo para encontrar tests: "¿dónde están los tests de pagos?" → `test_pagos.py`. Las clases no se usan en los tests existentes — mantener consistencia. Si un archivo crece mucho (>30 tests), se puede splitear en el futuro (ej: `test_pedidos_fsm.py` separado de `test_pedidos_client.py`).

### 4. FSM Tests — Simular transiciones completas, no solo el endpoint

**Decision:** Los tests del FSM crean un pedido en un estado, luego llaman al endpoint de transición correspondiente, y verifican el nuevo estado + efectos secundarios (stock, historial).

```python
def test_fsm_confirmado_to_en_preparacion(admin_client, seed_estados, seed_producto, db):
    # Crear pedido en CONFIRMADO (simulando post-webhook)
    pedido = crear_pedido_confirmado(db, seed_producto)

    response = admin_client.patch(
        f"/api/v1/admin/pedidos/{pedido.id}/transicionar",
        json={"nuevo_estado": "EN_PREPARACION"}
    )

    assert response.status_code == 200
    db.refresh(pedido)
    assert pedido.estado.codigo == "EN_PREPARACION"
    # Verificar historial
    ...
```

**Rationale:** Las transiciones del FSM ya están implementadas en `pedidos/service.py` (Change 34). Los tests verifican que el endpoint de transición funcione correctamente con todos los guards: validación de estado actual, permisos por rol, estados terminales, restauración de stock en cancelación. No se mockea el service — se usa el endpoint real para tests de integración.

### 5. Webhook de Pago — Simular notificación de MercadoPago

**Decision:** Los tests del webhook envían un payload JSON similar al que enviaría MercadoPago, con un header `x-signature` o similar si el endpoint lo valida. Si la validación de firma requiere un secreto real, se usa el secreto de test configurado en variables de entorno de prueba.

```python
def test_webhook_payment_approved(client, seed_estados, seed_producto, db):
    # Crear pedido PENDIENTE + pago
    pedido = crear_pedido_pendiente(db, seed_producto)

    webhook_payload = {
        "action": "payment.updated",
        "data": {"id": "pay_123"},
        "type": "payment",
    }

    response = client.post(
        "/api/v1/pagos/webhook",
        json=webhook_payload,
        headers={"x-signature": "ts=...,v1=..."}  # Si aplica
    )

    assert response.status_code == 200
    db.refresh(pedido)
    assert pedido.estado.codigo == "CONFIRMADO"
```

**Rationale:** No se mockea el servicio de MercadoPago (no hay llamadas HTTP reales en tests con SQLite). Se envía el payload al endpoint del webhook y se verifica el efecto en la BD. La validación de firma se testea por separado (firma inválida → 401). Si el endpoint no tiene validación de firma todavía, se testea sin ese header y se documenta como deuda técnica.

### 6. Cobertura Meta — 60% con foco en líneas críticas

**Decision:** El target ≥60% se mide con `pytest --cov=app --cov-report=term`. Los 4 dominios nuevos deben sumar aproximadamente 68 tests nuevos (~15 + ~30 + ~15 + ~8), llevando el total a ~220 tests. Estimación de cobertura post-change:

| Dominio                 | Tests nuevos | Cobertura estimada |
| ----------------------- | ------------ | ------------------ |
| Productos               | 15           | 19% → ~70%         |
| Pedidos (cliente + FSM) | 30           | 18% → ~75%         |
| Pagos                   | 15           | 13% → ~70%         |
| Checkout                | 8            | 12% → ~65%         |
| **Total general**       | **+68**      | **48% → ~62-65%**  |

**Rationale:** Cada test nuevo cubre paths que actualmente tienen 0% de cobertura (endpoints nunca llamados en tests). Los servicios de producto, pedido, pago y checkout son el core del negocio — subir su cobertura individual a ≥65% y la total a ≥60% es alcanzable con ~68 tests bien diseñados.

## Architecture

```
backend/tests/
├── conftest.py                  (MOD — +10 fixtures)
│   ├── admin_client             (NEW — TestClient autenticado como ADMIN)
│   ├── client_client            (NEW — TestClient autenticado como CLIENT)
│   ├── stock_client             (NEW — TestClient autenticado como STOCK)
│   ├── pedidos_client           (NEW — TestClient autenticado como PEDIDOS)
│   ├── seed_estados             (NEW — 6 estados de pedido en DB)
│   ├── seed_formas_pago         (NEW — 3 formas de pago en DB)
│   ├── seed_producto            (NEW — 1 producto con stock en DB)
│   ├── seed_categoria           (NEW — 1 categoría en DB)
│   ├── seed_ingrediente         (NEW — 1 ingrediente en DB)
│   └── seed_direccion           (NEW — 1 dirección en DB)
├── test_auth_register.py        (UNCHANGED — 6 tests)
├── test_auth_login.py           (UNCHANGED — 7 tests)
├── test_auth_refresh.py         (UNCHANGED — 6 tests)
├── test_auth_logout.py          (UNCHANGED — 3 tests)
├── test_auth_rbac.py            (UNCHANGED — 5 tests)
├── test_admin_orders_endpoints.py  (UNCHANGED — 13 tests)
├── test_admin_orders_service.py    (UNCHANGED — 8 tests)
├── test_admin_orders_repository.py (UNCHANGED — 9 tests)
├── ... (resto de tests existentes)
├── test_productos_crud.py       (NEW — ~15 tests)
├── test_pedidos_client.py       (NEW — ~30 tests, incluye FSM)
├── test_pagos.py                (NEW — ~15 tests)
└── test_checkout.py             (NEW — ~8 tests)
```

## Risks / Trade-offs

| Risk                                                                                                                                                                           | Mitigation                                                                                                                                                                                                                                          |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Los fixtures pre-autenticados comparten el mismo `client` (headers mutados). Dos tests que usen `admin_client` y `client_client` en el mismo test pueden interferir.           | Cada test function recibe una instancia fresca del fixture (scope="function"). Los headers se configuran en el fixture, no se mutan durante el test. Si un test necesita múltiples clientes, puede usar `client` base + setear headers manualmente. |
| SQLite en memoria no soporta todas las features de PostgreSQL (ej: `JSONB`, `ARRAY`, constraints específicos). Algunos tests pueden pasar en SQLite pero fallar en PostgreSQL. | Los tests existentes ya usan SQLite. Los modelos usan tipos compatibles (SQLModel abstrae las diferencias). Si un test requiere PostgreSQL-specific, se documenta como skip condicional.                                                            |
| El webhook de MP requiere validación de firma con `x-signature`. Si el endpoint no valida firma, los tests no pueden verificar ese path.                                       | Se testea lo que el endpoint implementa. Si no hay validación de firma, se documenta como gap y se agrega un test que verifique el comportamiento actual (sin validación).                                                                          |
| Crear pedidos requiere muchos datos relacionados (usuario, dirección, producto, estado, items). Los helpers pueden volverse complejos.                                         | Se crean funciones helper privadas dentro de cada archivo de test (ej: `_crear_pedido_pendiente()`) que encapsulan la creación. No se exportan como fixtures públicos para mantener `conftest.py` enfocado.                                         |
| 68 tests nuevos pueden ralentizar la suite.                                                                                                                                    | SQLite en memoria es rápido (~0.01s por test). La suite completa debería seguir corriendo en <10 segundos. Si se vuelve lenta, se puede paralelizar con `pytest -n auto`.                                                                           |
| Los tests de FSM pueden ser frágiles si el orden de ejecución importa.                                                                                                         | Cada test del FSM crea su propio pedido desde cero (aislamiento). No se depende de tests anteriores. El fixture `db` crea/dropea tablas por función.                                                                                                |

## Open Questions

1. ¿El endpoint de webhook tiene validación de firma (`x-signature`)? Si no, ¿se debe testear solo el comportamiento actual y documentar el gap?
2. ¿Los endpoints de admin para transiciones de pedido están en `/api/v1/admin/pedidos/{id}/transicionar` o en otra ruta? Verificar en `pedidos/router.py` antes de escribir los tests.
3. ¿El endpoint de checkout está en `/api/v1/checkout/validar` o en otra ruta? Verificar antes de escribir los tests.
4. ¿Deben los tests de Categorías e Ingredientes incluirse en este change si sobra tiempo? (Bonus, no bloqueante para ≥60%)
