## Context

Food Store necesita que los administradores puedan modificar parámetros operativos del sistema sin redeploy. Actualmente valores como horarios, costo de envío o mensaje de bienvenida están hardcodeados. El módulo `app/admin/` ya existe con router, service, repository y schemas para gestión de usuarios, pedidos, catálogo y métricas. El frontend tiene sidebar con sección admin, rutas protegidas por rol, y patrón establecido con TanStack Query + lazy imports.

No existe ningún modelo `SystemConfig` ni tabla de configuración en la base de datos. Tampoco hay página de configuración en el frontend — la ruta `/admin/reports` existe como placeholder pero `/admin/configuracion` es nueva.

**Restricciones existentes:**

- El flujo backend es unidireccional: `Router → Service → UoW → Repository → Model`. Sin embargo, en `app/admin/` el patrón usado es `Router → Service → Repository` (sin UoW explícito — los repositorios manejan su propia sesión). Se debe seguir este mismo patrón.
- Los modelos usan `from app.models import Base` con SQLAlchemy `Column` declarativo (no SQLModel)
- Las migraciones Alembic usan `op.create_table()` con `sa.Column()`
- La cadena de migraciones tiene múltiples heads. El down_revision se debe determinar ejecutando `alembic heads` al momento de crear la migración. La migración más reciente es `c55383006cf6` (add_ingrediente_model) pero se verificará el head real.
- Los endpoints admin existentes usan `current_user: User = Depends(require_role("ADMIN"))` para RBAC
- Las páginas admin usan `max-w-7xl px-4 py-8` como container estándar
- Componentes compartidos disponibles: `Card`, `Spinner`, `Skeleton`, `ErrorDisplay`
- El interceptor de Axios ya muestra toasts para errores 401/403/422/500

## Goals / Non-Goals

**Goals:**

- Backend: modelo SystemConfig, migración con seeds, repository, service, 2 endpoints REST
- Frontend: API client tipado, página de configuración con formulario, ruta protegida, ítem de navegación
- Auditoría por clave: `updated_by` (UUID del admin) y `updated_at` (timestamp UTC)
- Siembra de 5 parámetros iniciales en la migración
- RBAC estricto: solo ADMIN puede leer o modificar la configuración

**Non-Goals:**

- No validación en tiempo real de valores (ej: verificar que horario_apertura sea una hora válida)
- No versionado de configuración (no hay historial de cambios por clave)
- No visibilidad por rol (solo ADMIN ve la config; no hay parámetros visibles para otros roles)
- No tests automatizados en este change
- No endpoints públicos de configuración (solo admin)

## Decisions

### 1. Modelo: Tabla Key-Value con columnas de auditoría

**Decision**: Usar tabla `system_config` con `clave` (String, PK), `valor` (String), `updated_by` (UUID FK → User, nullable), `updated_at` (DateTime).

**Rationale**: Una tabla key-value es más flexible que un modelo de una sola fila con columnas fijas. Permite agregar nuevas claves de configuración sin migraciones adicionales. Cada clave tiene su propia auditoría independiente: si un admin cambia `costo_envio` y otro cambia `mensaje_bienvenida`, cada clave registra quién y cuándo fue modificada.

**Alternativa considerada**: Una tabla `config` con una columna JSONB que almacene todas las claves en un solo registro. Rechazada porque: (a) la auditoría sería a nivel de registro completo, no por clave; (b) las migraciones para agregar nuevas claves serían más complejas; (c) el acceso concurrente a distintas claves generaría conflictos de escritura.

### 2. Ubicación del código: dentro del módulo `app/admin/` existente

**Decision**: Agregar el modelo en un archivo nuevo (`app/models/system_config.py`), y el repository, service y router en los archivos existentes de `app/admin/`.

**Rationale**: La configuración del sistema es una funcionalidad administrativa. Los endpoints se montan bajo el prefijo `/admin` existente. Mantener todo en el módulo admin sigue el patrón establecido por `AdminMetricsRepository`, `AdminUserRepository`, etc. No se justifica un módulo separado para 2 endpoints y 1 modelo.

**Alternativa considerada**: Crear un módulo `app/system_config/` separado con su propio router. Rechazada — agrega complejidad innecesaria (nuevo router, nuevo prefijo, nueva inicialización) para una funcionalidad pequeña que pertenece conceptualmente al panel de administración.

