# Tasks: implement-admin-orders-management-ui

## 1. API Client — Admin Orders

- [x] 1.1 Create `frontend/src/shared/api/adminOrdersApi.ts`
  - [x] 1.1.1 Define TypeScript interfaces: `AdminOrderListItem`, `AdminOrderListResponse`, `AdminChangeStateRequest`, `AdminOrdersParams`, `PedidoDetail`
  - [x] 1.1.2 Define `PedidoDetail`, `DetallePedidoRead`, `HistorialRead` inline (self-contained types, no import from pedidosApi.ts needed)
  - [x] 1.1.3 Implement `fetchAdminOrders(params)` — GET `/admin/pedidos` with query params (page, size, estado_codigo, fecha_inicio, fecha_fin, usuario_id, monto_min, monto_max, search)
  - [x] 1.1.4 Implement `fetchAdminOrderDetail(id)` — GET `/admin/pedidos/{id}`, returns `PedidoDetail`
  - [x] 1.1.5 Implement `changeOrderState(id, body)` — PATCH `/admin/pedidos/{id}/estado`, body: `AdminChangeStateRequest`

## 2. FSM Constants

- [x] 2.1 Create `frontend/src/features/admin-orders/constants.ts`
  - [x] 2.1.1 Define `TRANSITIONS` object mirroring the FSM transitions (simplified per GROUP 2 instructions)
  - [x] 2.1.2 Define `TERMINAL_STATES` set: `['ENTREGADO', 'CANCELADO']`
  - [x] 2.1.3 Define `ESTADO_LABELS` for human-readable estado names

## 3. TanStack Query Hooks

- [x] 3.1 Create `frontend/src/features/admin-orders/hooks/useAdminOrders.ts`
  - [x] 3.1.1 Implement `useAdminOrders(params)` — useQuery with `['admin-orders', params]`, `placeholderData: (prev) => prev`, `staleTime: 15000`
  - [x] 3.1.2 Implement `useAdminOrderDetail(orderId)` — useQuery with `['admin-order-detail', orderId]`, `enabled: !!orderId`
  - [x] 3.1.3 Implement `useChangeOrderState()` — useMutation, invalidates `['admin-orders']` and `['admin-order-detail']`, toast success/error with API error message extraction

## 4. AdminOrdersPage — Table, Filters, Pagination

- [x] 4.1 Rewrite `frontend/src/pages/admin/AdminOrdersPage.tsx` (replace placeholder)
  - [x] 4.1.1 Add header: "Gestión de Pedidos" + description "Administración de pedidos y cambios de estado."
  - [x] 4.1.2 Add combined search input with debounce (localState + 300ms setTimeout + reset page to 1)
  - [x] 4.1.3 Single search input covers both ID and client name (combined field per design)
  - [x] 4.1.4 Add estado filter select: "Todos", "Pendiente", "Confirmado", "En Preparación", "En Camino", "Entregado", "Cancelado" — maps labels to estado_codigo values
  - [x] 4.1.5 Add date range inputs: `fecha_inicio` (type="date") and `fecha_fin` (type="date")
  - [x] 4.1.6 Build params object from filter state, pass to `useAdminOrders(params)`. Only include non-empty params
  - [x] 4.1.7 Handle loading state: render `<Skeleton />` with table-like layout (5 rows)
  - [x] 4.1.8 Handle error state: render `<ErrorDisplay />` with retry button calling `refetch()`
  - [x] 4.1.9 Handle empty state with filters active: `<EmptyState title="Sin resultados" description="No se encontraron pedidos con esos filtros." />`
  - [x] 4.1.10 Handle empty state with no filters: `<EmptyState title="No hay pedidos registrados" description="Aún no hay pedidos en el sistema." />`
  - [x] 4.1.11 Handle data state: render `<AdminOrderTable>` with items from `data.items`
  - [x] 4.1.12 `onSelectOrder` callback sets `selectedOrderId` → opens `OrderDetailModal`
  - [x] 4.1.13 Pagination controls: custom Prev/Next buttons matching AdminUsersPage pattern
  - [x] 4.1.14 "Mostrando X–Y de Z" text below pagination
  - [x] 4.1.15 Every filter change resets `page` to 1
  - [x] 4.1.16 Import and render `OrderDetailModal` and `EstadoChangeModal`, passing required props and callbacks

## 5. AdminOrderTable Component

- [x] 5.1 Create `frontend/src/features/admin-orders/components/AdminOrderTable.tsx`
  - [x] 5.1.1 Define props: `orders: AdminOrderListItem[]`, `isLoading`, `onSelectOrder: (id: string) => void`
  - [x] 5.1.2 Render table with columns: ID (truncated UUID), Cliente (cliente_nombre || truncated usuario_id), Monto ($ formatted), Estado (OrderBadge), Fecha (toLocaleDateString), Dirección (direccion_calle || '—')
  - [x] 5.1.3 Hover tooltip using HTML `title` attribute showing cliente + dirección (simpler than separate HoverPreview component per design doc alternative)
  - [x] 5.1.4 Terminal state styling: rows with `ENTREGADO` or `CANCELADO` have `opacity-75`

## 6. HoverPreview Component

- [x] 6.1 HoverPreview: implemented via HTML `title` attribute on `<tr>` elements in AdminOrderTable (simpler, no separate component needed). Shows "Cliente: {name}" + "Dirección: {street}".

## 7. OrderDetailModal Component

