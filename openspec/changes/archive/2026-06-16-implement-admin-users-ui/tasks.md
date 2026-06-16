# Tasks: implement-admin-users-ui

## 1. API Client — Admin Users

- [x] 1.1 Create `frontend/src/shared/api/adminUsersApi.ts`
  - [x] 1.1.1 Define TypeScript interfaces: `AdminUserResponse`, `AdminUserListResponse`, `AdminUserUpdateRequest`, `AdminUsersParams`
  - [x] 1.1.2 Implement `fetchAdminUsers(params)` — GET `/admin/usuarios` with query params (page, size, rol, search, estado)
  - [x] 1.1.3 Implement `fetchAdminUser(id)` — GET `/admin/usuarios/{id}`
  - [x] 1.1.4 Implement `updateAdminUser(id, body)` — PUT `/admin/usuarios/{id}`
  - [x] 1.1.5 Implement `deactivateAdminUser(id)` — DELETE `/admin/usuarios/{id}`
  - [x] 1.1.6 Implement `reactivateAdminUser(id)` — PATCH `/admin/usuarios/{id}/reactivar`

## 2. TanStack Query Hooks

- [x] 2.1 Create `frontend/src/features/admin-users/hooks/useAdminUsers.ts`
  - [x] 2.1.1 Implement `useAdminUsers(params)` — useQuery with `['admin-users', params]`, `placeholderData: (prev) => prev`
  - [x] 2.1.2 Implement `useAdminUser(id)` — useQuery with `['admin-user', id]`, `enabled: !!id`
  - [x] 2.1.3 Implement `useUpdateAdminUser()` — useMutation, invalidates `['admin-users']` and `['admin-user', id]`, toast success/error
  - [x] 2.1.4 Implement `useDeleteAdminUser()` — useMutation, invalidates `['admin-users']`, toast success/error
  - [x] 2.1.5 Implement `useReactivateAdminUser()` — useMutation, invalidates `['admin-users']`, toast success/error

## 3. AdminUsersPage — Table, Filters, Pagination

- [x] 3.1 Rewrite `frontend/src/pages/admin/AdminUsersPage.tsx` (replace placeholder)
  - [x] 3.1.1 Add header: "Gestión de Usuarios" + description
  - [x] 3.1.2 Add search input with debounce (localState + 300ms setTimeout + reset page to 1)
  - [x] 3.1.3 Add role filter select: "Todos los roles", "ADMIN", "STOCK", "PEDIDOS", "CLIENT"
  - [x] 3.1.4 Add estado filter select: "Activos" (default), "Inactivos", "Todos"
  - [x] 3.1.5 Build params object from filter state, pass to `useAdminUsers(params)`
  - [x] 3.1.6 Handle loading state: render `<Skeleton />` with table-like layout (8 rows)
  - [x] 3.1.7 Handle error state: render `<ErrorDisplay />` with retry
  - [x] 3.1.8 Handle empty state: render `<EmptyState />` with context-appropriate message
  - [x] 3.1.9 Handle data state: render table with columns (ID truncated, Nombre, Email, Roles badges, Estado badge, Fecha)
  - [x] 3.1.10 Role badges with color mapping: ADMIN=red, STOCK=blue, PEDIDOS=orange, CLIENT=green
  - [x] 3.1.11 Estado badge: Activo=green, Inactivo=red, Eliminado=gray
  - [x] 3.1.12 Soft-deleted users: gray row (`bg-gray-50`), line-through name, gray text, extra "Eliminado" badge
  - [x] 3.1.13 Click on active user row: open EditUserModal with selectedUserId
  - [x] 3.1.14 Click on soft-deleted user row: open ReactivateConfirmModal
  - [x] 3.1.15 Pagination controls: "Mostrando X–Y de Z", Anterior / Siguiente buttons

## 4. UserEditModal (created at `features/admin-users/components/UserEditModal.tsx`)

