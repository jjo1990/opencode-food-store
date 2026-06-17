# Tasks: implement-notifications-and-feedback

## 1. Badge Component (shared)

- [ ] 1.1 Crear `frontend/src/shared/components/Badge.tsx` con props `variant` (success | warning | error | info | neutral), `size` (sm | md), `className`, `children`
- [ ] 1.2 Implementar color map por variant usando tokens del proyecto (green-100/800, amber-100/800, red-100/800, blue-100/800, gray-100/800)
- [ ] 1.3 Implementar size map: sm = `px-2 py-0.5 text-xs`, md = `px-3 py-1 text-sm`
- [ ] 1.4 Exportar Badge con named export + default export

## 2. Enhanced Shared Components

- [ ] 2.1 Agregar prop `size` ('sm' | 'md' | 'lg' | 'xl') a Modal con default 'lg' (`max-w-lg` actual)
- [ ] 2.2 Agregar transición de fade-in al overlay y panel de Modal (`transition-opacity`)
- [ ] 2.3 Agregar prop `size` ('sm' | 'md' | 'lg') a Button con default 'md' (padding actual)
- [ ] 2.4 Agregar prop `fullWidth` (boolean, default false) a Button → `w-full` cuando true
- [ ] 2.5 Agregar prop `icon` (ReactNode, optional) a EmptyState — renderiza icon en lugar del SVG default
- [ ] 2.6 Agregar prop `className` (string, default '') a EmptyState — aplicado al wrapper
- [ ] 2.7 Agregar prop `title` (string, default 'Algo salió mal') a ErrorDisplay
- [ ] 2.8 Agregar prop `count` (number, default 1) a Skeleton — renderiza N skeletons en `space-y-2`
- [ ] 2.9 Agregar prop `delay` (number en ms, default 0) a Skeleton — retrasa render con `useState` + `setTimeout`, retorna null durante el delay
- [ ] 2.10 Crear `frontend/src/shared/components/SkeletonTable.tsx` con props `columns` (default 4), `rows` (default 5), `className`
- [ ] 2.11 SkeletonTable: header row con bg-gray-50 + N columnas `h-10`, body con M filas alternando bg-white/bg-gray-50 + N columnas `h-6`
- [ ] 2.12 Crear `frontend/src/shared/components/SkeletonCard.tsx` con prop `className`: imagen `h-48`, título `h-5 w-3/4`, subtítulo `h-4 w-1/2`, botón `h-10 w-24`
- [ ] 2.13 Exportar SkeletonTable y SkeletonCard con named + default export

## 3. Confirmation Modal

- [ ] 3.1 Crear `frontend/src/shared/components/ConfirmationModal.tsx` usando Modal internamente
- [ ] 3.2 Props: `isOpen`, `onClose`, `onConfirm`, `title`, `message`, `confirmLabel` (default 'Confirmar'), `cancelLabel` (default 'Cancelar'), `variant` ('danger' | 'warning' | 'info', default 'info'), `isLoading` (default false)
- [ ] 3.3 Variant → botón confirmar: danger = `<Button variant="danger">`, warning = `<Button variant="secondary">`, info = `<Button variant="primary">`
- [ ] 3.4 Botón cancelar siempre `<Button variant="ghost">` con `onClick={onClose}`
- [ ] 3.5 Cuando `isLoading=true`: confirm button con `isLoading=true` + disabled, cancel button permanece habilitado
- [ ] 3.6 Pasar `children` como `<p>{message}</p>` al Modal
- [ ] 3.7 Pasar `footer` como el par de botones (cancelar + confirmar) al Modal
- [ ] 3.8 Exportar ConfirmationModal con named + default export

## 4. Enhanced Toast System

- [ ] 4.1 Crear `frontend/src/shared/hooks/useToastAsync.ts` con hook `useToastAsync()`
- [ ] 4.2 Implementar método `promise<T>(promise, messages, options?)` que llama `toast.promise()`
- [ ] 4.3 `messages.success` y `messages.error` aceptan `string | ((data: T) => string)` para mensajes dinámicos
- [ ] 4.4 Agregar métodos `info(message: string)` y `warning(message: string)` a `useToast.ts`
- [ ] 4.5 `info()` usa `toast(message, { icon: 'ℹ️' })`, `warning()` usa `toast(message, { icon: '⚠️' })`
- [ ] 4.6 Agregar estilos `info` y `warning` en `toastOptions` del `<Toaster>` en `app/providers.tsx`:
  - `info`: `{ duration: 5000, style: { background: '#1e40af', color: '#fff' } }`
  - `warning`: `{ duration: 5000, style: { background: '#d97706', color: '#fff' } }`
