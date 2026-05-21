## 1. API Modules & Entities

- [x] 1.1 Crear `shared/api/usuariosApi.ts` con getProfile(), updateProfile(), changePassword()
- [x] 1.2 Crear `shared/api/direccionesApi.ts` con createAddress(), getAddresses(), getAddress(), updateAddress(), setPrincipal(), deleteAddress()
- [x] 1.3 Crear `entities/user/types.ts` con UserProfile interface
- [x] 1.4 Crear `entities/user/api.ts` con useProfile(), useUpdateProfile(), useChangePassword() hooks
- [x] 1.5 Crear `entities/address/types.ts` con Address, AddressCreate, AddressUpdate interfaces
- [x] 1.6 Crear `entities/address/api.ts` con useAddresses(), useCreateAddress(), useUpdateAddress(), useDeleteAddress(), useSetPrincipal() hooks

## 2. Shared Components

- [x] 2.1 Crear `shared/components/Modal.tsx` con portal, overlay, animación, título, children, footer

## 3. Profile Feature

- [x] 3.1 Crear `features/profile/components/ProfileForm.tsx` con edición inline de nombre/teléfono
- [x] 3.2 Crear `features/profile/components/PasswordForm.tsx` con modal de cambio de contraseña

## 4. Addresses Feature

- [x] 4.1 Crear `features/addresses/components/AddressCard.tsx` con datos, badge principal, acciones editar/eliminar/setPrincipal
- [x] 4.2 Crear `features/addresses/components/AddressForm.tsx` con formulario modal para crear/editar dirección
- [x] 4.3 Crear `features/addresses/components/AddressList.tsx` con loading/error/empty/data states

## 5. Pages

- [x] 5.1 Crear `pages/ProfilePage.tsx` orquestando ProfileForm + PasswordForm
- [x] 5.2 Crear `pages/AddressesPage.tsx` orquestando AddressList + AddressForm

## 6. Routing & Navigation

- [x] 6.1 Agregar rutas `/profile` y `/addresses` en `app/router.tsx` con ProtectedRoute(CLIENT)
- [x] 6.2 Verificar que shared/config/navigation.ts tenga entries para perfil y direcciones

## 7. Verify

- [x] 7.1 Type-check: `npx tsc --noEmit` sin errores
- [x] 7.2 Build: `npm run build` exitoso
