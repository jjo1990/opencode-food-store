## Context

Food Store tiene un sistema de componentes compartidos en `frontend/src/shared/components/` (`Button`, `Modal`, `Skeleton`, `EmptyState`, `ErrorDisplay`, `OrderBadge`, etc.) y un hook `useToast` en `shared/hooks/`. `react-hot-toast` v2.6.0 ya está instalado y configurado con `<Toaster>` en `app/providers.tsx`. Las páginas admin usan badges inline con clases Tailwind repetidas para roles, estados, disponibilidad, alérgenos y categorías. El `ToastContainer.tsx` es código muerto — el `<Toaster>` ya vive en `app/providers.tsx`.

**Restricciones existentes:**

- FSD estricto: `pages → features → entities → shared` (nunca al revés)
- TypeScript `strict: true`, no se permite `any`
- Solo Tailwind CSS, sin CSS modules
- Componentes compartidos exportan con nombre y default
- `Modal` actual usa `createPortal` con escape key y click-outside
- `OrderBadge` existe pero solo cubre estados de pedido (6 variantes hardcodeadas)
- `useToast` hook ofrece `success()`, `error()`, `loading()`, `dismiss()`, `dismissLoading()`
- Las páginas admin importan desde `../../shared/components/` (rutas relativas)
- `react-hot-toast` ya tiene `Toaster` configurado en `app/providers.tsx:20` con `position="top-right"` y estilos base

**Lo que NO existe:**

- Badge genérico reutilizable para rol/estado/disponibilidad/alérgeno
- `ConfirmationModal` estandarizado
- `toast.promise()` wrapper
- Props `size` en Modal y Button
- Props `icon`/`className` en EmptyState, `title` en ErrorDisplay, `count`/`delay` en Skeleton
- `SkeletonTable` y `SkeletonCard`

## Goals / Non-Goals

**Goals:**

- Crear `Badge` genérico como reemplazo directo de todos los badges inline duplicados
- Agregar `ConfirmationModal` para estandarizar confirmaciones de acciones destructivas
- Extender componentes existentes con props de extensibilidad (`size`, `fullWidth`, `icon`, `title`, `count`, `delay`, `className`)
- Crear `SkeletonTable` y `SkeletonCard` como patrones reutilizables
- Implementar `useToastAsync` con `toast.promise()`
- Extender `useToast` con métodos `info()` y `warning()`
- Eliminar `ToastContainer.tsx` (código muerto)
- Aplicar Badge en las 4 páginas admin que tienen badges inline
- Agregar confirmación a cancelar pedido en AdminOrdersPage

**Non-Goals:**

- No modificar `OrderBadge` (específico de pedidos, se mantiene para estados FSM)
- No crear sistema de notificaciones push/browser
- No modificar el interceptor de Axios (ya muestra toasts para errores HTTP)
- No tests automatizados en este change
- No cambios en backend
- No animaciones complejas — solo transiciones CSS con Tailwind
- No internacionalización de textos de badges

## Decisions

### 1. Badge Genérico en `shared/components/`

**Decision:**

```ts
interface BadgeProps {
  variant: 'success' | 'warning' | 'error' | 'info' | 'neutral';
  size?: 'sm' | 'md';
  children: ReactNode;
  className?: string;
}
```

Mapeo de colores usando tokens del proyecto:
| variant  | bg            | text          |
| -------- | ------------- | ------------- |
| success  | bg-green-100  | text-green-800  |
| warning  | bg-amber-100  | text-amber-800  |
| error    | bg-red-100    | text-red-800    |
| info     | bg-blue-100   | text-blue-800   |
| neutral  | bg-gray-100   | text-gray-800   |

**Rationale**: Cinco variantes semánticas cubren todos los casos de uso actuales: success (Activo, Disponible, Entregado), warning (Pendiente, En Preparación), error (Cancelado, Inactivo, Eliminado, contiene alérgenos), info (Stock, PEDIDOS, En Camino), neutral (Sin estado). La nomenclatura es semántica, no atada a dominios específicos. Las clases base son idénticas a los badges inline actuales: `inline-flex items-center rounded-full font-medium`.

