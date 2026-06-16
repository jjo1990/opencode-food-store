## Component Tree

```
AdminOrdersPage
├── Header ("Gestión de Pedidos" + description)
├── Filters Bar
│   ├── OrderIdInput (busca por ID de pedido, debounced 300ms)
│   ├── ClientNameInput (busca por nombre de cliente, debounced 300ms)
│   ├── EstadoSelect (dropdown: Todos, PENDIENTE, CONFIRMADO, EN_PREPARACION, EN_CAMINO, ENTREGADO, CANCELADO)
│   ├── FechaInicioInput (type="date")
│   └── FechaFinInput (type="date")
├── Content Area (4 states: loading → error → empty → data)
│   ├── [loading] → <Skeleton variant="card" /> rows (8 rows table-like)
│   ├── [error]   → <ErrorDisplay message={...} onRetry={refetch} />
│   ├── [empty]   → <EmptyState title="Sin pedidos" description="No se encontraron pedidos con esos filtros." />
│   └── [data]    → AdminOrderTable
│       ├── <thead> column headers: ID, Cliente, Monto, Estado, Fecha, Acción
│       └── <tbody> rows
│           └── AdminOrderRow
│               ├── ID (truncated UUID)
│               ├── Cliente (cliente_nombre or "—")
│               ├── Monto ($ formatted)
│               ├── Estado (OrderBadge)
│               ├── Fecha (DD/MM/YYYY)
│               ├── Acción ("Ver detalle" button)
│               └── [hover] → HoverPreview tooltip
│                   ├── Cliente: {nombre}
│                   ├── Dirección: {direccion_calle}
│                   └── Items: {cantidad_items} productos
├── Pagination ("Mostrando X–Y de Z", Anterior / Siguiente, o shared <Pagination>)
├── OrderDetailModal (reuses <Modal>)
│   ├── [loading detail] → <Spinner />
│   ├── [error] → <ErrorDisplay /> + Reintentar
│   ├── [data]
│   │   ├── Header: ID pedido + OrderBadge
│   │   ├── Info Grid: Monto ($), Fecha, Cliente, Dirección
│   │   ├── Items Table: nombre_snapshot, precio_snapshot, cantidad, subtotal
│   │   ├── OrderTimeline (historial de cambios de estado)
│   │   └── Footer: "Avanzar Estado" / "Cancelar Pedido" buttons (solo si estado no es terminal)
│   └── └── [terminal state] → mensaje "Pedido en estado final"
├── ChangeStateModal (reuses <Modal>)
│   ├── Current estado display (OrderBadge)
│   ├── Valid Transitions dropdown (derivado de FSM)
│   ├── Motivo textarea (obligatorio si destino = CANCELADO, placeholder contextual)
│   └── Footer: Cancelar / Confirmar
```

## Data Flow

### Server State (TanStack Query)

- `useAdminOrders(filters)` — `useQuery` con `queryKey: ['admin-orders', params]` y `placeholderData: (prev) => prev`
- `useAdminOrder(id)` — `useQuery` con `queryKey: ['admin-order', id]`, `enabled: !!id` (carga diferida al abrir modal de detalle)
- `useChangeOrderState()` — `useMutation` que invalida `['admin-orders']` y `['admin-order', id]` al completar

### Client State (local `useState` — NO Zustand)

Siguiendo el patrón de `AdminUsersPage` que usa `useState` local. Los filtros no necesitan persistencia entre navegaciones.

```typescript
const [page, setPage] = useState(1);
const [orderIdFilter, setOrderIdFilter] = useState('');
const [clientNameFilter, setClientNameFilter] = useState('');
const [estadoFilter, setEstadoFilter] = useState('');
const [fechaInicio, setFechaInicio] = useState('');
const [fechaFin, setFechaFin] = useState('');
const [selectedOrderId, setSelectedOrderId] = useState<string | null>(null);
const [isDetailModalOpen, setIsDetailModalOpen] = useState(false);
const [isChangeStateModalOpen, setIsChangeStateModalOpen] = useState(false);
```

Todo cambio de filtro resetea `page` a 1.

### Debounce Strategy

Solo los inputs de texto (`orderIdFilter`, `clientNameFilter`) usan debounce de 300ms. Los selects y date inputs disparan la query inmediatamente.

```typescript
const [localOrderId, setLocalOrderId] = useState(orderIdFilter);
const [localClientName, setLocalClientName] = useState(clientNameFilter);

useEffect(() => {
  setLocalOrderId(orderIdFilter);
}, [orderIdFilter]);
useEffect(() => {
  setLocalClientName(clientNameFilter);
}, [clientNameFilter]);
```

El input muestra el valor local inmediatamente (UX reactiva), pero la query se dispara solo con el valor debounced.

