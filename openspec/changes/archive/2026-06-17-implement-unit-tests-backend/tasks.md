# Tasks: implement-unit-tests-backend

## 1. Fixture Improvements (conftest.py)

- [ ] 1.1 Add `admin_client` fixture — creates ADMIN user with UUID, assigns role, generates JWT, sets Authorization header on TestClient
- [ ] 1.2 Add `client_client` fixture — creates CLIENT user with UUID, assigns role, generates JWT, sets Authorization header on TestClient
- [ ] 1.3 Add `stock_client` fixture — creates STOCK user with UUID, assigns role, generates JWT, sets Authorization header on TestClient
- [ ] 1.4 Add `pedidos_client` fixture — creates PEDIDOS user with UUID, assigns role, generates JWT, sets Authorization header on TestClient
- [ ] 1.5 Add `seed_estados` fixture — inserts 6 order states (PENDIENTE, CONFIRMADO, EN_PREPARACION, EN_CAMINO, ENTREGADO, CANCELADO) with correct `es_terminal` flags
- [ ] 1.6 Add `seed_formas_pago` fixture — inserts 3 payment methods (tarjeta, Rapipago, Pago Fácil)
- [ ] 1.7 Add `seed_producto` fixture — creates a test product with `stock > 0`, `precio > 0`, `disponible=True`, associated to a category
- [ ] 1.8 Add `seed_categoria` fixture — creates a test category with `nombre` and `slug`
- [ ] 1.9 Add `seed_ingrediente` fixture — creates a test ingredient with `nombre` and optional allergen info
- [ ] 1.10 Add `seed_direccion` fixture — creates a test address associated to a test user

## 2. Productos CRUD Tests (test_productos_crud.py)

- [ ] 2.1 Test: `GET /api/v1/productos` — returns paginated results, includes only available products, hides stock field
- [ ] 2.2 Test: `GET /api/v1/productos` — filter by `categoria_id`, search by `nombre`, filter by `precio_min` and `precio_max`
- [ ] 2.3 Test: `POST /api/v1/productos` (ADMIN) — creates product, returns 201 with all fields
- [ ] 2.4 Test: `POST /api/v1/productos` (STOCK) — creates product, returns 201
- [ ] 2.5 Test: `POST /api/v1/productos` (CLIENT) — returns 403
- [ ] 2.6 Test: `POST /api/v1/productos` (unauthenticated) — returns 403
- [ ] 2.7 Test: `POST /api/v1/productos` validation — precio negativo (422), stock negativo (422), nombre vacío (422)
- [ ] 2.8 Test: `GET /api/v1/productos/{slug}` — returns 200 with all product fields
- [ ] 2.9 Test: `GET /api/v1/productos/{slug}` — non-existent slug returns 404
- [ ] 2.10 Test: `PUT /api/v1/productos/{id}` (ADMIN) — updates product, returns 200
- [ ] 2.11 Test: `PUT /api/v1/productos/{id}` (CLIENT) — returns 403
- [ ] 2.12 Test: `PATCH /api/v1/admin/productos/{id}/stock` (ADMIN) — updates stock, returns 200 with new stock value
- [ ] 2.13 Test: Toggle `disponible` from `true` to `false` — product disappears from public listing
- [ ] 2.14 Test: Toggle `disponible` from `false` to `true` — product reappears in public listing
- [ ] 2.15 Test: `DELETE /api/v1/productos/{id}` (ADMIN) — soft delete, returns 204, product not in public listing
- [ ] 2.16 Test: `DELETE /api/v1/productos/{id}` — already deleted product returns 404

## 3. Pedidos Client Tests (test_pedidos_client.py)

- [ ] 3.1 Test: `POST /api/v1/pedidos` (CLIENT) — atomic creation with items, returns 201, estado PENDIENTE, snapshot verification
- [ ] 3.2 Test: `POST /api/v1/pedidos` — stock insuficiente returns 400, no order created (atomic rollback)
- [ ] 3.3 Test: `POST /api/v1/pedidos` — producto no disponible returns 400
- [ ] 3.4 Test: `POST /api/v1/pedidos` — dirección no pertenece al usuario returns 403
- [ ] 3.5 Test: `POST /api/v1/pedidos` (unauthenticated) — returns 403
- [ ] 3.6 Test: `GET /api/v1/pedidos` (CLIENT) — only sees own orders
- [ ] 3.7 Test: `GET /api/v1/pedidos` (ADMIN) — sees ALL orders
- [ ] 3.8 Test: `GET /api/v1/pedidos` — filter by estado
- [ ] 3.9 Test: `GET /api/v1/pedidos` — pagination works
- [ ] 3.10 Test: `GET /api/v1/pedidos/{id}` (CLIENT, own) — returns 200 with items, historial, total
- [ ] 3.11 Test: `GET /api/v1/pedidos/{id}` (CLIENT, other user) — returns 404 (ownership enforced)
- [ ] 3.12 Test: `GET /api/v1/pedidos/{id}` (ADMIN, any order) — returns 200
- [ ] 3.13 Test: `PATCH /api/v1/pedidos/{id}/cancelar` (CLIENT, own, PENDIENTE) — returns 200, estado CANCELADO
- [ ] 3.14 Test: `PATCH /api/v1/pedidos/{id}/cancelar` — already CONFIRMADO returns 422
- [ ] 3.15 Test: `GET /api/v1/pedidos/{id}/historial` — returns 200, ordered ASC, includes actor names

