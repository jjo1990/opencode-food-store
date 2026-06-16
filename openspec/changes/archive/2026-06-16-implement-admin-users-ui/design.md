## Component Tree

```
AdminUsersPage
├── Header (title + description)
├── Filters Bar
│   ├── SearchInput (debounced, by name/email)
│   ├── RoleSelect (multi-checkbox dropdown or select)
│   └── StatusSelect (Activo / Inactivo / Todos)
├── Content Area (handles 4 states: loading → error → empty → data)
│   ├── [loading] → <Skeleton variant="table" rows={8} />
│   ├── [error]   → <ErrorDisplay message={...} onRetry={refetch} />
│   ├── [empty]   → <EmptyState title="Sin usuarios" description="No se encontraron usuarios con esos filtros." />
│   └── [data]    → UsersTable
│       ├── <thead> column headers
│       └── <tbody> rows
│           └── UserRow (click → open EditUserModal)
│               ├── ID (truncated UUID)
│               ├── Nombre
│               ├── Email
│               ├── Badges de roles (colored pills)
│               ├── Estado badge (Activo=green / Inactivo=red)
│               └── Fecha creación
├── Pagination ("Mostrando X–Y de Z", Anterior / Siguiente)
├── EditUserModal (reuses <Modal>)
│   ├── full_name input
│   ├── email input
│   ├── telefono input
│   ├── Roles checkboxes (CLIENT, STOCK, PEDIDOS, ADMIN)
│   ├── Activo toggle switch
│   └── Footer: Cancelar / Guardar
├── DeactivateConfirmModal
│   └── "¿Desactivar usuario X? Podrá ser reactivado." → Confirmar / Cancelar
└── ReactivateConfirmModal
    └── "¿Reactivar usuario X?" → Confirmar / Cancelar
```

## Data Flow

### Server State (TanStack Query)

- `useAdminUsers(filters)` — `useQuery` con `queryKey: ['admin-users', filters]` y `placeholderData: (prev) => prev`
- `useAdminUser(id)` — `useQuery` con `queryKey: ['admin-user', id]`, `enabled: !!id` (carga diferida al abrir modal)
- `useUpdateUser()` — `useMutation` que invalida `['admin-users']` y `['admin-user', id]` al completar
- `useDeactivateUser()` — `useMutation` que invalida `['admin-users']`
- `useReactivateUser()` — `useMutation` que invalida `['admin-users']`

### Client State (local `useState` — NO Zustand)

Siguiendo el patrón de `AdminProductosPage` que usa `useState` local. Los filtros no necesitan persistencia entre navegaciones para este panel.

```typescript
const [page, setPage] = useState(1);
const [search, setSearch] = useState('');
const [rol, setRol] = useState<string>('');
const [estado, setEstado] = useState<string>('activo');
const [selectedUserId, setSelectedUserId] = useState<string | null>(null);
const [isEditModalOpen, setIsEditModalOpen] = useState(false);
const [isDeactivateModalOpen, setIsDeactivateModalOpen] = useState(false);
const [isReactivateModalOpen, setIsReactivateModalOpen] = useState(false);
```

Todo cambio de filtro resetea `page` a 1.

### Debounce Strategy

Search usa el patrón establecido en el frontend-design skill: `useState` local + `useEffect` con `setTimeout` de 300ms.

```typescript
const [localSearch, setLocalSearch] = useState(search);
useEffect(() => {
  setLocalSearch(search);
}, [search]);

const debouncedSearch = useCallback(
  (() => {
    let timer: ReturnType<typeof setTimeout>;
    return (value: string) => {
      clearTimeout(timer);
      timer = setTimeout(() => {
        setSearch(value);
        setPage(1);
      }, 300);
    };
  })(),
  []
);
```

El input muestra `localSearch` inmediatamente (UX reactiva), pero la query se dispara solo con `search` (300ms después del último keystroke).

## Modal Architecture

### EditUserModal

- Se abre al hacer click en una fila de la tabla
- `selectedUserId` se setea → dispara `useAdminUser(selectedUserId)` con `enabled: !!selectedUserId`
- Mientras carga el detalle (`isLoading`), muestra `<Spinner />` dentro del modal
- Si error, muestra mensaje y botón Reintentar
- Una vez cargado, rellena el formulario con los datos
- Al submit: arma `AdminUserUpdateRequest` solo con campos modificados (todos optional según schema backend), llama `updateUser.mutateAsync()`
- Si éxito: cierra modal, muestra toast, invalidate queries
- Si error: muestra toast de error, mantiene modal abierto