**Tamaños**: `sm` = `px-2 py-0.5 text-xs` (igual que badges actuales), `md` = `px-3 py-1 text-sm` (para badges más visibles).

**Alternativa considerada**: Usar `OrderBadge` como base y extenderlo. Rechazada — `OrderBadge` está acoplado a los 6 estados FSM de pedido con labels hardcodeados. Un Badge genérico con `children` es más flexible y no rompe el componente existente.

### 2. ConfirmationModal Envuelve Modal Existente

**Decision:**

```ts
interface ConfirmationModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  title: string;
  message: string;
  confirmLabel?: string;
  cancelLabel?: string;
  variant?: 'danger' | 'warning' | 'info';
  isLoading?: boolean;
}
```

`ConfirmationModal` usa `Modal` internamente pasando `title`, `isOpen`, `onClose`, `children` (el mensaje), y `footer` (los botones).

**Botones por variante**:
- `danger`: Botón "Confirmar" rojo (`variant="danger"`), Botón "Cancelar" ghost
- `warning`: Botón "Confirmar" secondary (borde primary), Botón "Cancelar" ghost
- `info`: Botón "Confirmar" primary, Botón "Cancelar" ghost

Cuando `isLoading=true`, el botón de confirmar muestra spinner y está deshabilitado.

**Rationale**: Componer en vez de duplicar. `Modal` ya maneja portal, escape key, click-outside y overflow del body. `ConfirmationModal` solo agrega la capa semántica de "acción a confirmar". Esto sigue el patrón de composición sobre herencia.

**Alternativa considerada**: Agregar props `onConfirm`, `confirmLabel`, etc. directamente a `Modal`. Rechazada — `Modal` es un componente de presentación genérico. Acoplarlo a "confirmación" viola SRP y fuerza a todos los usos de Modal a cargar con props que no usan.

### 3. Mejoras a Componentes Existentes — Compatibilidad Hacia Atrás

**Decision**: Todos los nuevos props son opcionales con defaults que mantienen el comportamiento actual. Cero breaking changes.

**Modal**:
- `size?: 'sm' | 'md' | 'lg' | 'xl'` (default: `'lg'` → `max-w-lg` actual)
  - `sm` = `max-w-sm`, `md` = `max-w-md`, `lg` = `max-w-lg`, `xl` = `max-w-xl`
- El overlay ya tiene `transition-opacity`, el panel tiene `transition-all`. Se agrega `opacity-0` inicial con `opacity-100` al abrir para animación de fade-in.

**Button**:
- `size?: 'sm' | 'md' | 'lg'` (default: `'md'` → padding actual)
  - `sm` = `px-3 py-1.5 text-xs`, `md` = `px-4 py-2 text-sm`, `lg` = `px-6 py-3 text-base`
- `fullWidth?: boolean` (default: `false`) → agrega `w-full` cuando true

**EmptyState**:
- `icon?: ReactNode` (default: ícono de bandeja actual) — permite personalizar el ícono SVG
- `className?: string` (default: `''`) — aplicado al wrapper para extensión

**ErrorDisplay**:
- `title?: string` (default: `'Algo salió mal'`) — permite título personalizado

**Skeleton**:
- `count?: number` (default: `1`) — renderiza N skeletons iguales en un contenedor con `space-y-2`
- `delay?: number` (default: `0`) — usa `setTimeout` + estado local para retrasar la aparición en ms, evita flash en cargas rápidas (< 200ms)
  - Mientras está en delay, retorna `null`. Usa `useEffect` + `useState` para el timer.

**Rationale**: Props opcionales = zero breaking changes. Las páginas existentes siguen funcionando sin modificar. La extensibilidad permite que nuevas features usen las variantes sin duplicar componentes.

### 4. Skeleton Patterns — SkeletonTable y SkeletonCard