- [x] 7.1 Create `frontend/src/features/admin-orders/components/OrderDetailModal.tsx`
  - [x] 7.1.1 Define props: `orderId`, `isOpen`, `onClose`, `onAdvanceState`, `onCancelOrder`
  - [x] 7.1.2 Fetch order detail with `useAdminOrderDetail(orderId)` when `orderId` is set
  - [x] 7.1.3 Loading state: render `<Spinner size="lg" />` centered inside modal
  - [x] 7.1.4 Error state: render `<ErrorDisplay />` with retry button calling `refetch()`
  - [x] 7.1.5 Data state: render "Pedido #{id_truncado}" + OrderBadge
  - [x] 7.1.6 Info grid: Subtotal, Costo envío, Total ($ formateado), Fecha de creación
  - [x] 7.1.7 Items table: Producto (nombre_snapshot), Precio Unit. ($), Cantidad, Subtotal ($)
  - [x] 7.1.8 OrderTimeline with history from order detail and currentState from estado_codigo
  - [x] 7.1.9 Footer — non-terminal: buttons "Cancelar Pedido" and "Avanzar Estado"
  - [x] 7.1.10 Footer — terminal: message "Pedido en estado final" (no action buttons)
  - [x] 7.1.11 "Avanzar Estado" click: call `onAdvanceState(orderId, estado_codigo)`
  - [x] 7.1.12 "Cancelar Pedido" click: call `onCancelOrder(orderId, estado_codigo)`
  - [x] 7.1.13 Modal uses shared `<Modal>` component

## 8. ChangeStateModal Component

- [x] 8.1 Create `frontend/src/features/admin-orders/components/EstadoChangeModal.tsx`
  - [x] 8.1.1 Define props: `orderId`, `currentEstado`, `isOpen`, `onClose`, `onSuccess`
  - [x] 8.1.2 Valid transitions from `TRANSITIONS[currentEstado]` constants (simplified, no role filtering per GROUP 6 spec)
  - [x] 8.1.3 Render current state as OrderBadge
  - [x] 8.1.4 Render dropdown `<select>` with valid transitions
  - [x] 8.1.5 Local state: `selectedState` (default first valid option), `motivo` (default "")
  - [x] 8.1.6 Motivo textarea: required + validation when CANCELADO, optional otherwise with contextual placeholder
  - [x] 8.1.7 "Confirmar" button: calls `changeStateMutation.mutateAsync()`
  - [x] 8.1.8 Disabled if CANCELADO selected and motivo empty
  - [x] 8.1.9 Loading state: "Procesando..." on button while mutation is pending
  - [x] 8.1.10 On success: `onSuccess()` + `onClose()`, toast via mutation hook
  - [x] 8.1.11 On error: modal stays open, toast via mutation hook
  - [x] 8.1.12 "Cancelar" button: calls `onClose()`
  - [x] 8.1.13 Terminal state: shows message, no dropdown
  - [x] 8.1.14 Uses shared `<Modal>` component

## 9. Integration — AdminOrdersPage Modals Wiring

- [x] 9.1 Wire modals in `AdminOrdersPage.tsx`
  - [x] 9.1.1 Manage state: `selectedOrderId`, `changeStateOrder` ({ id, estado })
  - [x] 9.1.2 No user role fetching needed (constants use simplified TRANSITIONS without role filtering per GROUP 6)
  - [x] 9.1.3 `OrderDetailModal` receives: `orderId={selectedOrderId}`, `isOpen={!!selectedOrderId}`, `onClose`, `onAdvanceState`, `onCancelOrder`
  - [x] 9.1.4 `onAdvanceState` / `onCancelOrder` handlers: close detail modal, open EstadoChangeModal
  - [x] 9.1.5 `EstadoChangeModal` receives: `orderId`, `currentEstado`, `isOpen`, `onClose`, `onSuccess`
  - [x] 9.1.6 Modal close properly resets state variables to null

## 10. Verification

- [x] 10.1 TypeScript type-check passes: `npx tsc --noEmit` (frontend directory) — 0 errors ✅
- [ ] 10.2 Manual smoke test checklist (requires backend running):
  - [ ] Load `/admin/orders` → shows orders table with pagination (20 per page)
  - [ ] Search by order ID → filters correctly, page resets to 1
  - [ ] Search by client name → filters correctly, page resets to 1
  - [ ] Filter by estado → filters correctly, page resets to 1
  - [ ] Filter by date range → filters correctly, page resets to 1
  - [ ] Hover over row → tooltip shows client name and address
  - [ ] Hover over row with missing data → tooltip shows "No registrado"/"No especificada"
  - [ ] Click "Ver detalle" → opens detail modal with items, timeline, action buttons
  - [ ] Detail modal items table → shows snapshot prices and names
  - [ ] Detail modal timeline → shows history entries with dates
  - [ ] Detail modal for terminal order → shows "Pedido en estado final", no action buttons
  - [ ] Click "Avanzar Estado" → opens change state modal with valid transitions dropdown
  - [ ] FSM dropdown for CONFIRMADO → shows EN_PREPARACION and CANCELADO (ADMIN role)
  - [ ] FSM dropdown for EN_PREPARACION as PEDIDOS → shows only EN_CAMINO
  - [ ] Select CANCELADO in dropdown → motivo field becomes required, Confirmar disabled until filled
  - [ ] Select non-CANCELADO → motivo field optional, Confirmar enabled
  - [ ] Confirm valid state change → API called, toast success, modals close, table updates
  - [ ] Confirm state change with error → toast error shown, modal stays open
  - [ ] Cancel in change state modal → returns to detail modal
  - [ ] Loading state → skeleton table shown
  - [ ] Error state → error message with retry button shown
  - [ ] Empty state (no results) → empty message shown
  - [ ] Pagination → next/previous navigates pages, current page indicator updates
