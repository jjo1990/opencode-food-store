## 1. API y Entity Layer

- [x] 1.1 Crear `shared/api/pedidosApi.ts` con funciones `getPedidos(params)`, `getPedido(id)` e interfaces de respuesta
- [x] 1.2 Crear `entities/order/types.ts` con interfaces Order, OrderDetail, OrderHistoryItem
- [x] 1.3 Crear `entities/order/api.ts` con hooks `useOrders(filters)`, `useOrder(id)` usando TanStack Query

## 2. Componentes Compartidos

- [x] 2.1 Crear `shared/components/OrderTimeline.tsx` — timeline visual vertical con steps, conectores, colores por estado, timestamps
- [x] 2.2 Crear `shared/components/OrderBadge.tsx` — badge de estado con color semántico (PENDIENTE=amber, CONFIRMADO=blue, EN_PREPARACION=indigo, EN_CAMINO=purple, ENTREGADO=green, CANCELADO=red)

## 3. Feature Components

- [x] 3.1 Crear `features/orders/components/OrderList.tsx` — tabla responsive con columnas: ID, estado (OrderBadge), total, fecha, cliente (si admin), acción "Ver detalle"
- [x] 3.2 Crear `features/orders/components/OrderDetail.tsx` — modal con info general, items con snapshots, y OrderTimeline
- [x] 3.3 Crear `features/orders/components/OrderConfirmation.tsx` — pantalla de éxito post-creación con ID, total, dirección, CTAs

## 4. Pages y Router

- [x] 4.1 Crear `pages/OrdersPage.tsx` para CLIENT — listado de pedidos del usuario autenticado
- [x] 4.2 Actualizar `pages/pedidos/PedidosPanelPage.tsx` — reemplazar stub con OrderList real para ADMIN/PEDIDOS
- [x] 4.3 Registrar rutas en `app/router.tsx`: `/orders` (CLIENT), y actualizar `/pedidos` con lazy loading

## 5. Verificación

- [x] 5.1 Verificar TypeScript: `npx tsc --noEmit` sin errores
- [x] 5.2 Verificar build: `npm run build` exitoso
