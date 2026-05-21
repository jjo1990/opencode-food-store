## Why

Los usuarios pueden gestionar su perfil y direcciones vía API (Changes 22 y 23), pero no hay interfaz visual para hacerlo. Sin estas páginas, el usuario no puede actualizar sus datos personales, cambiar su contraseña, ni gestionar sus direcciones de entrega — funcionalidades necesarias antes de llegar al flujo de checkout (Phase 4+).

## What Changes

- Nueva entity `User` en `entities/user/` con types y TanStack Query hooks (useProfile, useUpdateProfile, useChangePassword)
- Nueva entity `Address` en `entities/address/` con types y TanStack Query hooks (useAddresses, useCreateAddress, useUpdateAddress, useDeleteAddress, useSetPrincipal)
- Nuevos API modules en `shared/api/`: `usuariosApi.ts` y `direccionesApi.ts`
- Nueva página `ProfilePage` en `pages/ProfilePage.tsx` con:
  - Formulario editable de nombre y teléfono (inline, sin modal)
  - Sección de cambio de contraseña con modal de confirmación
  - TanStack Query: useQuery para cargar perfil, useMutation para actualizar
- Nueva página `AddressesPage` en `pages/AddressesPage.tsx` con:
  - Lista de direcciones con indicador de principal (estrella/badge)
  - Botones editar/eliminar por dirección
  - Modal para agregar/editar dirección (add EditAddressForm)
  - Confirmación de eliminación con advertencia
  - TanStack Query: useQuery para listar, useMutation para crear/actualizar/eliminar/setPrincipal
- Nuevo shared component `Modal` para diálogos de edición/confirmación
- Nuevos feature components: `ProfileForm`, `PasswordForm`, `AddressList`, `AddressCard`, `AddressForm`
- Registro de rutas `/profile` y `/addresses` en el router, protegidas con CLIENT role
- Validación inline de inputs en todos los formularios

## Capabilities

### New Capabilities

- `user-profile-frontend`: Interfaz de perfil de usuario con edición de datos personales y cambio de contraseña
- `delivery-addresses-frontend`: Interfaz de gestión de direcciones de entrega con CRUD visual y selector de principal

### Modified Capabilities

- _(ninguna — no hay specs frontend previas)_

## Impact

- **Frontend**: ~13 archivos nuevos (entities, API modules, features, pages, components), 2 archivos modificados (router, navigation config)
- **Dependencias**: Changes 22 (user-profile-crud) y 23 (delivery-addresses-crud) ya archivados — las APIs existen y funcional
- **No breaking**: no modifica APIs existentes, solo agrega nuevas páginas
