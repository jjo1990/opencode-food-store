## Context

El módulo `auth/` maneja registro, login, refresh y logout. El modelo `User` tiene los campos necesarios para perfil (`full_name`, `telefono`, `soft_deleted_at`), pero no hay endpoints para que el usuario gestione su perfil. El `UserRepository` en `auth/repository.py` ya tiene consultas base.

Se creará el módulo `usuarios/` siguiendo la arquitectura feature-first del proyecto.

## Goals / Non-Goals

**Goals:**

- Endpoint GET /api/v1/usuarios/me — perfil completo
- Endpoint PUT /api/v1/usuarios/me — actualizar nombre y teléfono
- Endpoint PUT /api/v1/usuarios/me/contrasena — cambiar contraseña con validación
- Endpoint DELETE /api/v1/usuarios/me — soft delete propio (solo CLIENT)
- Incluir `telefono` en UserResponse
- Tests completos

**Non-Goals:**

- Gestión de usuarios por ADMIN (es Change 22 pero del admin panel)
- CRUD de direcciones (es Change 23)
- Frontend de perfil (es Change 24)

## Decisions

### 1. Nuevo módulo `usuarios/` separado de `auth/`

**Decisión**: El perfil va en `backend/app/usuarios/`, no en `backend/app/auth/`.
**Por qué**: `auth/` se ocupa de autenticación (register, login, tokens). El perfil es gestión de datos del usuario autenticado. Son responsabilidades distintas. Feature-first: cada módulo tiene un dominio claro.

### 2. Reutilizar UserRepository existente

**Decisión**: NO crear un nuevo repository. Usar `UserRepository` de `auth/repository.py` y agregar los métodos faltantes (`update_profile`, `soft_delete`).
**Por qué**: Ya existe con queries base, filtros de soft delete y transacciones. No duplicamos lógica de acceso a datos.

### 3. Invalidar refresh tokens al cambiar contraseña

**Decisión**: Al cambiar la contraseña, eliminar TODOS los refresh tokens del usuario.
**Por qué**: Seguridad. Si alguien más tiene un refresh token válido, después del cambio de contraseña debe quedar invalidado. Esto fuerza un relogin en todos los dispositivos.

### 4. Soft delete solo para CLIENT

**Decisión**: El DELETE /me solo funciona si el usuario tiene rol CLIENT. ADMIN y otros roles no pueden auto-eliminarse.
**Por qué**: Un ADMIN no debería poder borrar su cuenta (necesita otro ADMIN). Esto se maneja desde el panel de administración.

## Risks / Trade-offs

| Riesgo                                                                                       | Mitigación                                                                                                   |
| -------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| **UserRepository está en auth/ y usuarios/ lo importa** — puede crear dependencia circular   | No hay círculo: usuarios/ importa auth/repository.py, nadie importa usuarios/ desde auth/. Es unidireccional |
| **Cambiar contraseña invalida refresh tokens** — el usuario queda deslogueado de todos lados | Es el comportamiento deseado. Mostrar mensaje claro "Se cerrarán todas las sesiones activas"                 |
