# user-profile Specification

## Purpose

TBD - created by archiving change implement-user-profile-crud. Update Purpose after archive.

## Requirements

### Requirement: GET /api/v1/usuarios/me retorna perfil completo

El sistema SHALL exponer un endpoint GET que retorne los datos del usuario autenticado.

#### Scenario: Usuario autenticado obtiene su perfil

- **WHEN** el usuario autenticado hace GET a `/api/v1/usuarios/me`
- **THEN** retorna 200 con: `id`, `email`, `full_name`, `telefono`, `roles:[]`, `created_at`
- **AND** el campo `telefono` puede ser null si no fue configurado

#### Scenario: Usuario no autenticado intenta obtener perfil

- **WHEN** un request sin token JWT hace GET a `/api/v1/usuarios/me`
- **THEN** retorna 401 Unauthorized

### Requirement: PUT /api/v1/usuarios/me actualiza perfil

El sistema SHALL exponer un endpoint PUT para actualizar `full_name` y/o `telefono` del usuario autenticado.

#### Scenario: Actualización exitosa de nombre y teléfono

- **WHEN** el usuario autenticado hace PUT a `/api/v1/usuarios/me` con `{ "full_name": "Nuevo Nombre", "telefono": "1234567890" }`
- **THEN** retorna 200 con los datos actualizados
- **AND** el campo `full_name` se actualiza en la BD
- **AND** el campo `telefono` se actualiza en la BD

#### Scenario: Actualización parcial (solo nombre)

- **WHEN** el usuario autenticado hace PUT a `/api/v1/usuarios/me` con `{ "full_name": "Solo Nombre" }`
- **THEN** retorna 200
- **AND** solo `full_name` se actualiza, `telefono` permanece igual

#### Scenario: Validación de nombre muy corto

- **WHEN** el usuario envía `{ "full_name": "A" }`
- **THEN** retorna 422 con error de validación (nombre ≥ 2 caracteres)

### Requirement: PUT /api/v1/usuarios/me/contrasena cambia contraseña

El sistema SHALL exponer un endpoint para cambiar la contraseña, requiriendo la actual para verificación.

#### Scenario: Cambio de contraseña exitoso

- **WHEN** el usuario autenticado hace PUT a `/api/v1/usuarios/me/contrasena` con `{ "current_password": "actual123", "new_password": "nuevaSegura456" }`
- **THEN** retorna 200 con mensaje de éxito
- **AND** la contraseña se actualiza en la BD (hasheada con bcrypt, cost ≥ 12)
- **AND** TODOS los refresh tokens del usuario se eliminan de la BD

#### Scenario: Contraseña actual incorrecta

- **WHEN** el usuario envía `current_password` que no coincide con la hasheada en BD
- **THEN** retorna 401 con mensaje "Contraseña actual incorrecta"

#### Scenario: Nueva contraseña muy corta

- **WHEN** el usuario envía `new_password` con menos de 8 caracteres
- **THEN** retorna 422 con error de validación

### Requirement: DELETE /api/v1/usuarios/me soft delete

El sistema SHALL exponer un endpoint para que el usuario CLIENT elimine su propia cuenta (soft delete).

#### Scenario: Cliente elimina su cuenta

- **WHEN** un usuario con rol CLIENT autenticado hace DELETE a `/api/v1/usuarios/me`
- **THEN** retorna 204 No Content
- **AND** el campo `soft_deleted_at` del usuario se setea a la fecha actual
- **AND** los refresh tokens del usuario se eliminan
- **AND** el usuario no puede hacer login nuevamente

#### Scenario: Admin intenta auto-eliminarse

- **WHEN** un usuario con rol ADMIN autenticado hace DELETE a `/api/v1/usuarios/me`
- **THEN** retorna 403 Forbidden (los ADMIN se gestionan desde el panel)

#### Scenario: Usuario no autenticado intenta eliminar

- **WHEN** un request sin token hace DELETE a `/api/v1/usuarios/me`
- **THEN** retorna 401 Unauthorized
