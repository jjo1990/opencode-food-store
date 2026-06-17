# ui-feedback Specification

## Purpose

Especifica el sistema centralizado de feedback visual para el usuario en Food Store. Cubre el componente Badge genérico con variantes semánticas, ConfirmationModal para acciones destructivas, mejoras de extensibilidad en componentes compartidos (Modal, Button, Skeleton, EmptyState, ErrorDisplay), patrones de skeleton reutilizables (SkeletonTable, SkeletonCard), y el sistema de toasts asíncronos con `toast.promise()`.

## ADDED Requirements

### Requirement: Badge renders with correct variant colors

El sistema DEBE proporcionar un componente `Badge` que renderice con los colores correctos según su variante semántica.

#### Scenario: Badge variant success renders green

- **WHEN** se renderiza `<Badge variant="success">Activo</Badge>`
- **THEN** el badge muestra fondo `bg-green-100` y texto `text-green-800`

#### Scenario: Badge variant warning renders amber

- **WHEN** se renderiza `<Badge variant="warning">Pendiente</Badge>`
- **THEN** el badge muestra fondo `bg-amber-100` y texto `text-amber-800`

#### Scenario: Badge variant error renders red

- **WHEN** se renderiza `<Badge variant="error">Cancelado</Badge>`
- **THEN** el badge muestra fondo `bg-red-100` y texto `text-red-800`

#### Scenario: Badge variant info renders blue

- **WHEN** se renderiza `<Badge variant="info">En Camino</Badge>`
- **THEN** el badge muestra fondo `bg-blue-100` y texto `text-blue-800`

#### Scenario: Badge variant neutral renders gray

- **WHEN** se renderiza `<Badge variant="neutral">Sin estado</Badge>`
- **THEN** el badge muestra fondo `bg-gray-100` y texto `text-gray-800`

---

### Requirement: Badge supports size variants

El sistema DEBE permitir dos tamaños de badge mediante la prop `size`.

#### Scenario: Badge size sm renders small

- **WHEN** se renderiza `<Badge size="sm">Texto</Badge>`
- **THEN** el badge tiene padding `px-2 py-0.5` y texto `text-xs`

#### Scenario: Badge size md renders medium

- **WHEN** se renderiza `<Badge size="md">Texto</Badge>`
- **THEN** el badge tiene padding `px-3 py-1` y texto `text-sm`

#### Scenario: Badge size defaults to sm when not specified

- **WHEN** se renderiza `<Badge variant="success">Texto</Badge>` sin prop `size`
- **THEN** el badge tiene el tamaño `sm` (padding `px-2 py-0.5`, texto `text-xs`)

---

### Requirement: Badge accepts className for extension

El sistema DEBE permitir extender los estilos del Badge mediante la prop `className`.

#### Scenario: Badge with custom className

- **WHEN** se renderiza `<Badge variant="info" className="ml-2">Extra</Badge>`
- **THEN** el badge incluye la clase `ml-2` además de sus clases base y de variante

---

### Requirement: ConfirmationModal shows with correct variant

El sistema DEBE proporcionar un `ConfirmationModal` que muestre botones con colores según la variante.

#### Scenario: ConfirmationModal danger variant shows red confirm button

- **WHEN** se renderiza `<ConfirmationModal isOpen={true} variant="danger" ...>`
- **THEN** el botón de confirmación usa el estilo `danger` (rojo)
- **AND** el botón de cancelación usa estilo `ghost`

#### Scenario: ConfirmationModal warning variant shows secondary confirm button

- **WHEN** se renderiza `<ConfirmationModal isOpen={true} variant="warning" ...>`
- **THEN** el botón de confirmación usa el estilo `secondary` (borde primary)
- **AND** el botón de cancelación usa estilo `ghost`

#### Scenario: ConfirmationModal info variant shows primary confirm button

- **WHEN** se renderiza `<ConfirmationModal isOpen={true} variant="info" ...>`
- **THEN** el botón de confirmación usa el estilo `primary` (verde)
- **AND** el botón de cancelación usa estilo `ghost`

#### Scenario: ConfirmationModal defaults to info variant

- **WHEN** se renderiza `<ConfirmationModal isOpen={true} ...>` sin prop `variant`
- **THEN** el botón de confirmación usa el estilo `primary`

---

### Requirement: ConfirmationModal triggers onConfirm callback

El sistema DEBE ejecutar la callback `onConfirm` cuando el usuario hace clic en el botón de confirmación.

