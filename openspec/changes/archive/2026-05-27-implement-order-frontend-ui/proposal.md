## Why

Los pedidos ya se crean (Change 28) y se pueden consultar via API (Change 29), pero no existe interfaz visual. El cliente no puede ver sus pedidos ni su detalle. Los gestores de pedidos (PEDIDOS) tienen una página stub sin funcionalidad. Sin UI de pedidos, el ciclo de compra está incompleto — el usuario crea un pedido y no ve qué pasó.

## What Changes

- **Nuevo API module**: `shared/api/pedidosApi.ts` con funciones para listar y obtener detalle de pedidos
- **Nueva entity**: `entities/order/` con types y TanStack Query hooks (useOrders, useOrder)
- **Nuevos componentes** en `features/orders/components/`:
  - `OrderConfirmation`: pantalla post-creación con ID, total, dirección, CTAs
  - `OrderList`: tabla responsive con badges de estado, paginación, cliente (admin)
  - `OrderDetail`: modal/vista expandible con snapshots, timeline de historial
- **Nuevas páginas**:
  - `/orders` para CLIENT: listado de pedidos del cliente
  - `/orders/:id` para CLIENT: detalle de pedido propio
- **Actualización de páginas existentes**:
  - `/pedidos` para PEDIDOS/ADMIN: reemplazar stub con OrderList real
  - `/pedidos/:id` para PEDIDOS/ADMIN: detalle de cualquier pedido
- **Registro en router**: nuevas rutas en `app/router.tsx`

## Capabilities

### Modified Capabilities

- `order-creation`: se agregan requirements de interfaz visual para listado y detalle de pedidos (frontend)

## Impact

- **Frontend**: ~9 archivos nuevos (api, entity, 3 componentes, páginas) + router.tsx modificado
- **No hay cambios backend**: todo consume la API existente de Changes 28-29
- **Backend**: ningún cambio