### FSM Integration — How valid transitions are derived

El frontend NO hardcodea las transiciones. En su lugar, importa `TRANSITIONS` desde un módulo de constantes que refleja exactamente `pedidos/service.py`:

```typescript
// features/admin-orders/constants.ts
export const FSM_TRANSITIONS: Record<string, Record<string, { roles: string[] }>> = {
  PENDIENTE: { CANCELADO: { roles: ['CLIENT', 'ADMIN', 'PEDIDOS'] } },
  CONFIRMADO: {
    EN_PREPARACION: { roles: ['ADMIN', 'PEDIDOS'] },
    CANCELADO: { roles: ['CLIENT', 'ADMIN', 'PEDIDOS'] },
  },
  EN_PREPARACION: { EN_CAMINO: { roles: ['ADMIN', 'PEDIDOS'] }, CANCELADO: { roles: ['ADMIN'] } },
  EN_CAMINO: { ENTREGADO: { roles: ['ADMIN', 'PEDIDOS'] } },
  ENTREGADO: {},
  CANCELADO: {},
};

export const TERMINAL_STATES = ['ENTREGADO', 'CANCELADO'];

export function getValidTransitions(currentState: string, userRoles: string[]): string[] {
  const transitions = FSM_TRANSITIONS[currentState] || {};
  return Object.entries(transitions)
    .filter(([_, info]) => info.roles.some((r) => userRoles.includes(r)))
    .map(([target]) => target);
}
```

El dropdown del `ChangeStateModal` solo muestra las transiciones retornadas por `getValidTransitions(estado_actual, userRoles)`.

### Modal Flow

1. **Click en fila** → abre `OrderDetailModal` con `selectedOrderId`
2. `useAdminOrder(selectedOrderId)` carga el detalle (items + historial)
3. **Click "Avanzar Estado"** en el modal de detalle → cierra modal de detalle, abre `ChangeStateModal` con el mismo `selectedOrderId` y `estado_actual`
4. **Click "Cancelar Pedido"** en el modal de detalle → abre `ChangeStateModal` con `nuevo_estado` pre-seleccionado a "CANCELADO" y campo motivo obligatorio visible
5. **Confirmar cambio de estado** en `ChangeStateModal` → llama `changeStateMutation.mutateAsync()`, cierra modales, invalida queries
6. **Éxito** → toast "Estado actualizado correctamente"
7. **Error** → toast con mensaje de error (ej. "Transición no válida", "No tienes permisos")

Cuando un pedido está en estado terminal (`ENTREGADO` o `CANCELADO`), el `OrderDetailModal` no muestra los botones de acción y muestra un mensaje "Pedido en estado final".

## API Client Design (`shared/api/adminOrdersApi.ts`)

Siguiendo el patrón de `adminUsersApi.ts`:

```typescript
import client from './client';

// Match backend AdminOrderListItem schema
export interface AdminOrderItem {
  id: string;
  cliente_nombre: string | null;
  usuario_id: string;
  estado_codigo: string;
  total: number;
  created_at: string;
  direccion_calle: string | null;
}

// Match backend AdminOrderListResponse schema
export interface AdminOrderListResponse {
  items: AdminOrderItem[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

// Match backend AdminChangeStateRequest schema
export interface AdminChangeStateRequest {
  nuevo_estado: string;
  motivo?: string | null;
}

export interface AdminOrdersParams {
  page?: number;
  size?: number;
  estado_codigo?: string;
  fecha_inicio?: string;
  fecha_fin?: string;
  usuario_id?: string;
  monto_min?: number;
  monto_max?: number;
}

// GET /admin/pedidos
export async function fetchAdminOrders(params: AdminOrdersParams): Promise<AdminOrderListResponse>;

// GET /admin/pedidos/{id} — returns same PedidoDetail as client API (items + historial)
export async function fetchAdminOrder(id: string): Promise<PedidoDetail>;

// PATCH /admin/pedidos/{id}/estado
export async function changeOrderState(
  id: string,
  body: AdminChangeStateRequest
): Promise<PedidoListResponse>;
```

Nota: `fetchAdminOrder` retorna `PedidoDetail` (mismo tipo que el endpoint de cliente), ya que el backend retorna la misma estructura con items e historial. Se reutilizan los tipos de `pedidosApi.ts`.

## TanStack Query Hooks Design (`features/admin-orders/hooks/useAdminOrders.ts`)

