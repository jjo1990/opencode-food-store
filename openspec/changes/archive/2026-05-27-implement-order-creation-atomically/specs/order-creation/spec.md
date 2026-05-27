## ADDED Requirements

### Requirement: Cliente puede crear un pedido desde su carrito

El sistema SHALL proveer un endpoint `POST /api/v1/pedidos` que permita a un cliente autenticado crear un pedido. La operación SHALL ser atómica: o persisten todos los datos o no persiste ninguno.

#### Scenario: Creación exitosa de pedido

- **WHEN** un cliente autenticado envía `POST /api/v1/pedidos` con items válidos, una dirección propia existente, y una forma de pago activa
- **THEN** el sistema retorna HTTP 201 con el `PedidoRead` (id, estado="PENDIENTE", total, created_at)
- **AND** se crea un registro en `pedido` con estado PENDIENTE
- **AND** se crean N registros en `detalle_pedido` (uno por item) con snapshots de precio y nombre
- **AND** se crea un registro en `historial_estado_pedido` con estado_desde=NULL y estado_nuevo="PENDIENTE"
- **AND** el carrito del cliente NO se modifica (el frontend lo limpia aparte)

#### Scenario: Producto no encontrado

- **WHEN** un item contiene un `producto_id` que no existe o está marcado como soft-deleted
- **THEN** el sistema retorna HTTP 422 con error describiendo qué producto_id es inválido
- **AND** no se persiste ningún cambio en BD

#### Scenario: Producto no disponible

- **WHEN** un item contiene un `producto_id` de un producto con `disponible=false`
- **THEN** el sistema retorna HTTP 422 con error "Producto X no está disponible"
- **AND** no se persiste ningún cambio en BD

#### Scenario: Stock insuficiente

- **WHEN** un item solicita una cantidad mayor al `stock_cantidad` del producto
- **THEN** el sistema retorna HTTP 422 con error "Stock insuficiente para Producto X (disponible: Y, solicitado: Z)"
- **AND** no se persiste ningún cambio en BD

#### Scenario: Dirección no pertenece al usuario

- **WHEN** el `direccion_id` enviado pertenece a otro usuario o no existe
- **THEN** el sistema retorna HTTP 422 con error "Dirección no encontrada"
- **AND** no se persiste ningún cambio en BD

#### Scenario: Forma de pago no existe o deshabilitada

- **WHEN** el `forma_pago_codigo` no existe en el catálogo o tiene `habilitado=false`
- **THEN** el sistema retorna HTTP 422 con error "Forma de pago no válida"
- **AND** no se persiste ningún cambio en BD

#### Scenario: Carrito vacío

- **WHEN** la lista de items está vacía
- **THEN** el sistema retorna HTTP 422 con error "Debe incluir al menos un item"
- **AND** no se persiste ningún cambio en BD

### Requirement: Snapshots inmutables en el pedido

El sistema SHALL capturar snapshots de los datos volátiles al momento de crear el pedido para garantizar la inmutabilidad histórica.

#### Scenario: Precio snapshot en detalle

- **WHEN** se crea un pedido
- **THEN** cada `detalle_pedido` almacena `precio_snapshot` con el valor de `producto.precio_base` al momento de la creación
- **AND** si el precio del producto cambia después, el detalle del pedido existente NO se modifica

#### Scenario: Nombre snapshot en detalle

- **WHEN** se crea un pedido
- **THEN** cada `detalle_pedido` almacena `nombre_snapshot` con el valor de `producto.nombre` al momento de la creación

#### Scenario: Dirección snapshot en pedido

- **WHEN** se crea un pedido
- **THEN** el `pedido` almacena `direccion_snapshot` con la dirección completa serializada (calle, numero, ciudad, etc.)
- **AND** si el usuario modifica o elimina la dirección después, el pedido existente NO se ve afectado

### Requirement: Cálculo de totales

El sistema SHALL calcular automáticamente los valores monetarios del pedido.

#### Scenario: Cálculo de subtotal

- **WHEN** se crea un pedido con múltiples items
- **THEN** cada `detalle_pedido.subtotal` = `precio_snapshot * cantidad`
- **AND** `pedido.subtotal` = suma de todos los `detalle_pedido.subtotal`

#### Scenario: Cálculo de costo de envío

- **WHEN** se crea un pedido
- **THEN** `pedido.costo_envio` = 50.00 (valor fijo v1)

#### Scenario: Cálculo de total

- **WHEN** se crea un pedido
- **THEN** `pedido.total` = `pedido.subtotal + pedido.costo_envio`

### Requirement: Historial inicial del pedido

El sistema SHALL registrar el estado inicial del pedido en el historial append-only.

#### Scenario: Primer registro de historial

- **WHEN** se crea un pedido exitosamente
- **THEN** se inserta un registro en `historial_estado_pedido` con:
  - `estado_desde` = NULL (RN-02)
  - `estado_nuevo` = "PENDIENTE"
  - `actor_id` = ID del usuario que creó el pedido
  - `created_at` = timestamp actual

#### Scenario: Append-only enforcement

- **WHEN** se intenta actualizar o eliminar un registro existente en `historial_estado_pedido`
- **THEN** el sistema (a nivel de aplicación) SHALL rechazar la operación
- **AND** solo se permiten INSERTs en esta tabla

### Requirement: SELECT FOR UPDATE en validación de stock

El sistema SHALL bloquear los rows de productos durante la validación de stock para prevenir race conditions.

#### Scenario: Lock optimista en validación concurrente

- **WHEN** dos solicitudes de creación de pedido intentan usar el mismo producto simultáneamente
- **THEN** cada solicitud SHALL ejecutar `SELECT ... FOR UPDATE` sobre el producto antes de validar stock
- **AND** la segunda solicitud SHALL esperar hasta que la primera complete su transacción
- **AND** si después de la primera transacción el stock es insuficiente, la segunda SHALL fallar con error de stock insuficiente

### Requirement: Seed data para catálogos

El sistema SHALL incluir datos semilla para que la creación de pedidos funcione.

#### Scenario: Estados de pedido seedeados

- **WHEN** se ejecuta el script de seed
- **THEN** existen 6 registros en `estado_pedido`: PENDIENTE (orden 1), CONFIRMADO (2), EN_PREPARACIÓN (3), EN_CAMINO (4), ENTREGADO (5, es_terminal=true), CANCELADO (6, es_terminal=true)

#### Scenario: Formas de pago seedeadas

- **WHEN** se ejecuta el script de seed
- **THEN** existen 3 registros en `forma_pago`: MERCADOPAGO (habilitado), EFECTIVO (habilitado), TRANSFERENCIA (habilitado)

#### Scenario: Idempotencia del seed

- **WHEN** el script de seed se ejecuta múltiples veces
- **THEN** no se duplican registros (usa `INSERT ... ON CONFLICT DO NOTHING`)
