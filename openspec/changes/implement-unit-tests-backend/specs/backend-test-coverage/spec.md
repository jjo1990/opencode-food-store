# backend-test-coverage Specification

## Purpose

Especifica los tests unitarios de backend para Food Store que deben existir para alcanzar ≥60% de cobertura de código. Cubre los dominios Productos (CRUD y listado público), Pedidos (creación atómica, FSM completo de 6 estados, cancelación con restauración de stock), Pagos (preferencia MercadoPago, webhook con idempotencia, historial), Checkout (validación de items), y mejoras a los fixtures de prueba (clientes pre-autenticados por rol, datos seed).

## ADDED Requirements

### Requirement: Product CRUD operations MUST be fully tested

El sistema DEBE tener tests que verifiquen todas las operaciones CRUD de productos, incluyendo listado público, creación, lectura, actualización, actualización de stock, toggle de disponibilidad, soft delete, y validación de campos.

#### Scenario: Public product listing returns paginated results with filters

- **WHEN** se hace un request `GET /api/v1/productos` sin autenticación
- **THEN** la respuesta es `200 OK` con una lista paginada de productos
- **AND** solo se incluyen productos disponibles (no eliminados ni con `disponible=false`)
- **AND** el campo `stock` NO está expuesto en la respuesta pública
- **AND** se puede filtrar por `categoria_id`, buscar por `nombre`, y filtrar por `precio_min` y `precio_max`

#### Scenario: Product creation requires ADMIN or STOCK role

- **WHEN** un ADMIN o STOCK hace `POST /api/v1/productos` con datos válidos
- **THEN** la respuesta es `201 Created` con los campos del producto creado
- **WHEN** un CLIENT hace `POST /api/v1/productos`
- **THEN** la respuesta es `403 Forbidden`
- **WHEN** un usuario no autenticado hace `POST /api/v1/productos`
- **THEN** la respuesta es `403 Forbidden`

#### Scenario: Product creation validates input fields

- **WHEN** se envía `POST /api/v1/productos` con `precio` negativo
- **THEN** la respuesta es `422 Unprocessable Entity`
- **WHEN** se envía con `stock` negativo
- **THEN** la respuesta es `422 Unprocessable Entity`
- **WHEN** se envía con `nombre` vacío
- **THEN** la respuesta es `422 Unprocessable Entity`

#### Scenario: Product read by slug returns full product data

- **WHEN** se hace `GET /api/v1/productos/{slug}` con un slug válido
- **THEN** la respuesta es `200 OK` con todos los campos del producto
- **WHEN** se hace `GET /api/v1/productos/{slug}` con un slug inexistente
- **THEN** la respuesta es `404 Not Found`

#### Scenario: Product update requires ADMIN role

- **WHEN** un ADMIN hace `PUT /api/v1/productos/{id}` con datos actualizados
- **THEN** la respuesta es `200 OK` con los campos actualizados
- **WHEN** un CLIENT hace `PUT /api/v1/productos/{id}`
- **THEN** la respuesta es `403 Forbidden`

#### Scenario: Stock update endpoint works for admin

- **WHEN** un ADMIN hace `PATCH /api/v1/admin/productos/{id}/stock` con `{"stock": 50}`
- **THEN** la respuesta es `200 OK` y el stock del producto es 50

#### Scenario: Availability toggle changes product visibility

- **WHEN** se cambia `disponible` de `true` a `false` mediante el endpoint correspondiente
- **THEN** el producto ya no aparece en el listado público
- **WHEN** se vuelve a activar
- **THEN** el producto reaparece en el listado público

#### Scenario: Soft delete removes product from public listing

- **WHEN** un ADMIN hace `DELETE /api/v1/productos/{id}`
- **THEN** la respuesta es `204 No Content`
- **AND** el producto no aparece en `GET /api/v1/productos`
- **AND** `GET /api/v1/productos/{slug}` del producto eliminado retorna `404 Not Found`
- **WHEN** se intenta eliminar un producto ya eliminado
- **THEN** la respuesta es `404 Not Found`

---

### Requirement: Client order operations MUST be fully tested

El sistema DEBE tener tests que verifiquen la creación atómica de pedidos con validación de stock, listado de pedidos propios, detalle con ownership, cancelación en estado PENDIENTE, y auditoría de historial.

#### Scenario: Atomic order creation with stock validation and price snapshot

- **WHEN** un CLIENT autenticado hace `POST /api/v1/pedidos` con items válidos
- **THEN** la respuesta es `201 Created` con el pedido creado, estado `PENDIENTE`, items incluidos, y total calculado
- **AND** los precios e historial de estados se guardan como snapshot al momento de creación
- **WHEN** se crea un pedido con stock insuficiente para algún item
- **THEN** la respuesta es `400 Bad Request`
- **AND** NO se crea el pedido (rollback atómico — cero filas en `pedidos` y `detalles_pedido`)
- **WHEN** se incluye un producto no disponible
- **THEN** la respuesta es `400 Bad Request`