#### Scenario: User clicks confirm button

- **WHEN** el usuario hace clic en el botón "Confirmar" (o el valor de `confirmLabel`)
- **THEN** se ejecuta la función `onConfirm`
- **AND** el modal NO se cierra automáticamente (el cierre lo controla `onClose`)

#### Scenario: User clicks cancel button

- **WHEN** el usuario hace clic en el botón "Cancelar" (o el valor de `cancelLabel`)
- **THEN** se ejecuta la función `onClose`
- **AND** NO se ejecuta `onConfirm`

#### Scenario: User clicks overlay backdrop

- **WHEN** el usuario hace clic fuera del modal (en el overlay)
- **THEN** se ejecuta `onClose`
- **AND** NO se ejecuta `onConfirm`

#### Scenario: User presses Escape key

- **WHEN** el usuario presiona la tecla Escape
- **THEN** se ejecuta `onClose`
- **AND** NO se ejecuta `onConfirm`

---

### Requirement: ConfirmationModal shows loading state

El sistema DEBE mostrar un spinner y deshabilitar el botón de confirmación cuando `isLoading` es `true`.

#### Scenario: ConfirmationModal in loading state

- **WHEN** se renderiza `<ConfirmationModal isOpen={true} isLoading={true} ...>`
- **THEN** el botón de confirmación muestra un spinner inline
- **AND** el botón de confirmación está deshabilitado (`disabled`)
- **AND** el botón de cancelación permanece habilitado

#### Scenario: ConfirmationModal exits loading state

- **WHEN** `isLoading` cambia de `true` a `false`
- **THEN** el spinner desaparece del botón de confirmación
- **AND** el botón de confirmación vuelve a estar habilitado

---

### Requirement: Toast async wraps promise with loading/success/error states

El sistema DEBE proporcionar un hook `useToastAsync` que use `toast.promise()` para mostrar estados de carga, éxito y error durante operaciones asíncronas.

#### Scenario: Toast async shows loading state while promise is pending

- **WHEN** se llama a `toastAsync.promise(fetchData(), { loading: 'Cargando...', success: 'Listo', error: 'Falló' })`
- **THEN** se muestra un toast con el mensaje "Cargando..." y un spinner
- **AND** el toast permanece visible mientras la promesa está pendiente

#### Scenario: Toast async shows success when promise resolves

- **WHEN** la promesa pasada a `toastAsync.promise()` se resuelve exitosamente
- **THEN** el toast de carga se reemplaza por un toast de éxito con el mensaje `success`
- **AND** el toast de éxito se cierra automáticamente después de la duración configurada

#### Scenario: Toast async shows error when promise rejects

- **WHEN** la promesa pasada a `toastAsync.promise()` es rechazada
- **THEN** el toast de carga se reemplaza por un toast de error con el mensaje `error`
- **AND** el toast de error se cierra automáticamente después de la duración configurada

#### Scenario: Toast async success message is dynamic function

- **WHEN** `success` es una función `(data: T) => string` y la promesa se resuelve con datos
- **THEN** el toast de éxito muestra el resultado de llamar a la función con los datos resueltos

---

### Requirement: useToast includes info and warning methods

El sistema DEBE extender el hook `useToast` existente con métodos `info()` y `warning()`.

#### Scenario: useToast.info shows an info toast

- **WHEN** se llama a `toast.info('Recordatorio: la tienda cierra a las 22:00')`
- **THEN** se muestra un toast con el mensaje y un ícono informativo (ℹ️)
- **AND** el toast usa el estilo configurado para tipo `info` en el Toaster

#### Scenario: useToast.warning shows a warning toast

- **WHEN** se llama a `toast.warning('Quedan pocas unidades')`
- **THEN** se muestra un toast con el mensaje y un ícono de advertencia (⚠️)
- **AND** el toast usa el estilo configurado para tipo `warning` en el Toaster

---

### Requirement: Toaster global config includes info and warning styles

El sistema DEBE configurar estilos visuales para los tipos de toast `info` y `warning` en el componente `<Toaster>` global.

#### Scenario: Toaster has info style configured

- **WHEN** se renderiza el `<Toaster>` en `app/providers.tsx`
- **THEN** `toastOptions` incluye la clave `info` con `duration: 5000` y estilos visuales (fondo azul oscuro, texto blanco)

#### Scenario: Toaster has warning style configured

