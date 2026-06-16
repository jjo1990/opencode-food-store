## Why

Los administradores necesitan modificar parámetros del sistema (horarios de apertura, costo de envío, zona de entrega, mensaje de bienvenida) en tiempo de ejecución sin necesidad de redeploy. Actualmente todos estos valores están hardcodeados en el código o dispersos en variables de entorno, lo que obliga a un redeploy ante cualquier ajuste operativo. Esto bloquea la flexibilidad del negocio para adaptarse a cambios de horario, promociones de envío gratis, o ajustes de zona de cobertura.

## What Changes

- **Nueva tabla `system_config`** — modelo key-value con clave primaria string, valor texto, y columnas de auditoría (`updated_by` FK → User, `updated_at`)
- **Migración Alembic** — crea la tabla y siembra 5 filas iniciales con valores por defecto (horario_apertura, horario_cierre, zona_entrega, costo_envio, mensaje_bienvenida)
- **Nuevo `AdminConfigRepository`** en `backend/app/admin/repository.py` — queries de lectura/upsert sobre `SystemConfig`
- **Nuevos schemas Pydantic** en `backend/app/admin/schemas.py` — `SystemConfigResponse` y `SystemConfigUpdateRequest`
- **Nuevos métodos en `AdminService`** — `get_config()` y `update_config()` con lógica de upsert + auditoría
- **Dos nuevos endpoints** en `backend/app/admin/router.py`:
  - `GET /admin/configuracion` — devuelve todas las claves como diccionario + metadata de auditoría por clave
  - `PUT /admin/configuracion` — recibe un dict de clave-valor, hace upsert por clave, actualiza auditoría
- **Frontend: API client** `shared/api/configApi.ts` — interfaces tipadas + `fetchConfig()` y `updateConfig()`
- **Frontend: página** `pages/admin/AdminConfigPage.tsx` — formulario con un input por clave de configuración, botón "Guardar cambios", estados de loading/error/éxito
- **Frontend: ruta** `/admin/configuracion` con `ProtectedRoute allowedRoles={['ADMIN']}` y lazy import
- **Frontend: navegación** — ítem "Configuración" (⚙️) en la sección admin del sidebar

## Capabilities

### New Capabilities

- `system-configuration`: Gestión de configuración del sistema en tiempo de ejecución para administradores. Incluye modelo key-value con auditoría por clave, endpoints GET/PUT protegidos por RBAC, y página de administración en el frontend con formulario de edición.

### Modified Capabilities

<!-- Ninguna capacidad existente modifica sus requerimientos -->

## Impact

- **Backend**: `backend/app/models/system_config.py` (nuevo), `backend/app/models/__init__.py` (registro), `backend/alembic/versions/` (nueva migración), `backend/app/admin/repository.py` (nuevo repositorio), `backend/app/admin/schemas.py` (nuevos schemas), `backend/app/admin/service.py` (nuevos métodos), `backend/app/admin/router.py` (nuevos endpoints)
- **Frontend**: `frontend/src/shared/api/configApi.ts` (nuevo), `frontend/src/pages/admin/AdminConfigPage.tsx` (nuevo), `frontend/src/app/router.tsx` (nueva ruta), `frontend/src/shared/config/navigation.ts` (nuevo ítem)
- **Base de datos**: Nueva tabla `system_config` con 5 filas seed. FK a `user` para auditoría. Sin impacto en tablas existentes.
- **Dependencias**: Ninguna nueva. SQLAlchemy y FastAPI ya están disponibles.
- **Seguridad**: Ambos endpoints requieren `require_role("ADMIN")`. El campo `updated_by` registra qué admin realizó cada cambio. Sin exposición de datos sensibles adicional.