### Role Removal Confirmation (CRÍTICO)

Si el usuario que se está editando tiene rol ADMIN y se desmarca el checkbox ADMIN:

1. NO se envía el PUT inmediatamente
2. Se muestra un mini-modal o overlay de confirmación dentro del modal: "¿Estás seguro? Si quitás el rol ADMIN, este usuario perderá acceso al panel de administración."
3. Solo si confirma, se envía el PUT con los roles actualizados
4. Si cancela, se restaura el checkbox ADMIN a marcado

### Deactivate Confirmation

- Botón "Desactivar usuario" en el footer del modal de edición o como acción en la fila
- Abre `DeactivateConfirmModal` con mensaje explicativo
- Al confirmar, llama `deactivateUser.mutateAsync(selectedUserId)`
- Éxito: cierra modales, invalida queries

### Reactivate Confirmation

- Solo visible si el usuario está soft-deleted
- Mismo flujo que deactivate pero con `reactivateUser.mutateAsync(selectedUserId)`

## API Client Design (`shared/api/adminUsersApi.ts`)

Siguiendo el patrón de `adminCatalogApi.ts`:

```typescript
import client from './client';

export interface AdminUserResponse {
  id: string;
  email: string;
  full_name: string | null;
  telefono: string | null;
  roles: string[];
  activo: boolean;
  created_at: string;
  soft_deleted_at: string | null;
}

export interface AdminUserListResponse {
  items: AdminUserResponse[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface AdminUserUpdateRequest {
  full_name?: string | null;
  email?: string | null;
  telefono?: string | null;
  roles?: string[];
}

export interface AdminUsersParams {
  page?: number;
  size?: number;
  rol?: string;
  search?: string;
  estado?: string;
}

export async function fetchAdminUsers(params: AdminUsersParams): Promise<AdminUserListResponse>;
export async function fetchAdminUser(id: string): Promise<AdminUserResponse>;
export async function updateAdminUser(
  id: string,
  body: AdminUserUpdateRequest
): Promise<AdminUserResponse>;
export async function deactivateAdminUser(id: string): Promise<{ message: string }>;
export async function reactivateAdminUser(id: string): Promise<AdminUserResponse>;
```

## TanStack Query Hooks Design (`features/admin-users/hooks/useAdminUsers.ts`)

```typescript
export function useAdminUsers(params: AdminUsersParams) {
  return useQuery<AdminUserListResponse>({
    queryKey: ['admin-users', params],
    queryFn: () => fetchAdminUsers(params),
    placeholderData: (prev) => prev,
  });
}

export function useAdminUser(id: string | null) {
  return useQuery<AdminUserResponse>({
    queryKey: ['admin-user', id],
    queryFn: () => fetchAdminUser(id!),
    enabled: !!id,
  });
}

export function useUpdateUser() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, body }: { id: string; body: AdminUserUpdateRequest }) =>
      updateAdminUser(id, body),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-users'] });
      toast.success('Usuario actualizado correctamente');
    },
    onError: () => {
      toast.error('Error al actualizar usuario');
    },
  });
}

// Similar pattern for useDeactivateUser and useReactivateUser
```

## Visual Design Decisions

### Role Badges (colored pills)

- **ADMIN**: bg-red-100 text-red-800 (rol más sensible, color de advertencia)
- **STOCK**: bg-blue-100 text-blue-800
- **PEDIDOS**: bg-yellow-100 text-yellow-800
- **CLIENT**: bg-green-100 text-green-800

### Estado Badge

- **Activo**: bg-green-100 text-green-800
- **Inactivo**: bg-red-100 text-red-800

### Soft-deleted Users

- Fila con `bg-gray-50`, texto `text-gray-400`
- Nombre con `line-through`
- Estado badge adicional "Eliminado" en gris
- Al hacer click, solo permite Reactivar (no editar)

### Responsive

- En mobile (≤640px): tabla horizontal scroll, columnas reducidas (solo Nombre, Email, Estado)
- Modal: `max-w-lg` en desktop, `max-w-full` en mobile

## File Structure

```
frontend/src/
├── shared/api/
│   └── adminUsersApi.ts          ← NEW: API client + types
├── features/
│   └── admin-users/
│       └── hooks/
│           └── useAdminUsers.ts  ← NEW: TanStack Query hooks
└── pages/
    └── admin/
        ├── AdminUsersPage.tsx    ← REWRITE: full implementation
        └── EditUserModal.tsx     ← NEW: edit modal component
```