- **WHEN** se renderiza el `<Toaster>` en `app/providers.tsx`
- **THEN** `toastOptions` incluye la clave `warning` con `duration: 5000` y estilos visuales (fondo ámbar oscuro, texto blanco)

---

### Requirement: Skeleton renders count items

El sistema DEBE permitir renderizar múltiples skeletons iguales mediante la prop `count`.

#### Scenario: Skeleton with count=5 renders five items

- **WHEN** se renderiza `<Skeleton count={5} />`
- **THEN** se renderizan 5 elementos `<Skeleton>` en un contenedor con `space-y-2`

#### Scenario: Skeleton with count=1 (default) renders single item

- **WHEN** se renderiza `<Skeleton />` sin prop `count`
- **THEN** se renderiza exactamente 1 skeleton (comportamiento actual preservado)

---

### Requirement: Skeleton supports delay prop to prevent flash

El sistema DEBE permitir retrasar la aparición del skeleton para evitar flashes en cargas rápidas.

#### Scenario: Skeleton with delay=200 does not render before 200ms

- **WHEN** se renderiza `<Skeleton delay={200} />` y el componente se monta
- **THEN** durante los primeros 200ms no se renderiza nada (retorna `null`)
- **AND** después de 200ms, el skeleton aparece normalmente

#### Scenario: Skeleton with delay=0 renders immediately

- **WHEN** se renderiza `<Skeleton delay={0} />`
- **THEN** el skeleton se renderiza inmediatamente (comportamiento actual preservado)

---

### Requirement: Modal supports size prop

El sistema DEBE permitir controlar el ancho máximo del Modal mediante la prop `size`.

#### Scenario: Modal size sm renders with max-w-sm

- **WHEN** se renderiza `<Modal size="sm" ...>`
- **THEN** el panel del modal tiene `max-w-sm`

#### Scenario: Modal size xl renders with max-w-xl

- **WHEN** se renderiza `<Modal size="xl" ...>`
- **THEN** el panel del modal tiene `max-w-xl`

#### Scenario: Modal size defaults to lg (max-w-lg)

- **WHEN** se renderiza `<Modal ...>` sin prop `size`
- **THEN** el panel del modal tiene `max-w-lg` (comportamiento actual preservado)

---

### Requirement: Button supports size prop

El sistema DEBE permitir controlar el tamaño del Button mediante la prop `size`.

#### Scenario: Button size sm renders small

- **WHEN** se renderiza `<Button size="sm">Click</Button>`
- **THEN** el botón tiene `px-3 py-1.5 text-xs`

#### Scenario: Button size lg renders large

- **WHEN** se renderiza `<Button size="lg">Click</Button>`
- **THEN** el botón tiene `px-6 py-3 text-base`

---

### Requirement: Button supports fullWidth prop

El sistema DEBE permitir que el Button ocupe el ancho completo de su contenedor.

#### Scenario: Button with fullWidth is w-full

- **WHEN** se renderiza `<Button fullWidth>Click</Button>`
- **THEN** el botón tiene la clase `w-full`

#### Scenario: Button without fullWidth has auto width

- **WHEN** se renderiza `<Button>Click</Button>` sin prop `fullWidth`
- **THEN** el botón NO tiene `w-full` y usa su ancho natural

---

### Requirement: EmptyState accepts custom icon

El sistema DEBE permitir personalizar el ícono del EmptyState.

#### Scenario: EmptyState with custom icon

- **WHEN** se renderiza `<EmptyState icon={<MyIcon />} title="..." description="..." />`
- **THEN** se renderiza el ícono personalizado en lugar del ícono de bandeja por defecto

#### Scenario: EmptyState without icon shows default

- **WHEN** se renderiza `<EmptyState title="..." description="..." />` sin prop `icon`
- **THEN** se renderiza el ícono de bandeja de entrada por defecto (comportamiento actual)

---

### Requirement: EmptyState accepts className

El sistema DEBE permitir extender el contenedor del EmptyState con clases adicionales.

#### Scenario: EmptyState with className

- **WHEN** se renderiza `<EmptyState className="mt-8" title="..." description="..." />`
- **THEN** el wrapper del EmptyState incluye la clase `mt-8`

---

### Requirement: ErrorDisplay accepts custom title

El sistema DEBE permitir personalizar el título del ErrorDisplay.

#### Scenario: ErrorDisplay with custom title

- **WHEN** se renderiza `<ErrorDisplay title="Error de conexión" message="..." />`
- **THEN** el título mostrado es "Error de conexión" en lugar de "Algo salió mal"

