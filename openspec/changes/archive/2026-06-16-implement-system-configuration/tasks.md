# Tasks: implement-system-configuration

## 1. Backend — Model & Migration

- [x] 1.1 Crear `backend/app/models/system_config.py` con el modelo `SystemConfig(Base)`: columnas `clave` (String PK), `valor` (String), `updated_by` (UUID FK → User, nullable), `updated_at` (DateTime)
- [x] 1.2 Registrar `SystemConfig` en `backend/app/models/__init__.py` (import + `__all__`)
- [x] 1.3 Crear migración Alembic: crear tabla `system_config` + insertar 5 filas seed (`horario_apertura`, `horario_cierre`, `zona_entrega`, `costo_envio`, `mensaje_bienvenida`) con `updated_by = NULL`
- [x] 1.4 Ejecutar migración y verificar que la tabla existe con los 5 seeds

## 2. Backend — Repository, Service, Schemas, Router

- [x] 2.1 Agregar `AdminConfigRepository` en `backend/app/admin/repository.py` con métodos `get_all()` (JOIN a User para nombre) y `upsert(clave, valor, updated_by)`
- [x] 2.2 Agregar `SystemConfigAuditItem`, `SystemConfigResponse` y `SystemConfigUpdateRequest` en `backend/app/admin/schemas.py`
- [x] 2.3 Agregar `get_config()` a `AdminService` — obtiene todas las filas, construye dict `configuracion` y dict `auditoria` con metadatos por clave
- [x] 2.4 Agregar `update_config()` a `AdminService` — recibe `SystemConfigUpdateRequest` y `current_user`, hace upsert de cada clave con `updated_by = current_user.id`, retorna config actualizada
- [x] 2.5 Agregar `GET /admin/configuracion` y `PUT /admin/configuracion` al router con `response_model` explícito y `Depends(require_role("ADMIN"))`
- [x] 2.6 Verificar endpoints con Swagger UI o curl: GET devuelve 5 claves con auditoría, PUT actualiza y refleja cambios

## 3. Frontend — API Client

- [x] 3.1 Crear `frontend/src/shared/api/adminConfigApi.ts` con interfaces TypeScript: `ConfigResponse`, `ConfigUpdateRequest`
- [x] 3.2 Implementar `fetchConfig()` → `GET /admin/configuracion` y `updateConfig(body)` → `PUT /admin/configuracion`

## 4. Frontend — Page, Route, Navigation

- [x] 4.1 Crear `frontend/src/pages/admin/AdminConfigPage.tsx` con formulario dinámico: un input/textarea por clave de configuración y botón "Guardar cambios"
- [x] 4.2 Implementar `useQuery(['admin', 'configuracion'], fetchConfig)` para GET y `useMutation` para PUT con invalidación de query e invalidation on success
- [x] 4.3 Agregar ruta `/admin/configuracion` en `app/router.tsx` con `lazy(() => import(...))` y `ProtectedRoute allowedRoles={['ADMIN']}`
- [x] 4.4 Agregar ítem `{ label: 'Configuración', path: '/admin/configuracion', icon: '⚙️', allowedRoles: ['ADMIN'], section: 'admin' }` en `shared/config/navigation.ts`
- [x] 4.5 Manejar estados: loading (Skeleton lines), error (ErrorDisplay), success (toast "Configuración guardada")

## 5. Polish & Verify

- [x] 5.1 Ejecutar `npx tsc --noEmit` en `frontend/` — sin errores de TypeScript
- [x] 5.2 Verificar RBAC: usuario sin rol ADMIN recibe 403 en `GET /admin/configuracion` y `PUT /admin/configuracion`
- [x] 5.3 Verificar que los 5 seeds existen en la tabla `system_config` después de correr la migración
- [x] 5.4 Verificar que `updated_by` y `updated_at` se actualizan correctamente al hacer PUT
- [x] 5.5 Verificar frontend: la página carga la configuración existente, permite editar, y al guardar actualiza los valores y la auditoría en la UI
