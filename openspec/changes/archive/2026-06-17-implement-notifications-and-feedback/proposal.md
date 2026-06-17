## Why

La UX actual de Food Store carece de un sistema de feedback consistente. Los badges de estado y rol se duplican en cada página con estilos inline repetidos. No existe `toast.promise()` para flujos asíncronos — los mutations muestran toasts manualmente con `loading()` + `dismissLoading()` + `success()`/`error()`. Los componentes compartidos (`Modal`, `Button`, `EmptyState`, `ErrorDisplay`, `Skeleton`) no tienen variantes de tamaño ni props de extensión. No hay modales de confirmación estandarizados para acciones destructivas (cancelar pedido, eliminar, desactivar usuario). Estos problemas generan código duplicado, UX inconsistente, y riesgo de acciones irreversibles sin confirmación.

## What Changes

- **Nuevo `Badge` genérico** en `shared/components/Badge.tsx` — unifica todos los badges inline duplicados en páginas admin con variantes semánticas (`success`, `warning`, `error`, `info`, `neutral`) y tamaños (`sm`, `md`)
- **Refactor de badges duplicados** — AdminUsersPage (roles + estado), AdminProductosPage (disponibilidad), AdminIngredientesPage (alérgenos), AdminCategoriasPage (estado) migran a `<Badge>`
- **Nuevo `ConfirmationModal`** en `shared/components/ConfirmationModal.tsx` — envuelve `Modal` con título, mensaje, botones confirmar/cancelar, variante visual (`danger`, `warning`, `info`), y estado de carga
- **Confirmaciones en acciones destructivas** — AdminOrdersPage (cancelar pedido) y cualquier otra acción destructiva encontrada
- **Mejoras a componentes existentes** — `Modal` (+`size` prop, transición de opacidad), `Button` (+`size`, +`fullWidth`), `EmptyState` (+`icon`, +`className`), `ErrorDisplay` (+`title`), `Skeleton` (+`count`, +`delay`)
- **Nuevo `SkeletonTable` y `SkeletonCard`** — patrones de skeleton reutilizables para tablas y cards
- **Nuevo `useToastAsync` hook** — wrapper de `toast.promise()` para flujos asíncronos con estados loading/success/error
- **Extensión de `useToast`** — agrega métodos `info()` y `warning()` al hook existente
- **Configuración de `Toaster`** — agrega estilos para tipos custom (`info`, `warning`) en `app/providers.tsx`
- **Eliminación de `ToastContainer.tsx`** — código muerto, el `<Toaster>` ya está en `app/providers.tsx`

## Capabilities

### New Capabilities

- `ui-feedback`: Sistema centralizado de feedback visual para el usuario. Incluye Badge genérico con variantes semánticas, ConfirmationModal para acciones destructivas, SkeletonTable/SkeletonCard para estados de carga, useToastAsync para flujos asíncronos con toast.promise(), y mejoras de extensibilidad en todos los componentes compartidos.

### Modified Capabilities

<!-- Los componentes compartidos existentes reciben nuevas props pero mantienen compatibilidad hacia atrás -->

## Impact

- **Frontend**: `shared/components/Badge.tsx` (nuevo), `shared/components/ConfirmationModal.tsx` (nuevo), `shared/components/SkeletonTable.tsx` (nuevo), `shared/components/SkeletonCard.tsx` (nuevo), `shared/components/Modal.tsx` (modificado), `shared/components/Button.tsx` (modificado), `shared/components/EmptyState.tsx` (modificado), `shared/components/ErrorDisplay.tsx` (modificado), `shared/components/Skeleton.tsx` (modificado), `shared/hooks/useToast.ts` (modificado), `shared/hooks/useToastAsync.ts` (nuevo), `shared/components/ToastContainer.tsx` (eliminado), `app/providers.tsx` (modificado), `pages/admin/AdminUsersPage.tsx` (refactor badges), `pages/admin/AdminProductosPage.tsx` (refactor badges), `pages/admin/AdminIngredientesPage.tsx` (refactor badges), `pages/admin/AdminCategoriasPage.tsx` (refactor badges), `pages/admin/AdminOrdersPage.tsx` (confirmación cancelar)
- **Backend**: Sin cambios
- **Base de datos**: Sin cambios
- **Dependencias**: `react-hot-toast` v2.6.0 ya instalado. Ninguna dependencia nueva.
- **Seguridad**: Sin impacto. Las confirmaciones son puramente frontend.