#### Scenario: ErrorDisplay without title shows default

- **WHEN** se renderiza `<ErrorDisplay message="..." />` sin prop `title`
- **THEN** el título mostrado es "Algo salió mal" (comportamiento actual)

---

### Requirement: ToastContainer.tsx is removed

El sistema NO DEBE contener el componente `ToastContainer.tsx` ya que el `<Toaster>` global está configurado en `app/providers.tsx`.

#### Scenario: ToastContainer.tsx file does not exist

- **WHEN** se lista el directorio `shared/components/`
- **THEN** el archivo `ToastContainer.tsx` no existe

#### Scenario: No imports reference ToastContainer

- **WHEN** se busca `ToastContainer` en todos los archivos del proyecto
- **THEN** no hay imports de `ToastContainer` en ningún archivo (solo existía su propia definición)

---

### Requirement: Badge Component Replaces Duplicated Inline Badges

El sistema DEBE reemplazar todos los badges inline duplicados en páginas admin con el componente `<Badge>` genérico.

#### Scenario: AdminUsersPage uses Badge for roles

- **WHEN** se renderiza AdminUsersPage con usuarios que tienen roles
- **THEN** los badges de rol usan `<Badge variant="...">` en lugar de spans inline con clases Tailwind
- **AND** los colores por rol se preservan: ADMIN usa variant error, STOCK usa info, PEDIDOS usa warning, CLIENT usa success

#### Scenario: AdminUsersPage uses Badge for user status

- **WHEN** se renderiza AdminUsersPage con usuarios activos/inactivos/eliminados
- **THEN** los badges de estado usan `<Badge variant="...">`: Activo → success, Inactivo → neutral, Eliminado → error

#### Scenario: AdminProductosPage uses Badge for availability

- **WHEN** se renderiza AdminProductosPage
- **THEN** los badges de disponibilidad usan `<Badge>`: Disponible → success, No disponible → error

#### Scenario: AdminIngredientesPage uses Badge for allergens

- **WHEN** se renderiza AdminIngredientesPage
- **THEN** los badges de alérgenos usan `<Badge>`: Contiene alérgenos → warning, Sin alérgenos → success

#### Scenario: AdminCategoriasPage uses Badge for category status

- **WHEN** se renderiza AdminCategoriasPage
- **THEN** los badges de estado usan `<Badge>`: Activo → success, Inactivo → neutral

---

### Requirement: ConfirmationModal is used for destructive actions

El sistema DEBE usar `ConfirmationModal` antes de ejecutar acciones destructivas o irreversibles.

#### Scenario: AdminOrdersPage shows confirmation before canceling order

- **WHEN** un admin hace clic en "Cancelar pedido" en AdminOrdersPage
- **THEN** se muestra un `ConfirmationModal` con variant danger, título "Cancelar pedido", y mensaje explicando que la acción no se puede deshacer
- **AND** el pedido solo se cancela si el admin confirma en el modal

#### Scenario: AdminOrdersPage cancel confirmation is dismissed

- **WHEN** el `ConfirmationModal` de cancelar pedido está abierto y el admin hace clic en "Cancelar" o cierra el modal
- **THEN** el modal se cierra sin cancelar el pedido

---

### Requirement: SkeletonTable renders table-shaped skeleton

El sistema DEBE proporcionar un componente `SkeletonTable` que renderice una estructura de tabla esqueleto.

#### Scenario: SkeletonTable renders header and data rows

- **WHEN** se renderiza `<SkeletonTable columns={5} rows={5} />`
- **THEN** se renderiza 1 fila de header con 5 celdas skeleton (`h-10`)
- **AND** se renderizan 5 filas de datos con 5 celdas skeleton cada una (`h-6`)

#### Scenario: SkeletonTable uses default columns and rows

- **WHEN** se renderiza `<SkeletonTable />` sin props
- **THEN** se renderiza con 4 columnas y 5 filas (defaults)

---

### Requirement: SkeletonCard renders card-shaped skeleton

El sistema DEBE proporcionar un componente `SkeletonCard` que renderice una estructura de card esqueleto.

#### Scenario: SkeletonCard renders image and text placeholders

- **WHEN** se renderiza `<SkeletonCard />`
- **THEN** se renderiza un skeleton de imagen rectangular (`h-48`)
- **AND** se renderiza un skeleton de título (`h-5 w-3/4`)
- **AND** se renderiza un skeleton de subtítulo (`h-4 w-1/2`)
