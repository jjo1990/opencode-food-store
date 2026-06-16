## Why

El panel de administración tiene los endpoints REST de gestión de usuarios funcionando desde Change 37 (`implement-admin-users-management`) y la navegación ya redirige a `/admin/users`, pero la página `AdminUsersPage` es un placeholder que solo muestra "Próximamente". Los administradores necesitan una UI completa para buscar, filtrar, editar, desactivar y reactivar usuarios sin tocar la base de datos. Completar esta UI desbloquea la gestión operativa diaria del panel admin.

## What Changes

- Crear `shared/api/adminUsersApi.ts` con tipos TypeScript y funciones fetch para los 5 endpoints (`GET /admin/usuarios`, `GET /admin/usuarios/{id}`, `PUT /admin/usuarios/{id}`, `DELETE /admin/usuarios/{id}`, `PATCH /admin/usuarios/{id}/reactivar`)
- Crear `features/admin-users/hooks/useAdminUsers.ts` con TanStack Query hooks (`useAdminUsers`, `useAdminUser`, `useUpdateUser`, `useDeactivateUser`, `useReactivateUser`)
- Reemplazar el placeholder `AdminUsersPage.tsx` con tabla completa: columnas ID/Nombre/Email/Roles(badges)/Estado/Registro, búsqueda con debounce por nombre/email, filtros por rol y estado, paginación
- Crear modal de edición (`EditUserModal.tsx`) reutilizando el componente `Modal` compartido: campos full_name, email, telefono, checkboxes de roles (CLIENT/STOCK/PEDIDOS/ADMIN), toggle activo/inactivo, botones Guardar/Cancelar
- Confirmación crítica al quitar rol ADMIN: modal de confirmación adicional antes de enviar el PUT
- Confirmación para soft-delete (desactivar) y reactivar usuario
- Estilo visual consistente con `AdminProductosPage.tsx`: filas de usuarios soft-deleted en gris, badges de roles con colores, estados loading/error/empty

## Capabilities

### New Capabilities

- `admin-users`: Interfaz de gestión de usuarios en el panel de administración — tabla paginada con búsqueda, filtros, modal de edición, confirmaciones para acciones críticas, y estados visuales para usuarios activos/inactivos/eliminados.

### Modified Capabilities

<!-- None — this is a new frontend UI. No existing spec requirements change. -->

## Impact

- **Código afectado**: Solo frontend (no requiere cambios en backend)
  - `frontend/src/shared/api/adminUsersApi.ts` — nuevo
  - `frontend/src/features/admin-users/hooks/useAdminUsers.ts` — nuevo
  - `frontend/src/pages/admin/AdminUsersPage.tsx` — reescritura completa
  - `frontend/src/pages/admin/EditUserModal.tsx` — nuevo
- **APIs consumidas**: `/api/v1/admin/usuarios/*` (ya existentes, sin cambios)
- **Dependencias**: `implement-admin-users-management` (backend completado), `implement-admin-dashboard-ui` (dashboard y layout admin completados)
- **Componentes compartidos reutilizados**: `Modal`, `Skeleton`, `ErrorDisplay`, `EmptyState`
