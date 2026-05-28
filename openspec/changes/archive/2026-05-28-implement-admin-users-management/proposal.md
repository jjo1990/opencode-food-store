## Why

El módulo admin tiene solo 2 endpoints para gestión de roles (heredados del Change 12) y la página de usuarios en frontend es un placeholder "Próximamente". Los administradores necesitan una interfaz completa para gestionar usuarios del sistema: listar, buscar, ver detalle, editar datos y roles, desactivar/activar cuentas. Sin esto, la administración del sistema depende de operaciones directas en base de datos.

## What Changes

- **`GET /api/v1/admin/usuarios`**: listado paginado de usuarios, filtrable por rol, email/name (ILIKE), estado (activo/inactivo)
- **`GET /api/v1/admin/usuarios/{user_id}`**: detalle completo de un usuario con sus roles
- **`PUT /api/v1/admin/usuarios/{user_id}`**: actualizar nombre, email, teléfono y/o roles
- **`DELETE /api/v1/admin/usuarios/{user_id}`**: soft delete (marca `soft_deleted_at`)
- **`PATCH /api/v1/admin/usuarios/{user_id}/reactivar`**: restaurar un usuario soft-deleted
- **Seguridad**: solo ADMIN puede operar; protege al último admin de perder su rol
- **Invalidación de tokens**: al cambiar roles, se revocan todos los refresh tokens del usuario (fuerza re-login)

## Capabilities

### New Capabilities

- `admin-users`: Gestión administrativa de usuarios — listado, búsqueda, detalle, edición, activación/desactivación, control de roles con protección del último administrador

### Modified Capabilities

- (ninguna — los endpoints existentes de roles en `admin/` se expanden pero no cambian requisitos)

## Impact

- **Nuevos archivos backend**:
  - `backend/app/admin/schemas.py` — schemas Pydantic para request/response admin
  - `backend/app/admin/repository.py` — consultas BD específicas de admin
- **Archivos modificados backend**:
  - `backend/app/admin/service.py` — nuevos métodos: listar, detalle, actualizar, desactivar, reactivar
  - `backend/app/admin/router.py` — nuevos endpoints REST
  - `backend/app/auth/repository.py` — nuevo método `list_all_users()` con filtros
  - `backend/app/core/security.py` — posible exposer de `revoke_all_user_tokens()` si no existe
- **Sin cambios de frontend** (Change 42 cubre la UI)