## 4. FSM Full Flow Tests (test_pedidos_client.py)

- [ ] 4.1 Test: PENDIENTE → CANCELADO (CLIENT cancels own order)
- [ ] 4.2 Test: PENDIENTE → CONFIRMADO blocked via endpoint (returns 422, only webhook can confirm)
- [ ] 4.3 Test: CONFIRMADO → EN_PREPARACION (ADMIN transitions)
- [ ] 4.4 Test: CONFIRMADO → CANCELADO (ADMIN) — verify stock restoration (stock increases back)
- [ ] 4.5 Test: EN_PREPARACION → EN_CAMINO (ADMIN transitions)
- [ ] 4.6 Test: EN_PREPARACION → CANCELADO (ADMIN) — verify stock restoration
- [ ] 4.7 Test: EN_CAMINO → ENTREGADO (ADMIN transitions)
- [ ] 4.8 Test: ENTREGADO → any transition returns 422 (terminal state protection)
- [ ] 4.9 Test: CANCELADO → any transition returns 422 (terminal state protection)
- [ ] 4.10 Test: Role validation per transition — CLIENT cannot transition (except cancel own PENDIENTE), STOCK cannot transition

## 5. Pagos Tests (test_pagos.py)

- [ ] 5.1 Test: `POST /api/v1/pagos/crear` (CLIENT, PENDIENTE order) — returns 201 with MercadoPago preference data
- [ ] 5.2 Test: `POST /api/v1/pagos/crear` — order not found returns 404
- [ ] 5.3 Test: `POST /api/v1/pagos/crear` — order not in PENDIENTE returns 400
- [ ] 5.4 Test: `POST /api/v1/pagos/crear` (unauthenticated) — returns 403
- [ ] 5.5 Test: `POST /api/v1/pagos/crear` — order belongs to another user returns 403
- [ ] 5.6 Test: `POST /api/v1/pagos/crear` — idempotency (same idempotency_key twice returns 200, same payment)
- [ ] 5.7 Test: `POST /api/v1/pagos/webhook` — approved payment with valid signature, order → CONFIRMADO, stock decremented
- [ ] 5.8 Test: `POST /api/v1/pagos/webhook` — invalid/missing signature returns 401
- [ ] 5.9 Test: `POST /api/v1/pagos/webhook` — duplicate notification is idempotent (200, no state change, no duplicate history)
- [ ] 5.10 Test: `POST /api/v1/pagos/webhook` — rejected payment, order stays PENDIENTE
- [ ] 5.11 Test: `GET /api/v1/pagos/{pedido_id}` (CLIENT, own) — returns 200 with payment attempts
- [ ] 5.12 Test: `GET /api/v1/pagos/{pedido_id}` (CLIENT, other user) — returns 403
- [ ] 5.13 Test: `POST /api/v1/pagos/reintentar` (CLIENT, last payment rejected) — returns 201
- [ ] 5.14 Test: `POST /api/v1/pagos/reintentar` (CLIENT, last payment approved) — returns 400

## 6. Checkout Tests (test_checkout.py)

- [ ] 6.1 Test: `POST /api/v1/checkout/validar` — valid items return 200 with successful validation
- [ ] 6.2 Test: `POST /api/v1/checkout/validar` — producto no encontrado returns error in validation result
- [ ] 6.3 Test: `POST /api/v1/checkout/validar` — producto no disponible returns error in validation result
- [ ] 6.4 Test: `POST /api/v1/checkout/validar` — stock insuficiente returns error in validation result
- [ ] 6.5 Test: `POST /api/v1/checkout/validar` — personalizaciones inválidas (ingrediente no existe) returns error
- [ ] 6.6 Test: `POST /api/v1/checkout/validar` — precio cambiado returns warning in validation result
- [ ] 6.7 Test: `POST /api/v1/checkout/validar` — carrito vacío returns error in validation result

## 7. Verification

- [ ] 7.1 Run `cd backend && python -m pytest` — all new + existing tests pass (152 + ~68 = ~220 total)
- [ ] 7.2 Run `cd backend && python -m pytest --cov=app --cov-report=term` — verify coverage ≥60%
- [ ] 7.3 Verify no regression: all 152 existing tests still pass without modification
- [ ] 7.4 Verify test isolation — tests pass with `pytest --random-order` (no order dependency)
