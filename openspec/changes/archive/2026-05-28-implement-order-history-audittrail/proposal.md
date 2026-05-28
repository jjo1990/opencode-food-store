## Why

El historial de cambios de estado ya se registra (creación de pedido, webhook, FSM), pero no hay un endpoint dedicado para consultarlo. El detalle del pedido (`GET /pedidos/{id}`) incluye el historial, pero sin el nombre del actor (solo el ID). Para el timeline visual y la auditoría administrativa se necesita un endpoint específico con datos enriquecidos.

## What Changes

- **Nuevo endpoint `GET /api/v1/pedidos/{id}/historial`**: retorna el historial de cambios de estado del pedido ordenado cronológicamente
- **Enriquecimiento del actor**: cada entrada incluye `actor_id` y `actor_nombre` (nombre del usuario o "SISTEMA" si es null)
- **Misma seguridad**: ownership check (CLIENT ve propio, ADMIN/PEDIDOS ve todos)

## Capabilities

### New Capabilities

- `order-history-audittrail`: Endpoint de consulta de historial de cambios de estado con datos enriquecidos del actor

### Modified Capabilities

- (ninguna)

## Impact

- **Nuevo endpoint**: `GET /api/v1/pedidos/{id}/historial`
- **Archivos a modificar**:
  - `backend/app/pedidos/schemas.py` — nuevo `HistorialResponse` con `actor_nombre`
  - `backend/app/pedidos/service.py` — nuevo método `obtener_historial()`
  - `backend/app/pedidos/router.py` — nueva ruta GET
