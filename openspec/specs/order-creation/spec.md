# order-creation Specification

## Purpose

TBD - created by archiving change implement-order-creation-atomically. Update Purpose after archive.

## Requirements

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

### Requirement: Cliente puede listar sus pedidos

El sistema SHALL proveer un endpoint `GET /api/v1/pedidos` que permita a un usuario autenticado listar pedidos. Los clientes (CLIENT) ven solo sus propios pedidos. Los usuarios con rol ADMIN o PEDIDOS ven todos los pedidos del sistema.

#### Scenario: Cliente lista sus propios pedidos

- **WHEN** un cliente autenticado envía `GET /api/v1/pedidos`
- **THEN** el sistema retorna HTTP 200 con una lista paginada de `PedidoListRead`
- **AND** la lista contiene solo pedidos donde `usuario_id` coincide con el usuario actual
- **AND** los pedidos eliminados (soft_deleted_at NOT NULL) NO se incluyen

#### Scenario: Admin lista todos los pedidos

- **WHEN** un usuario con rol ADMIN o PEDIDOS envía `GET /api/v1/pedidos`
- **THEN** el sistema retorna HTTP 200 con una lista paginada de TODOS los pedidos del sistema (sin filtrar por usuario)

#### Scenario: Paginación funcional

- **WHEN** un usuario envía `GET /api/v1/pedidos?skip=0&limit=10`
- **THEN** el sistema retorna hasta 10 pedidos (o menos si no hay suficientes)
- **AND** la respuesta incluye `total` con la cantidad total de pedidos que coinciden con el filtro

#### Scenario: Filtro por estado

- **WHEN** un usuario envía `GET /api/v1/pedidos?estado_codigo=PENDIENTE`
- **THEN** el sistema retorna solo pedidos cuyo `estado_codigo` es "PENDIENTE"

### Requirement: Usuario puede ver detalle de un pedido

El sistema SHALL proveer un endpoint `GET /api/v1/pedidos/{id}` que retorne el detalle completo de un pedido. Incluye: datos del pedido, items con snapshots (nombre, precio, cantidad, subtotal, personalización), e historial de estados ordenado cronológicamente.

#### Scenario: Cliente ve detalle de su propio pedido

- **WHEN** un cliente autenticado envía `GET /api/v1/pedidos/{id}` donde el pedido le pertenece
- **THEN** el sistema retorna HTTP 200 con `PedidoDetail`
- **AND** la respuesta incluye los items del pedido con sus snapshots
- **AND** la respuesta incluye el historial de estados ordenado ASC por `created_at`

#### Scenario: Cliente no puede ver pedido ajeno

- **WHEN** un cliente autenticado envía `GET /api/v1/pedidos/{id}` donde el pedido pertenece a otro usuario
- **THEN** el sistema retorna HTTP 404

#### Scenario: Admin/PEDIDOS puede ver cualquier pedido

- **WHEN** un usuario con rol ADMIN o PEDIDOS envía `GET /api/v1/pedidos/{id}` de cualquier pedido
- **THEN** el sistema retorna HTTP 200 con el detalle completo

#### Scenario: Pedido no encontrado

- **WHEN** un usuario envía `GET /api/v1/pedidos/{id}` con un ID que no existe o está soft-deleted
- **THEN** el sistema retorna HTTP 404

### Requirement: Historial ordenado en detalle

El sistema SHALL retornar el historial de estados del pedido ordenado cronológicamente (ASC) en el detalle.

#### Scenario: Historial cronológico

- **WHEN** se solicita el detalle de un pedido con múltiples transiciones de estado
- **THEN** el historial se retorna ordenado ASC por `created_at` (más antiguo primero)
- **AND** el primer registro tiene `estado_desde = NULL` (RN-02)

### Requirement: Interfaz de listado de pedidos

El sistema SHALL proveer una interfaz visual para listar pedidos, adaptada por rol (CLIENT ve propios, ADMIN/PEDIDOS ve todos).

#### Scenario: Cliente ve lista de sus pedidos

- **WHEN** un cliente autenticado navega a `/orders`
- **THEN** el sistema muestra una tabla responsive con: ID (truncado), estado (badge color), total, fecha
- **AND** los pedidos se ordenan del más reciente al más antiguo
- **AND** hay paginación si hay más de 20 pedidos

#### Scenario: Admin/Gestor ve todos los pedidos

- **WHEN** un usuario con rol ADMIN o PEDIDOS navega a `/pedidos`
- **THEN** el sistema muestra la misma tabla pero incluye columna "Cliente"
- **AND** puede ver pedidos de cualquier usuario

#### Scenario: Estados vacío

- **WHEN** un usuario sin pedidos navega a `/orders`
- **THEN** el sistema muestra EmptyState con mensaje "Aún no tienes pedidos" y CTA "Ir al catálogo"

### Requirement: Interfaz de detalle de pedido

El sistema SHALL proveer una vista de detalle de pedido con información completa: datos generales, items con snapshots, y timeline de historial.

#### Scenario: Cliente ve detalle de pedido

- **WHEN** un cliente hace clic en un pedido de su lista
- **THEN** el sistema muestra un modal con:
  - **Info general**: ID, estado (badge), total, costo envío, fecha
  - **Items**: tabla con nombre, precio snapshot, cantidad, subtotal, personalización
  - **Timeline**: historial de estados con conectores visuales, timestamps y actores

#### Scenario: Timeline visual

- **WHEN** se muestra el timeline de un pedido con múltiples estados
- **THEN** cada estado se muestra como un step con: círculo de color, nombre del estado, timestamp, y línea conectora
- **AND** el estado actual se destaca visualmente
- **AND** los estados futuros (no alcanzados) se muestran atenuados o como placeholder

### Requirement: Pantalla de confirmación post-creación

El sistema SHALL mostrar una pantalla de confirmación inmediatamente después de crear un pedido exitosamente.

#### Scenario: Confirmación de pedido creado

- **WHEN** un cliente crea un pedido exitosamente
- **THEN** el sistema muestra una pantalla con:
  - Ícono de éxito (check verde)
  - Mensaje "¡Pedido creado exitosamente!"
  - ID del pedido
  - Total pagado
  - Dirección de entrega
  - Botón "Ver mis pedidos"
  - Botón "Ir a pagar" (si forma_pago = MERCADOPAGO)
