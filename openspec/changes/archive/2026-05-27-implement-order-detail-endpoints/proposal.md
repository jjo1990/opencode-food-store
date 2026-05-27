## Why

El Change 28 creó el endpoint para crear pedidos, pero sin endpoints de lectura el usuario no puede ver sus pedidos ni el admin gestionarlos. Necesitamos `GET /api/v1/pedidos` (listado paginado con filtros) y `GET /api/v1/pedidos/{id}` (detalle completo con líneas, snapshots e historial) para que los pedidos sean visibles y operables.

## What Changes

- **Nuevos métodos en `PedidoRepository`**: `get_by_id()` con eager loading de detalles e historial, `get_by_user()` con filtros y paginación, `get_all()` para admin/PEDIDOS, métodos de count
- **Nuevos endpoints**:
  - `GET /api/v1/pedidos` — listado paginado, CLIENT ve solo sus pedidos, ADMIN/PEDIDOS ven todos. Filtrable por estado_codigo.
  - `GET /api/v1/pedidos/{id}` — detalle completo con items (snapshots), historial de estados (ordenado ASC), headers de ownership check
- **Schemas nuevos**: `PedidoListRead`, `PedidoDetail` (extiende PedidoRead con items + historial)
- **Actualización de spec `order-creation`**: se agregan los requirements de lectura

## Capabilities

### Modified Capabilities

- `order-creation`: Se agregan requirements de consulta de pedidos (listado paginado y detalle) con control de ownership por rol. El spec existente solo cubría creación.

## Impact

- **Backend**: solo se modifican archivos existentes del módulo `pedidos/` — repository, service, router, schemas
- **No hay cambios en BD**: reutiliza tablas existentes (pedido, detalle_pedido, historial_estado_pedido)
- **No hay migración**: cero cambios de schema