#### Scenario: Order creation validates auth and ownership

- **WHEN** un usuario no autenticado hace `POST /api/v1/pedidos`
- **THEN** la respuesta es `403 Forbidden`
- **WHEN** un CLIENT intenta usar una dirección que no le pertenece
- **THEN** la respuesta es `403 Forbidden`

#### Scenario: Client only sees their own orders

- **WHEN** un CLIENT hace `GET /api/v1/pedidos`
- **THEN** la respuesta es `200 OK` y solo contiene pedidos de ese usuario
- **WHEN** un ADMIN hace `GET /api/v1/pedidos`
- **THEN** la respuesta es `200 OK` y contiene TODOS los pedidos
- **AND** se puede filtrar por `estado` y paginar los resultados

#### Scenario: Order detail enforces ownership

- **WHEN** un CLIENT hace `GET /api/v1/pedidos/{id}` de su propio pedido
- **THEN** la respuesta es `200 OK` con items, historial, y total
- **WHEN** un CLIENT hace `GET /api/v1/pedidos/{id}` de un pedido de otro usuario
- **THEN** la respuesta es `404 Not Found` (no se revela la existencia)
- **WHEN** un ADMIN hace `GET /api/v1/pedidos/{id}` de cualquier pedido
- **THEN** la respuesta es `200 OK`

#### Scenario: Client cancels their own PENDIENTE order

- **WHEN** un CLIENT hace `PATCH /api/v1/pedidos/{id}/cancelar` en su pedido en estado `PENDIENTE`
- **THEN** la respuesta es `200 OK` y el pedido pasa a estado `CANCELADO`
- **WHEN** un CLIENT intenta cancelar un pedido en estado `CONFIRMADO`
- **THEN** la respuesta es `422 Unprocessable Entity` (solo PENDIENTE puede ser cancelado por el cliente)

#### Scenario: Order history shows audit trail with actors

- **WHEN** se hace `GET /api/v1/pedidos/{id}/historial`
- **THEN** la respuesta es `200 OK` con una lista de cambios de estado ordenada ASC por timestamp
- **AND** cada entrada incluye el estado anterior, estado nuevo, y nombre del actor que realizó el cambio

---

### Requirement: Order FSM full flow MUST be tested with all 6 states

El sistema DEBE tener tests que verifiquen todas las transiciones válidas e inválidas del FSM de pedidos de 6 estados, la protección de estados terminales, la validación de roles por transición, y la restauración de stock al cancelar.

#### Scenario: All valid transitions work correctly

- **WHEN** un pedido en `PENDIENTE` se cancela vía endpoint (CLIENT o ADMIN)
- **THEN** el pedido pasa a `CANCELADO`
- **WHEN** se intenta transicionar de `PENDIENTE` a `CONFIRMADO` vía endpoint (sin webhook)
- **THEN** la respuesta es `422 Unprocessable Entity` (solo vía webhook de pago)
- **WHEN** un ADMIN transiciona de `CONFIRMADO` a `EN_PREPARACION`
- **THEN** el pedido pasa a `EN_PREPARACION`
- **WHEN** un ADMIN transiciona de `CONFIRMADO` a `CANCELADO`
- **THEN** el pedido pasa a `CANCELADO` Y el stock de los productos se restaura
- **WHEN** un ADMIN transiciona de `EN_PREPARACION` a `EN_CAMINO`
- **THEN** el pedido pasa a `EN_CAMINO`
- **WHEN** un ADMIN transiciona de `EN_PREPARACION` a `CANCELADO`
- **THEN** el pedido pasa a `CANCELADO` Y el stock de los productos se restaura
- **WHEN** un ADMIN transiciona de `EN_CAMINO` a `ENTREGADO`
- **THEN** el pedido pasa a `ENTREGADO`

#### Scenario: Terminal states reject all transitions

- **WHEN** se intenta cualquier transición desde `ENTREGADO`
- **THEN** la respuesta es `422 Unprocessable Entity`
- **WHEN** se intenta cualquier transición desde `CANCELADO`
- **THEN** la respuesta es `422 Unprocessable Entity`

#### Scenario: Role validation per FSM transition

- **WHEN** un CLIENT intenta transicionar un pedido (que no sea cancelar el propio en PENDIENTE)
- **THEN** la respuesta es `403 Forbidden`
- **WHEN** un STOCK intenta transicionar un pedido (sin permiso PEDIDOS/ADMIN)
- **THEN** la respuesta es `403 Forbidden`

---

### Requirement: Payment operations MUST be fully tested

