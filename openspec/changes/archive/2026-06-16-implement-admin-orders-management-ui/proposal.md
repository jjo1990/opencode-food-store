## Why

El panel de administración tiene los endpoints REST de gestión de pedidos funcionando desde Change 38 (`implement-admin-order-management`) — listado con filtros avanzados, cambio de estado con FSM y detalle completo con snapshots e historial. La navegación ya redirige a `/admin/orders` y los componentes compartidos `OrderBadge` y `OrderTimeline` están listos, pero la página `AdminOrdersPage` es un placeholder que solo muestra "Próximamente". Los administradores y gestores de pedidos necesitan una UI completa para buscar, filtrar, visualizar en detalle y transicionar pedidos entre estados directamente desde el panel. Completar esta UI desbloquea la operación diaria de gestión de pedidos del negocio.

## What Changes

- Crear `shared/api/adminOrdersApi.ts` con tipos TypeScript y funciones fetch para los 3 endpoints admin (`GET /admin/pedidos`, `GET /admin/pedidos/{id}`, `PATCH /admin/pedidos/{id}/estado`)
- Crear `features/admin-orders/hooks/useAdminOrders.ts` con TanStack Query hooks (`useAdminOrders`, `useAdminOrder`, `useChangeOrderState`)
- Reemplazar el placeholder `AdminOrdersPage.tsx` con tabla completa: columnas ID/Cliente/Monto/Estado(badge)/Fecha, filtros por ID de pedido, nombre de cliente, estado, rango de fechas, hover preview con tooltip de datos rápidos (cliente, dirección, items), paginación
- Crear modal de detalle (`OrderDetailModal.tsx`): información del pedido, tabla de items con snapshots, timeline de historial (`OrderTimeline`), botones de acción (Avanzar Estado, Cancelar)
- Crear modal de cambio de estado (`ChangeStateModal.tsx`): dropdown con estados siguientes válidos según FSM, input de motivo (obligatorio si destino es CANCELADO), confirmación
- Todo cambio de filtro resetea página a 1
- Estilo visual consistente con `AdminUsersPage.tsx`: estados loading/error/empty, badges de estado con colores via `OrderBadge`

## Capabilities

### New Capabilities

- `admin-orders`: Interfaz de gestión de pedidos en el panel de administración — tabla paginada con búsqueda por ID/cliente, filtros por estado y rango de fechas, hover preview con tooltip, modal de detalle con snapshots e historial timeline, y modal de cambio de estado con FSM validation integrada y motivo obligatorio para cancelación.

### Modified Capabilities

<!-- None — this is a new frontend UI. No existing spec requirements change. -->

## Impact

- **Código afectado**: Solo frontend (no requiere cambios en backend)
  - `frontend/src/shared/api/adminOrdersApi.ts` — nuevo
  - `frontend/src/features/admin-orders/hooks/useAdminOrders.ts` — nuevo
  - `frontend/src/features/admin-orders/components/OrderDetailModal.tsx` — nuevo
  - `frontend/src/features/admin-orders/components/ChangeStateModal.tsx` — nuevo
  - `frontend/src/features/admin-orders/components/AdminOrderTable.tsx` — nuevo
  - `frontend/src/features/admin-orders/components/HoverPreview.tsx` — nuevo
  - `frontend/src/pages/admin/AdminOrdersPage.tsx` — reescritura completa
- **APIs consumidas**: `/api/v1/admin/pedidos`, `/api/v1/admin/pedidos/{id}`, `/api/v1/admin/pedidos/{id}/estado` (ya existentes, sin cambios)
- **Dependencias**: `implement-admin-order-management` (backend completado, Change 38), `implement-admin-dashboard-ui` (dashboard y layout admin completados, Change 41)
- **Componentes compartidos reutilizados**: `OrderBadge`, `OrderTimeline`, `Modal`, `Card`, `Skeleton`, `ErrorDisplay`, `EmptyState`, `Spinner`, `Pagination`