**Decision**: Crear componentes de composición que usan `Skeleton` internamente.

**SkeletonTable**:
```ts
interface SkeletonTableProps {
  columns?: number;   // default: 4
  rows?: number;      // default: 5
  className?: string;
}
```
- Renderiza un header skeleton (1 fila con N columnas, `h-10`) + M filas de datos (cada una con N columnas `h-6`)
- Usa `Skeleton variant="text"` para cada celda
- Estructura: `<div>` contenedor con `border border-gray-200 rounded-lg overflow-hidden` → header row con `bg-gray-50` → body rows con `bg-white` (alternando `bg-gray-50` cada 2 filas)

**SkeletonCard**:
```ts
interface SkeletonCardProps {
  className?: string;
}
```
- Renderiza una card skeleton: imagen rectangular (`h-48`), título (`h-5 w-3/4`), subtítulo (`h-4 w-1/2`), botón (`h-10 w-24`)
- Usa `Skeleton variant="card"` para la imagen, `Skeleton variant="text"` para textos
- Layout: `rounded-xl border border-gray-200 p-0 overflow-hidden` con padding interno para textos

**Rationale**: Patrones de skeleton reutilizables evitan duplicar arrays de `<Skeleton>` en cada página. AdminUsersPage y AdminOrdersPage actualmente renderizan skeletons inline (ej: `{Array.from({ length: 5 }).map(...)}`). Estos componentes estandarizan el patrón y son usables en cualquier página admin o cliente.

### 5. useToastAsync — toast.promise() Wrapper

**Decision**:

```ts
function useToastAsync() {
  const promise = <T>(
    promise: Promise<T>,
    messages: {
      loading: string;
      success: string | ((data: T) => string);
      error: string | ((err: unknown) => string);
    },
    options?: { duration?: number }
  ) => toast.promise(promise, messages, options);
  
  return { promise };
}
```

**Rationale**: `react-hot-toast` nativamente soporta `toast.promise()` con estados loading/success/error. Actualmente los mutations usan este patrón manual:
```ts
const toastId = toast.loading('Guardando...');
try { await mutateAsync(); toast.success('Guardado', { id: toastId }); }
catch { toast.error('Error', { id: toastId }); }
```

`useToastAsync` abstrae este boilerplate en una línea:
```ts
toastAsync.promise(mutateAsync(), { loading: 'Guardando...', success: 'Guardado', error: 'Error al guardar' });
```

Las funciones `success` y `error` aceptan tanto `string` como `(data: T) => string` para mensajes dinámicos basados en la respuesta.

### 6. Extensión de useToast con info/warning

**Decision**: Agregar `info(message)` y `warning(message)` al hook `useToast`.

`react-hot-toast` soporta tipos custom vía `toast(message, { icon: '...' })`. Se usa:
- `info`: `toast(message, { icon: 'ℹ️' })`
- `warning`: `toast(message, { icon: '⚠️' })`

Se agregan estilos para estos tipos en el `Toaster` de `app/providers.tsx`:
```ts
toastOptions: {
  // ... existentes
  info: { duration: 5000, style: { background: '#1e40af', color: '#fff' } },
  warning: { duration: 5000, style: { background: '#d97706', color: '#fff' } },
}
```

### 7. Eliminación de ToastContainer.tsx

**Decision**: Eliminar `frontend/src/shared/components/ToastContainer.tsx` completamente.

**Rationale**: El `<Toaster>` ya está configurado en `app/providers.tsx:20` con la misma configuración. `ToastContainer.tsx` es código muerto — no se importa en ningún lado (verificado con grep: solo aparece en su propia definición). Mantenerlo es confuso y puede llevar a doble renderizado de toasts si alguien lo importa por error.

### 8. Aplicación de Badge en Páginas Admin

**Decision**: Reemplazar todos los badges inline con `<Badge>` importado de `shared/components/Badge`.

