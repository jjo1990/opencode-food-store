## ADDED Requirements

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