El sistema DEBE tener tests que verifiquen la creación de preferencias de pago, el procesamiento del webhook de MercadoPago con validación de firma e idempotencia, el historial de pagos, y el reintento tras rechazo.

#### Scenario: Payment preference creation validates state and ownership

- **WHEN** un CLIENT autenticado hace `POST /api/v1/pagos/crear` para su pedido en estado `PENDIENTE`
- **THEN** la respuesta es `201 Created` con los datos de la preferencia de MercadoPago
- **WHEN** se intenta crear un pago para un pedido inexistente
- **THEN** la respuesta es `404 Not Found`
- **WHEN** se intenta crear un pago para un pedido que NO está en `PENDIENTE`
- **THEN** la respuesta es `400 Bad Request`
- **WHEN** un usuario no autenticado intenta crear un pago
- **THEN** la respuesta es `403 Forbidden`
- **WHEN** un CLIENT intenta crear un pago para un pedido de otro usuario
- **THEN** la respuesta es `403 Forbidden`

#### Scenario: Payment creation is idempotent

- **WHEN** se crea un pago con una `idempotency_key` por primera vez
- **THEN** la respuesta es `201 Created` con una nueva preferencia
- **WHEN** se repite la misma request con la misma `idempotency_key`
- **THEN** la respuesta es `200 OK` y retorna la misma preferencia (no se crea un pago duplicado)

#### Scenario: Webhook processes approved payment and confirms order

- **WHEN** el webhook recibe una notificación de pago aprobado con firma válida
- **THEN** la respuesta es `200 OK`
- **AND** el pedido asociado pasa a estado `CONFIRMADO`
- **AND** el stock de los productos del pedido se decrementa

#### Scenario: Webhook validates signature

- **WHEN** el webhook recibe una notificación con firma inválida o ausente
- **THEN** la respuesta es `401 Unauthorized`
- **AND** el pedido NO cambia de estado

#### Scenario: Webhook is idempotent for duplicate notifications

- **WHEN** el webhook recibe una notificación duplicada (mismo `payment_id` ya procesado)
- **THEN** la respuesta es `200 OK`
- **AND** el pedido NO cambia de estado (ya estaba CONFIRMADO)
- **AND** no se crean entradas duplicadas en el historial

#### Scenario: Webhook handles rejected payment

- **WHEN** el webhook recibe una notificación de pago rechazado
- **THEN** la respuesta es `200 OK`
- **AND** el pedido permanece en estado `PENDIENTE` (no cambia)

#### Scenario: Payment history is accessible and enforces ownership

- **WHEN** un CLIENT hace `GET /api/v1/pagos/{pedido_id}` de su propio pedido
- **THEN** la respuesta es `200 OK` con los intentos de pago registrados
- **WHEN** un CLIENT hace `GET /api/v1/pagos/{pedido_id}` de un pedido ajeno
- **THEN** la respuesta es `403 Forbidden`

#### Scenario: Payment retry works after rejection

- **WHEN** un CLIENT hace `POST /api/v1/pagos/reintentar` después de un pago rechazado
- **THEN** la respuesta es `201 Created` con una nueva preferencia
- **WHEN** un CLIENT hace `POST /api/v1/pagos/reintentar` cuando el último pago fue aprobado
- **THEN** la respuesta es `400 Bad Request`

---

### Requirement: Checkout validation MUST be fully tested

El sistema DEBE tener tests que verifiquen la validación de items del carrito antes del pago, incluyendo existencia de producto, disponibilidad, stock suficiente, personalizaciones válidas, cambios de precio, y carrito vacío.

#### Scenario: Checkout validates valid items successfully

- **WHEN** se hace `POST /api/v1/checkout/validar` con items válidos (productos existentes, disponibles, con stock suficiente)
- **THEN** la respuesta es `200 OK` con un resultado de validación exitoso

#### Scenario: Checkout detects non-existent product

- **WHEN** se hace `POST /api/v1/checkout/validar` con un `producto_id` que no existe
- **THEN** la respuesta es `200 OK` pero el resultado de validación contiene un error de "producto no encontrado"

#### Scenario: Checkout detects unavailable product

- **WHEN** se hace `POST /api/v1/checkout/validar` con un producto marcado como `disponible=false`
- **THEN** la respuesta es `200 OK` pero el resultado contiene un error de "producto no disponible"

#### Scenario: Checkout detects insufficient stock

- **WHEN** se hace `POST /api/v1/checkout/validar` con una cantidad mayor al stock disponible
- **THEN** la respuesta es `200 OK` pero el resultado contiene un error de "stock insuficiente"

#### Scenario: Checkout validates ingredient customizations

- **WHEN** se hace `POST /api/v1/checkout/validar` con personalizaciones que referencian un ingrediente inexistente
- **THEN** la respuesta es `200 OK` pero el resultado contiene un error de personalización inválida