**Mapeo AdminUsersPage**:
- `ROLE_BADGE[role]` → `<Badge variant={ROLE_VARIANT[role]} size="sm">{role}</Badge>`
  - ADMIN → error, STOCK → info, PEDIDOS → warning, CLIENT → success
- Status badges inline → `<Badge variant="success" size="sm">Activo</Badge>`, etc.

**Mapeo AdminProductosPage**:
- Disponible → `<Badge variant="success" size="sm">Disponible</Badge>`
- No disponible → `<Badge variant="error" size="sm">No disponible</Badge>`

**Mapeo AdminIngredientesPage**:
- "Contiene alérgenos" → `<Badge variant="warning" size="sm">Contiene alérgenos</Badge>`
- "Sin alérgenos" → `<Badge variant="success" size="sm">Sin alérgenos</Badge>`

**Mapeo AdminCategoriasPage**:
- Activo → `<Badge variant="success" size="sm">Activo</Badge>`
- Inactivo → `<Badge variant="neutral" size="sm">Inactivo</Badge>`

## Architecture

```
shared/components/
├── Badge.tsx              (NEW — genérico, variant/size/className)
├── ConfirmationModal.tsx  (NEW — compone Modal con footer de confirmación)
├── SkeletonTable.tsx      (NEW — tabla skeleton reutilizable)
├── SkeletonCard.tsx       (NEW — card skeleton reutilizable)
├── Modal.tsx              (MOD — +size prop, fade-in animation)
├── Button.tsx             (MOD — +size, +fullWidth props)
├── EmptyState.tsx         (MOD — +icon, +className props)
├── ErrorDisplay.tsx       (MOD — +title prop)
├── Skeleton.tsx           (MOD — +count, +delay props)
├── ToastContainer.tsx     (DELETED — código muerto)
├── OrderBadge.tsx         (UNCHANGED — específico de pedidos)
└── ...

shared/hooks/
├── useToast.ts            (MOD — +info(), +warning() methods)
└── useToastAsync.ts       (NEW — toast.promise() wrapper)

app/
└── providers.tsx           (MOD — +info/+warning styles en Toaster)

pages/admin/
├── AdminUsersPage.tsx      (MOD — badges inline → <Badge>)
├── AdminProductosPage.tsx  (MOD — badges inline → <Badge>)
├── AdminIngredientesPage.tsx (MOD — badges inline → <Badge>)
├── AdminCategoriasPage.tsx (MOD — badges inline → <Badge>)
└── AdminOrdersPage.tsx     (MOD — +ConfirmationModal en cancelar pedido)
```

## Risks / Trade-offs

| Risk | Mitigation |
| ---- | ---------- |
| `Skeleton.delay` causa layout shift si el contenido real tiene altura diferente | Documentar que el skeleton debe tener el mismo height que el contenido. Usar `SkeletonTable`/`SkeletonCard` que ya replican la estructura real. |
| `ConfirmationModal` no cubre todos los casos de uso futuro (ej: formularios de confirmación con inputs) | Es intencional. `Modal` genérico sigue disponible para casos complejos. `ConfirmationModal` es para el 90% de casos: acción destructiva simple. |
| `Badge` no contempla íconos dentro del badge | No es necesario para los casos actuales. Si se necesita en el futuro, `children` acepta cualquier ReactNode. |
| Eliminar `ToastContainer.tsx` podría romper si algún archivo lo importa | Verificado con grep: cero imports externos. Solo se importa a sí mismo. |

## Open Questions

1. ¿Debería `SkeletonTable` aceptar una prop `headerColumns` separada de `columns` para casos donde header y body tienen distinto número de columnas? (No por ahora — todas las tablas actuales tienen header y body simétricos.)
2. ¿Debería `Badge` tener variante `outline` (solo borde, sin fondo)? (No en este change. Se puede agregar después si hay demanda.)
3. ¿Debería `ConfirmationModal` soportar un `input` de confirmación tipo "Escribí ELIMINAR para confirmar"? (No en MVP. Se puede agregar como prop `requireTypedConfirmation` en change futuro.)