```typescript
export function useAdminOrders(params: AdminOrdersParams) {
  return useQuery<AdminOrderListResponse>({
    queryKey: ['admin-orders', params],
    queryFn: () => fetchAdminOrders(params),
    placeholderData: (prev) => prev,
  });
}

export function useAdminOrder(id: string | null) {
  return useQuery<PedidoDetail>({
    queryKey: ['admin-order', id],
    queryFn: () => fetchAdminOrder(id!),
    enabled: !!id,
  });
}

export function useChangeOrderState() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, body }: { id: string; body: AdminChangeStateRequest }) =>
      changeOrderState(id, body),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: ['admin-orders'] });
      queryClient.invalidateQueries({ queryKey: ['admin-order', variables.id] });
      toast.success('Estado del pedido actualizado correctamente');
    },
    onError: (error: any) => {
      const msg = error?.response?.data?.detail || 'Error al cambiar el estado del pedido';
      toast.error(msg);
    },
  });
}
```

## Reuse vs Build Decisions

### REUSE (sin cambios)

- **`OrderBadge`** — perfecto para admin, soporta los 6 estados del FSM y tiene colores consistentes
- **`OrderTimeline`** — diseñado exactamente para el historial de pedidos con `TimelineEntry[]`, soporta estados futuros, CANCELADO, y badge "Actual"
- **`Modal`** — componente compartido genérico, usado para ambos modales (detail y change state)
- **`Card`**, **`Pagination`**, **`Skeleton`**, **`ErrorDisplay`**, **`EmptyState`**, **`Spinner`** — todos reutilizados sin modificaciones

### BUILD (componentes admin-specific nuevos)

- **`AdminOrderTable`** — NO reutiliza `OrderList` directamente porque:
  1. Usa `AdminOrderItem` (tiene `cliente_nombre` y `direccion_calle`) en lugar de `Order`
  2. Necesita hover preview con tooltip por fila (no existe en `OrderList`)
  3. Usa paginación `page`/`size`/`pages` (backend admin) en lugar de `skip`/`limit`
  4. El click abre un modal de detalle con acciones (no solo "Ver detalle")
- **`HoverPreview`** — tooltip que aparece al hacer hover sobre una fila, mostrando cliente, dirección y cantidad de items
- **`OrderDetailModal`** — modal admin-specific que extiende el concepto del `OrderDetail` de cliente con botones de acción "Avanzar Estado" y "Cancelar Pedido"
- **`ChangeStateModal`** — modal exclusivo del admin para transicionar estados con FSM validation y motivo requerido en cancelación

## Visual Design Decisions

### Hover Preview (Tooltip)

Al hacer hover en una fila de la tabla, se muestra un tooltip posicionado a la derecha de la fila con:

- **Cliente**: {cliente_nombre || "No registrado"}
- **Dirección**: {direccion_calle || "No especificada"}
- **Items**: {cantidad_items} (obtenido del detalle al hacer hover — se podría cargar on-demand o mostrar un placeholder)

Para mantenerlo simple y evitar una query por cada hover, el hover preview muestra solo los datos que ya vienen en `AdminOrderItem`: `cliente_nombre` y `direccion_calle`. La cantidad de items se omite del preview para evitar N+1 queries.

Implementación: CSS-only tooltip con `group-hover` y `absolute` positioning, o un `title` attribute simple.

### Estado Badges (via OrderBadge)

Ya definidos en `OrderBadge.tsx`:

- PENDIENTE: amber
- CONFIRMADO: blue
- EN_PREPARACION: indigo
- EN_CAMINO: purple
- ENTREGADO: green
- CANCELADO: red

### Estados Terminales Visuales

Cuando un pedido está en `ENTREGADO` o `CANCELADO`, la fila en la tabla puede tener un estilo sutilmente atenuado (`opacity-75`) y el modal de detalle oculta los botones de acción.

### Responsive

- Desktop (≥1024px): tabla completa con todas las columnas + filtros en fila horizontal
- Tablet (640–1023px): tabla con scroll horizontal, filtros en 2 columnas
- Mobile (<640px): tabla reducida (solo ID, Estado, Total), filtros stacked verticalmente, modal full-width

## File Structure

```
frontend/src/
├── shared/api/
│   └── adminOrdersApi.ts              ← NEW: API client + types for admin orders
├── features/
│   └── admin-orders/
│       ├── constants.ts               ← NEW: FSM transitions mirror, getValidTransitions()
│       ├── hooks/
│       │   └── useAdminOrders.ts      ← NEW: TanStack Query hooks
│       └── components/
│           ├── AdminOrderTable.tsx     ← NEW: admin-specific table with hover preview
│           ├── HoverPreview.tsx        ← NEW: tooltip component for row hover
│           ├── OrderDetailModal.tsx    ← NEW: detail modal with items + timeline + actions
│           └── ChangeStateModal.tsx    ← NEW: state change modal with FSM dropdown
└── pages/
    └── admin/
        └── AdminOrdersPage.tsx        ← REWRITE: full implementation replacing placeholder
```
