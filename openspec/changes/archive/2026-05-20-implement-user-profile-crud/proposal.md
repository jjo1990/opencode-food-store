## Why

El sistema registra usuarios con email y nombre, pero no hay forma de que el usuario autenticado vea o modifique su perfil. El modelo `User` ya tiene campos `full_name` y `telefono` que nunca se usan. Sin este change, los usuarios no pueden actualizar sus datos personales ni cambiar su contraseña.

## What Changes

1. **Nuevo módulo `usuarios/`** con estructura feature-first: `schemas.py`, `repository.py`, `service.py`, `router.py`
2. **GET /api/v1/usuarios/me**: retorna perfil del usuario autenticado (id, email, full_name, teléfono, roles, created_at)
3. **PUT /api/v1/usuarios/me**: actualiza full_name y/o teléfono del usuario autenticado
4. **PUT /api/v1/usuarios/me/contrasena**: cambia contraseña (requiere contraseña actual + nueva, invalida refresh tokens)
5. **DELETE /api/v1/usuarios/me**: soft delete del propio usuario (solo CLIENT, no ADMIN)
6. **Incluir `telefono` en UserResponse**: el campo existe en la BD pero no se expone en ninguna respuesta
7. **Tests**: cobertura de los 4 endpoints

## Capabilities

### New Capabilities

- `user-profile`: Gestión del perfil del usuario autenticado — consulta, actualización de datos, cambio de contraseña y auto-eliminación

### Modified Capabilities

- `user-auth`: El schema `UserResponse` se modifica para incluir `telefono` como campo opcional

## Impact

- **Archivos nuevos**: `backend/app/usuarios/__init__.py`, `schemas.py`, `repository.py`, `service.py`, `router.py`
- **Archivos a modificar**: `backend/app/auth/schemas.py` (agregar telefono a UserResponse), `backend/app/main.py` (registrar router), `backend/app/core/dependencies.py` (quizás)
- **Tests**: `backend/tests/test_usuarios_profile.py`
- **Sin cambios en frontend**: es backend puro