#### Scenario: Checkout warns on price change

- **WHEN** se hace `POST /api/v1/checkout/validar` con un precio que no coincide con el precio actual del producto
- **THEN** la respuesta es `200 OK` pero el resultado contiene un warning de "precio cambiado"

#### Scenario: Checkout rejects empty cart

- **WHEN** se hace `POST /api/v1/checkout/validar` con una lista de items vacía
- **THEN** la respuesta es `200 OK` pero el resultado contiene un error de "carrito vacío"

---

### Requirement: Test fixtures MUST include pre-authenticated role clients

El sistema DEBE proveer fixtures de `TestClient` pre-autenticados para cada rol (ADMIN, CLIENT, STOCK, PEDIDOS) de modo que los tests no necesiten registrar y loguear usuarios manualmente.

#### Scenario: admin_client fixture provides authenticated ADMIN TestClient

- **WHEN** un test usa el fixture `admin_client`
- **THEN** el `TestClient` tiene el header `Authorization: Bearer <token>` configurado
- **AND** el token corresponde a un usuario con rol `ADMIN`
- **AND** las requests autenticadas con este cliente pasan la verificación de RBAC para endpoints de ADMIN

#### Scenario: client_client fixture provides authenticated CLIENT TestClient

- **WHEN** un test usa el fixture `client_client`
- **THEN** el `TestClient` tiene el header `Authorization: Bearer <token>` configurado
- **AND** el token corresponde a un usuario con rol `CLIENT`
- **AND** las requests con este cliente son rechazadas en endpoints que requieren ADMIN

#### Scenario: stock_client fixture provides authenticated STOCK TestClient

- **WHEN** un test usa el fixture `stock_client`
- **THEN** el `TestClient` tiene el header `Authorization: Bearer <token>` configurado
- **AND** el token corresponde a un usuario con rol `STOCK`

#### Scenario: pedidos_client fixture provides authenticated PEDIDOS TestClient

- **WHEN** un test usa el fixture `pedidos_client`
- **THEN** el `TestClient` tiene el header `Authorization: Bearer <token>` configurado
- **AND** el token corresponde a un usuario con rol `PEDIDOS`

---

### Requirement: Test fixtures MUST include seed data for reference tables

El sistema DEBE proveer fixtures que inserten datos de referencia en la base de datos de prueba: estados de pedido, formas de pago, productos, categorías, ingredientes, y direcciones.

#### Scenario: seed_estados fixture provides all 6 order states

- **WHEN** un test usa el fixture `seed_estados`
- **THEN** la base de datos contiene los 6 estados: PENDIENTE, CONFIRMADO, EN_PREPARACION, EN_CAMINO, ENTREGADO, CANCELADO
- **AND** ENTREGADO y CANCELADO tienen `es_terminal=true`

#### Scenario: seed_formas_pago fixture provides 3 payment methods

- **WHEN** un test usa el fixture `seed_formas_pago`
- **THEN** la base de datos contiene las 3 formas de pago (tarjeta, Rapipago, Pago Fácil)

#### Scenario: seed_producto fixture provides a test product with stock

- **WHEN** un test usa el fixture `seed_producto`
- **THEN** existe un producto en la BD con `nombre`, `precio > 0`, `stock > 0`, `disponible=true`, y pertenece a una categoría

#### Scenario: seed_categoria fixture provides a test category

- **WHEN** un test usa el fixture `seed_categoria`
- **THEN** existe una categoría en la BD con `nombre` y `slug`

#### Scenario: seed_ingrediente fixture provides a test ingredient

- **WHEN** un test usa el fixture `seed_ingrediente`
- **THEN** existe un ingrediente en la BD con `nombre` y opcionalmente información de alérgenos

#### Scenario: seed_direccion fixture provides a test address

- **WHEN** un test usa el fixture `seed_direccion`
- **THEN** existe una dirección en la BD asociada a un usuario de prueba

---

### Requirement: Overall test coverage MUST reach at least 60 percent

El sistema DEBE alcanzar una cobertura total de statements ≥60% medida con `pytest --cov=app --cov-report=term`.

#### Scenario: Coverage report shows 60 percent or higher

- **WHEN** se ejecuta `pytest --cov=app --cov-report=term` con todos los tests (existentes + nuevos)
- **THEN** el reporte de cobertura muestra `TOTAL` con ≥60% de statements cubiertos

#### Scenario: All existing tests continue to pass

- **WHEN** se ejecuta `pytest` con todos los tests
- **THEN** los 152 tests existentes pasan sin modificaciones (sin regresión)

#### Scenario: Tests are isolated and independent

- **WHEN** se ejecutan los tests en orden aleatorio (`pytest --random-order`)
- **THEN** todos los tests pasan (ningún test depende del orden de ejecución)
