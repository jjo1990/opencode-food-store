## Context

El frontend existente tiene:

- Catálogo funcional (ProductGrid, filtros, categorías) con TanStack Query + Zustand + URL sync
- Auth funcional (login/register con authStore persistente, ProtectedRoute, Axios interceptor JWT)
- Layout responsivo (Header + Sidebar + Footer con navegación por rol)
- 10 shared components (Button, Card, Input, Skeleton, EmptyState, ErrorDisplay, Spinner, ToastContainer, Pagination, ErrorBoundary)
- Navegación por roles configurada en `shared/config/navigation.ts`

NO existen:

- Entity User ni Address (no hay types ni hooks)
- API modules para usuarios ni direcciones
- Modal component
- Páginas de perfil ni direcciones
- Rutas `/profile` ni `/addresses` en el router

Backend APIs disponibles (Changes 22 y 23):

- `GET /api/v1/usuarios/me` → perfil del usuario
- `PUT /api/v1/usuarios/me` → actualizar nombre/teléfono
- `PUT /api/v1/usuarios/me/contrasena` → cambiar contraseña
- `DELETE /api/v1/usuarios/me` → eliminar cuenta
- `GET /api/v1/direcciones` → listar direcciones
- `POST /api/v1/direcciones` → crear dirección
- `GET /api/v1/direcciones/{id}` → detalle dirección
- `PUT /api/v1/direcciones/{id}` → modificar dirección
- `PATCH /api/v1/direcciones/{id}/principal` → marcar como principal
- `DELETE /api/v1/direcciones/{id}` → eliminar dirección

## Goals / Non-Goals

**Goals:**

- Página de perfil con edición inline de nombre/teléfono
- Cambio de contraseña con modal de verificación
- Página de direcciones con listado, creación, edición, eliminación
- Indicador visual de dirección principal
- Confirmación antes de eliminar direcciones
- Validación inline en todos los formularios
- Estados: Loading (skeleton), Error (retry), Empty (CTA), Success (toast)
- Rutas protegidas con rol CLIENT

**Non-Goals:**

- Edición de email (no está en la API)
- Eliminación de cuenta desde frontend (existe en API pero no se expone)
- Sidebar/header no se modifican (ya existe navegación a perfil)
- Mapa o geolocalización

## Decisions

### 1. Entity pattern: types + hooks separados

- **Decisión**: `entities/user/` con `types.ts` (interfaces) y `api.ts` (TanStack Query hooks), mismo patrón que `entities/product/`
- **Por qué**: Consistencia con el patrón existente. Los hooks encapsulan query keys, staleTime, enabled, etc.
- **Alternativa**: Hooks inline en las páginas — descartado porque dificulta reuso y testing.

### 2. Modal component nuevo en shared

- **Decisión**: Crear `shared/components/Modal.tsx` con portal a body, overlay, animación fade, soporte para título, children, y footer con acciones
- **Por qué**: No existe componente Modal en el proyecto. Se necesita para: cambio de contraseña, agregar/editar dirección, confirmación de eliminación. Mejor crear uno reutilizable que copiar lógica 3 veces.
- **Alternativa**: Usar `<dialog>` nativo HTML — descartado por falta de control de animaciones y comportamiento inconsistente entre navegadores.

### 3. ProfileForm como feature component, no page inline

- **Decisión**: Extraer `ProfileForm` y `PasswordForm` a `features/profile/components/`
- **Por qué**: FSD estricto — la página solo orquesta, la lógica de formulario vive en features. Permite reuso si mañana hay un modal de edición rápida de perfil.
- **Alternativa**: Todo inline en ProfilePage — descartado por violar FSD y dificultar testing.

### 4. AddressList + AddressCard + AddressForm separados

- **Decisión**: Tres componentes en `features/addresses/components/`: AddressList (contenedor con loading/error/empty), AddressCard (card individual con acciones), AddressForm (formulario modal para crear/editar)
- **Por qué**: AddressCard podría reutilizarse en checkout (seleccionar dirección de entrega). AddressList maneja estados de TanStack Query. AddressForm es el formulario puro.
- **Alternativa**: Todo en un solo componente — descartado por falta de separación de responsabilidades.

### 5. TanStack Query mutations con invalidación

- **Decisión**: Después de crear/actualizar/eliminar dirección, invalidar query key `['addresses']` para refrescar lista automáticamente
- **Por qué**: Patrón establecido en el frontend skill. TanStack Query maneja caché y refetch automático.
- **Alternativa**: Refetch manual — descartado porque TanStack Query lo hace mejor con invalidation.

### 6. Sin Modal para confirmación de eliminación con componente separado

- **Decisión**: Reutilizar el Modal shared component para el diálogo de confirmación de eliminación
- **Por qué**: Consistencia visual. El Modal acepta children, así que el contenido de confirmación puede ser personalizado.

## Risks / Trade-offs

| Riesgo                                                                                                                     | Mitigación                                                                             |
| -------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| El Modal component necesita portal para renderizar sobre el layout                                                         | Usar `ReactDOM.createPortal` con un div al final del body                              |
| La mutation de cambio de contraseña requiere contraseña actual + nueva — si falla, el modal se cierra sin feedback claro   | No cerrar el modal automáticamente en error; mostrar error inline en el modal          |
| Al eliminar dirección principal, no se auto-asigna nueva principal (por diseño del backend). El usuario podría confundirse | Mostrar toast informativo: "Dirección eliminada. No hay dirección principal asignada." |