- [x] 4.1 Create `frontend/src/features/admin-users/components/UserEditModal.tsx`
  - [x] 4.1.1 Define props: `isOpen`, `onClose`, `userId`
  - [x] 4.1.2 Fetch user detail with `useAdminUser(userId)` inside modal
  - [x] 4.1.3 Loading state inside modal: `<Spinner />`
  - [x] 4.1.4 Error state inside modal: error message + Retry button
  - [x] 4.1.5 Form with local state initialized from user data: `fullName`, `email`, `telefono`, `roles: string[]`, `activo: boolean`
  - [x] 4.1.6 Fields: full_name (text input), email (email input), telefono (text input)
  - [x] 4.1.7 Roles: checkboxes for CLIENT, STOCK, PEDIDOS, ADMIN
  - [x] 4.1.8 Role removal confirmation: if ADMIN checkbox was checked and gets unchecked, show inline confirmation with Confirm/Cancel
  - [x] 4.1.9 Activo toggle switch
  - [x] 4.1.10 "Desactivar usuario" button in footer → opens DeactivateConfirmModal
  - [x] 4.1.11 "Guardar cambios" button: build `AdminUserUpdateRequest` (only changed fields), call `updateMutation.mutateAsync()`
  - [x] 4.1.12 On success: close modal, show toast (via mutation onSuccess)
  - [x] 4.1.13 On error: show error toast, keep modal open (via mutation onError)
  - [x] 4.1.14 "Cancelar" button: close modal without saving
  - [x] 4.1.15 Disable "Guardar cambios" if no changes detected (hasChanges check)
  - [x] 4.1.16 Close modal on Escape key (handled by shared Modal)

## 5. Confirmation Modals

- [x] 5.1 Role removal inline confirmation (inside UserEditModal)
  - [x] 5.1.1 Detect when ADMIN role checkbox transitions from checked to unchecked
  - [x] 5.1.2 Show inline warning message: "¿Estás seguro? Si quitás el rol ADMIN, este usuario perderá acceso al panel de administración."
  - [x] 5.1.3 "Confirmar" → hide warning, keep ADMIN unchecked, allow save
  - [x] 5.1.4 "Cancelar" → restore ADMIN checkbox to checked, hide warning

- [x] 5.2 DeactivateConfirmModal (inline in AdminUsersPage + inside UserEditModal footer)
  - [x] 5.2.1 Reuse shared `<Modal>` component
  - [x] 5.2.2 Message: "¿Desactivar a {nombre}? El usuario no podrá acceder al sistema pero sus datos se conservarán."
  - [x] 5.2.3 "Confirmar" → call `deleteMutation.mutateAsync(userId)`, on success close all modals + toast
  - [x] 5.2.4 "Cancelar" → close confirmation

- [x] 5.3 ReactivateConfirmModal (inline in AdminUsersPage)
  - [x] 5.3.1 Reuse shared `<Modal>` component
  - [x] 5.3.2 Message: "¿Reactivar a {nombre}? El usuario recuperará el acceso al sistema."
  - [x] 5.3.3 "Confirmar" → call `reactivateMutation.mutateAsync(userId)`, on success close modal + toast
  - [x] 5.3.4 "Cancelar" → close confirmation modal

## 6. Verification

- [x] 6.1 TypeScript type-check passes: `npx tsc --noEmit` (frontend directory) — 0 errors
- [ ] 6.2 Manual smoke test checklist (requires backend running):
  - [ ] Load page → shows users table with pagination
  - [ ] Search with debounce → filters correctly, page resets
  - [ ] Filter by role → filters correctly
  - [ ] Filter by estado → filters correctly
  - [ ] Click active user → opens EditUserModal with populated fields
  - [ ] Edit fields and save → API called, table updates, toast shown
  - [ ] Cancel edit → no API call, modal closes
  - [ ] Remove ADMIN role → confirmation appears, confirm saves, cancel restores
  - [ ] Deactivate user → confirmation appears, confirm deletes, table updates
  - [ ] Reactivate soft-deleted user → confirmation appears, confirm reactivates
  - [ ] Loading state → skeleton shown
  - [ ] Error state → error message with retry shown
  - [ ] Empty state (no results) → empty message shown
  - [ ] Soft-deleted users → gray row styling applied
  - [ ] Pagination → next/previous navigates pages, "Mostrando X–Y de Z" updates
