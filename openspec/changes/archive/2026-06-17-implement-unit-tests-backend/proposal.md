## Why

Food Store tiene **4 dominios core del negocio con cobertura críticamente baja**: productos (19%), pedidos (18%), pagos (13%), checkout (12%). De 152 tests existentes, el 48% de cobertura total viene principalmente de auth (24 tests), admin orders (30 tests), admin metrics (29 tests) y admin catalog (28 tests) — áreas ya bien cubiertas. Pero los módulos que manejan el flujo de negocio principal (catálogo público, creación de pedidos, FSM completo, webhook de pagos, validación de checkout) están casi sin testear.

Sin tests en estos dominios, cualquier refactor o cambio puede romper funcionalidad crítica sin ser detectado. El sistema no tiene forma de verificar que:

- Un producto se crea, actualiza, soft-deletea y filtra correctamente en el catálogo público
- Un pedido se crea atómicamente con validación de stock y snapshots de precio
- El FSM de 6 estados del pedido funciona con todas las transiciones, roles y restauración de stock
- El webhook de MercadoPago procesa pagos con idempotencia, validación de firma y transiciones de estado
- La validación de checkout detecta productos no disponibles, stock insuficiente y cambios de precio

La especificación SDD v5.0 establece ≥60% de cobertura en líneas críticas. Cada test nuevo también sirve como documentación viva del comportamiento esperado.

## What Changes

- **Fixture mejorados (`conftest.py`)**: 10 fixtures nuevos — 4 clientes pre-autenticados por rol (admin_client, client_client, stock_client, pedidos_client) + 6 fixtures de datos seed (estados, formas_pago, producto, categoría, ingrediente, dirección). Los fixtures pre-autenticados eliminan la necesidad de registrar+loguear manualmente en cada test.

- **`test_productos_crud.py`** (~15 tests): CRUD completo de productos. Listado público paginado con filtros (categoría, nombre, precio min/max). Creación con validación de auth (ADMIN/STOCK vs CLIENT/unauth). Validación de campos (precio negativo, stock negativo, nombre vacío). Lectura por slug, update, stock update (admin), toggle disponibilidad, soft delete con verificación de exclusión del listado público.

- **`test_pedidos_client.py`** (~20 tests): Creación atómica de pedidos con snapshot de precio. Validación de stock insuficiente (rollback atómico). Auth y ownership (cliente solo ve sus pedidos, admin ve todos). Listado con filtros y paginación. Detalle con items, historial y total. Cancelación solo en estado PENDIENTE. Historial de auditoría ordenado ASC con actores.

- **FSM Full Flow** (~10 tests, dentro de `test_pedidos_client.py`): Las 6 transiciones de estado: PENDIENTE→CONFIRMADO (bloqueado vía endpoint), PENDIENTE→CANCELADO, CONFIRMADO→EN_PREPARACION, CONFIRMADO→CANCELADO (con restauración de stock), EN_PREPARACION→EN_CAMINO, EN_PREPARACION→CANCELADO (con restauración de stock), EN_CAMINO→ENTREGADO. Estados terminales (ENTREGADO, CANCELADO) rechazan transiciones. Validación de roles por transición.

- **`test_pagos.py`** (~15 tests): Creación de preferencia MercadoPago. Auth, ownership y validación de estado (solo PENDIENTE). Idempotencia con idempotency_key. Webhook con firma válida (pedido→CONFIRMADO, stock decrementado). Webhook con firma inválida (401). Notificación duplicada (idempotente). Pago rechazado (pedido permanece PENDIENTE). Historial de pagos. Reintento solo tras rechazo.

- **`test_checkout.py`** (~8 tests): Validación de items válidos. Producto no encontrado, no disponible, stock insuficiente. Personalizaciones inválidas (ingrediente no existe). Precio cambiado (warning). Carrito vacío (error).

- **Sin modificar código de producción**: Este change es exclusivamente tests. No modifica routers, services, repositories, ni models.

## Capabilities

### New Capabilities

- `backend-test-coverage`: Tests unitarios con pytest para los dominios Productos, Pedidos (cliente), Pagos (webhook MP), y Checkout. Fixtures pre-autenticados por rol (ADMIN, CLIENT, STOCK, PEDIDOS) y datos seed. Cobertura total ≥60%.

### Modified Capabilities

Ninguna. Este change no modifica capacidades existentes.

## Impact

- **Backend**: `tests/conftest.py` (modificado — 10 fixtures nuevos), `tests/test_productos_crud.py` (nuevo), `tests/test_pedidos_client.py` (nuevo), `tests/test_pagos.py` (nuevo), `tests/test_checkout.py` (nuevo)
- **Frontend**: Sin cambios
- **Base de datos**: Sin cambios (usa SQLite en memoria para tests, tablas creadas/dropeadas por fixture `db`)
- **Dependencias**: Changes 9 (`implement-auth-register`), 32 (`implement-payment-webhook`), 34 (`implement-order-fsm-transitions`) — todos ya implementados y mergeados
- **Seguridad**: Sin impacto. Los tests no exponen secretos ni tokens reales.
