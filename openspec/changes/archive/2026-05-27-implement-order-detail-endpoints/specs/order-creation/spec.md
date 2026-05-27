## ADDED Requirements

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