### 3. API Contract

**Decision**:

```
GET /admin/configuracion
  → 200: {
      "configuracion": { "clave": "valor", ... },
      "auditoria": {
        "clave": {
          "updated_by": "uuid" | null,
          "updated_by_name": "Nombre Admin" | null,
          "updated_at": "2026-06-16T20:00:00Z"
        }, ...
      }
    }

PUT /admin/configuracion
  ← Body: { "configuracion": { "clave": "valor", ... } }
  → 200: misma forma que GET (datos actualizados)
  → 403: si el usuario no es ADMIN
```

**Rationale**: La respuesta incluye tanto la configuración como la auditoría en dos objetos separados para que el frontend pueda mostrar los valores en el formulario y al mismo tiempo renderizar "Última modificación por X el día Y" debajo de cada campo. El `updated_by_name` se resuelve mediante JOIN con la tabla `user` en el repository.

El PUT acepta un dict parcial: solo las claves enviadas se actualizan, el resto permanece intacto. Esto permite editar un solo campo sin reenviar todos los demás. La respuesta del PUT devuelve la configuración completa (no solo las claves modificadas) para mantener la coherencia con el estado del frontend.

### 4. Seed Data en la Migración

**Decision**: Insertar 5 filas iniciales en el `upgrade()` de la migración Alembic:

| clave                | valor                                                       |
| -------------------- | ----------------------------------------------------------- |
| `horario_apertura`   | `"08:00"`                                                   |
| `horario_cierre`     | `"22:00"`                                                   |
| `zona_entrega`       | `"{\"lat\": -34.6037, \"lng\": -58.3816, \"radio_km\": 5}"` |
| `costo_envio`        | `"150.00"`                                                  |
| `mensaje_bienvenida` | `"¡Bienvenido a Food Store!"`                               |

**Rationale**: Estos 5 parámetros son los valores de configuración usados actualmente en el sistema. La migración los siembra con `updated_by = NULL` y `updated_at = now()` para indicar que fueron creados por el sistema, no por un admin específico. Esto asegura que después de correr la migración, el endpoint GET devuelva datos reales en lugar de un diccionario vacío.

**Alternativa considerada**: No sembrar datos y mostrar un formulario vacío. Rechazada — el frontend necesita valores iniciales para renderizar el formulario; un estado vacío agrega complejidad innecesaria de manejo de "no configurado".

### 5. Frontend Structure

**Decision**:

```
shared/api/configApi.ts        ← Interfaces + fetchConfig() + updateConfig()
pages/admin/AdminConfigPage.tsx ← Formulario con input por clave + botón Guardar
```

- **TanStack Query**: `useQuery(['admin', 'configuracion'], fetchConfig)` para GET, `useMutation` para PUT con `onSuccess` que invalida la query y muestra toast de confirmación
- **Estados**:
  - **Loading**: `Skeleton` lines (una por cada input esperado)
  - **Error**: `ErrorDisplay` con mensaje y botón "Reintentar"
  - **Success (tras guardar)**: toast verde "Configuración guardada correctamente" vía `react-hot-toast`
- **Formulario**: un `<input type="text">` por cada clave del diccionario `configuracion`, más un `<textarea>` para `mensaje_bienvenida`. Botón "Guardar cambios" deshabilitado mientras el mutation está en progreso
- **Ruta**: `/admin/configuracion` con `ProtectedRoute allowedRoles={['ADMIN']}` y lazy import
- **Nav**: `{ label: 'Configuración', path: '/admin/configuracion', icon: '⚙️', allowedRoles: ['ADMIN'], section: 'admin' }` — se inserta después del ítem Dashboard

**Alternativa considerada**: Usar `react-hook-form`. Rechazada — el proyecto ya decidió usar TanStack Form como estándar. Sin embargo, para un formulario simple de key-value dinámicas (las claves vienen del backend), usar TanStack Query + estado local con `useState` es más simple que configurar TanStack Form con campos dinámicos.

### 6. Auditoría

**Decision**: `updated_by` almacena el UUID del admin que realizó el PUT, y `updated_at` se actualiza con `datetime.utcnow()` en cada escritura. El GET hace JOIN con `User` para incluir `updated_by_name` en la respuesta.