- [ ] 4.7 Eliminar `frontend/src/shared/components/ToastContainer.tsx` (código muerto)

## 5. Apply Badge Component (replace duplications)

- [ ] 5.1 AdminUsersPage: reemplazar `ROLE_BADGE` + spans inline → `<Badge variant={...} size="sm">{role}</Badge>`
- [ ] 5.2 AdminUsersPage: reemplazar `renderStatusBadge` spans inline → `<Badge variant={...} size="sm">`
- [ ] 5.3 AdminUsersPage: eliminar constante `ROLE_BADGE` y funciones helper `renderRoleBadges`/`renderStatusBadge` (inline el Badge directamente)
- [ ] 5.4 AdminProductosPage: reemplazar badges de disponibilidad inline → `<Badge variant={...} size="sm">`
- [ ] 5.5 AdminIngredientesPage: reemplazar badges de alérgenos inline → `<Badge variant={...} size="sm">`
- [ ] 5.6 AdminCategoriasPage: reemplazar badges de estado inline → `<Badge variant={...} size="sm">`

## 6. Apply Confirmation Modals

- [ ] 6.1 AdminOrdersPage: agregar `ConfirmationModal` antes de cancelar pedido (variant danger)
- [ ] 6.2 Revisar AdminUsersPage, AdminProductosPage, AdminIngredientesPage, AdminCategoriasPage — agregar ConfirmationModal donde haya acciones destructivas sin confirmación (ej: eliminar/desactivar)
- [ ] 6.3 Cada confirmación debe mostrar mensaje descriptivo de la acción y su irreversibilidad

## 7. Apply Skeleton Patterns

- [ ] 7.1 AdminUsersPage: reemplazar array de `<Skeleton>` inline en estado loading → `<SkeletonTable columns={...} rows={...} />`
- [ ] 7.2 AdminOrdersPage: reemplazar array de `<Skeleton>` inline en estado loading → `<SkeletonTable />`
- [ ] 7.3 Revisar otras páginas admin (productos, ingredientes, categorías) y usar SkeletonTable donde tengan skeletons de tabla inline

## 8. Verification

- [ ] 8.1 Ejecutar `npx tsc --noEmit` en `frontend/` — cero errores de TypeScript
- [ ] 8.2 Verificar que `Badge` renderiza correctamente los 5 variants × 2 sizes (10 combinaciones)
- [ ] 8.3 Verificar que `ConfirmationModal` muestra botones correctos por variant y dispara `onConfirm`/`onClose`
- [ ] 8.4 Verificar que `ConfirmationModal` en estado loading deshabilita confirmar pero no cancelar
- [ ] 8.5 Verificar que `toast.promise()` vía `useToastAsync` muestra estados loading/success/error
- [ ] 8.6 Verificar que `useToast.info()` y `useToast.warning()` muestran toasts con íconos correctos
- [ ] 8.7 Verificar que `SkeletonTable` renderiza N×M celdas con estructura de tabla
- [ ] 8.8 Verificar que `SkeletonCard` renderiza imagen + texto + botón placeholder
- [ ] 8.9 Verificar que `Skeleton delay={200}` no aparece antes de 200ms
- [ ] 8.10 Verificar que `Modal size="xl"` tiene max-w-xl, `Button size="sm"` tiene padding reducido, `Button fullWidth` tiene w-full
- [ ] 8.11 Verificar que `EmptyState icon={...}` usa ícono custom, `ErrorDisplay title="..."` muestra título custom
- [ ] 8.12 Verificar FSD: ningún archivo en `shared/` importa de `pages/`, `features/`, o `entities/`
- [ ] 8.13 Verificar que `ToastContainer.tsx` fue eliminado y ningún archivo lo importa
- [ ] 8.14 Verificar que las 4 páginas admin (users, productos, ingredientes, categorías) usan `<Badge>` y renderizan igual que antes
- [ ] 8.15 Verificar que AdminOrdersPage muestra confirmación antes de cancelar pedido y la acción solo se ejecuta tras confirmar
