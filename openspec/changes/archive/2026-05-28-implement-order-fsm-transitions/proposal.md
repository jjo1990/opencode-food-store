## Why

Los pedidos pueden cambiar de estado a lo largo de su ciclo de vida (PENDIENTE → CONFIRMADO → EN_PREPARACIÓN → EN_CAMINO → ENTREGADO), pero actualmente no existe un mecanismo centralizado que valide estas transiciones. El único cambio de estado ocurre en el webhook (PENDIENTE → CONFIRMADO). Sin la FSM, los administradores no pueden avanzar pedidos manualmente, cancelar pedidos, restaurar stock al cancelar, ni registrar el historial de cambios.

## What Changes

- **Nuevo service layer `PedidoService.avanzar_estado()`**: método central con validación de transiciones, roles y stock
- **Mapa de transiciones hardcodeado**: define qué transiciones son válidas (PENDIENTE→CONFIRMADO solo vía webhook), qué roles pueden ejecutarlas, y qué acciones de stock se requieren
- **Endpoint `PATCH /api/v1/pedidos/{id}/avanzar`**: recibe `{ nuevo_estado, motivo? }`, valida rol y transición, ejecuta el cambio
- **Endpoint `PATCH /api/v1/pedidos/{id}/cancelar`** o reutilización del avanzar: permite cancelación con validación de roles
- **Restauración de stock**: al cancelar desde CONFIRMADO o EN_PREPARACIÓN, incrementa stock atómicamente (SELECT FOR UPDATE)
- **Auditoría**: cada transición registra un `HistorialEstadoPedido` con estado_anterior, estado_nuevo, actor, motivo

No hay breaking changes. No se modifican endpoints existentes.

## Capabilities

### New Capabilities

- `order-fsm-transitions`: Máquina de estados de pedidos con validación de transiciones, roles, restauración de stock y auditoría

### Modified Capabilities

- (ninguna — el comportamiento existente de creación y consulta de pedidos no cambia)

## Impact

- **Nuevos endpoints**:
  - `PATCH /api/v1/pedidos/{id}/avanzar` (autenticado, rol según transición)
- **Archivos a crear**:
  - (no se crean archivos nuevos, se modifica el service existente)
- **Archivos a modificar**:
  - `backend/app/pedidos/schemas.py` — nuevo `AvanzarEstadoRequest` schema
  - `backend/app/pedidos/service.py` — nuevo método `avanzar_estado()` con FSM completa, restauración de stock, registro de historial
  - `backend/app/pedidos/router.py` — nueva ruta `PATCH /{pedido_id}/avanzar`
  - `backend/app/pedidos/repository.py` — posible método `update_estado()` si es necesario
- **Dependencias**: `Producto` model para restauración de stock