**Rationale**: No se necesita una tabla de auditoría completa (con historial de cambios) en este change. El requisito es saber quién modificó cada clave por última vez. Esto es suficiente para trazabilidad operativa. Si en el futuro se necesita historial completo, se puede agregar una tabla `system_config_audit` sin cambiar este diseño.

**Trade-off**: Si dos admins modifican la misma clave en rápida sucesión, solo se registra el último. Para un sistema de configuración de parámetros operativos esto es aceptable.

## Architecture

```
Router (admin/router.py)
  └─ GET  /admin/configuracion  → service.get_config(current_user)
  └─ PUT  /admin/configuracion  → service.update_config(body, current_user)

Service (admin/service.py) — AdminService
  └─ self.config_repo = AdminConfigRepository(db)
  └─ get_config()    → SystemConfigResponse
  └─ update_config() → SystemConfigResponse

Repository (admin/repository.py) — AdminConfigRepository
  └─ get_all()        → list[SystemConfig] (con JOIN a User para nombre)
  └─ upsert(clave, valor, updated_by) → None (actualiza o inserta)

Model (models/system_config.py) — SystemConfig(Base)
  └─ clave: String PK
  └─ valor: String
  └─ updated_by: UUID FK → User (nullable)
  └─ updated_at: DateTime

Schemas (admin/schemas.py)
  └─ SystemConfigAuditItem
  └─ SystemConfigResponse
  └─ SystemConfigUpdateRequest
```

## Data Flow — GET /admin/configuracion

```
1. Repository.get_all() → SELECT * FROM system_config LEFT JOIN user ON updated_by = user.id
2. Service.get_config() → itera filas, construye:
     configuracion = {row.clave: row.valor}
     auditoria = {row.clave: {updated_by, updated_by_name (del JOIN), updated_at}}
3. Router → retorna SystemConfigResponse(configuracion=..., auditoria=...)
```

## Data Flow — PUT /admin/configuracion

```
1. Router recibe { "configuracion": { "costo_envio": "200.00" } }
2. Service.update_config() → por cada clave en el body:
     Repository.upsert(clave, valor, updated_by=current_user.id)
       → UPDATE system_config SET valor=..., updated_by=..., updated_at=now() WHERE clave=...
       → Si no existe (rowcount=0): INSERT INTO system_config ...
3. Service.get_config() → retorna la configuración completa actualizada
4. Router → retorna SystemConfigResponse
```

## Risks / Trade-offs

| Risk                                                                                      | Mitigation                                                                                                               |
| ----------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| Sin validación de tipos: `costo_envio` podría guardarse como "gratis" en vez de un número | Documentar en el frontend el formato esperado con placeholders. Validación de tipos se puede agregar en change futuro.   |
| Sin versionado: un cambio accidental no se puede deshacer                                 | El alcance del MVP no incluye historial. Se recomienda agregar `system_config_audit` en un change futuro si se necesita. |
| El modelo usa String para `valor` — sin validación de longitud                            | La columna se crea como `sa.String(500)` en la migración. Suficiente para los parámetros actuales.                       |
| La migración usa `op.bulk_insert()` para los seeds — dependencia de SQLAlchemy Core       | Las migraciones del proyecto ya usan SQLAlchemy Core (`op.create_table`). Es consistente.                                |
| Si un admin malicioso inyecta claves con nombres no previstos, se persisten               | Esto es por diseño: la tabla key-value permite extensibilidad. El frontend muestra todas las claves existentes.          |

## Migration Plan

**Upgrade**: Crear tabla `system_config` con PK `clave`, FK a `user`, e insertar 5 filas seed.

**Rollback**: `op.drop_table("system_config")` en `downgrade()`. Cero impacto en otras tablas.

## Open Questions

1. ¿Se debería permitir eliminar claves de configuración? (No en este change. Solo GET y PUT.)
2. ¿Debería haber un endpoint público para leer ciertas claves (ej: `mensaje_bienvenida` desde el frontend público)? (No en este change. Solo admin.)
3. ¿El `costo_envio` debería estar en centavos (int) o en pesos (decimal string)? (Se usa string para flexibilidad con otros valores no numéricos. El frontend puede parsear y formatear.)
