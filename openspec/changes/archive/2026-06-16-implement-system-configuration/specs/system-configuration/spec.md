# system-configuration Specification

## Purpose

Especifica el modelo de datos, endpoints REST y página de administración para la gestión de configuración del sistema en tiempo de ejecución. Los administradores pueden leer y modificar parámetros operativos (horarios, costo de envío, zona de entrega, mensaje de bienvenida) sin necesidad de redeploy. Cada cambio queda registrado con auditoría por clave (quién modificó y cuándo).

## Requirements

### Requirement: SystemConfig Model

El sistema DEBE tener una tabla `system_config` que almacene pares clave-valor con metadatos de auditoría por clave.

#### Scenario: Tabla system_config existe con la estructura correcta

- **WHEN** se ejecuta la migración Alembic
- **THEN** se crea la tabla `system_config` con columnas: `clave` (String, PK), `valor` (String, NOT NULL), `updated_by` (UUID, FK → user.id, nullable), `updated_at` (DateTime, NOT NULL)
- **AND** la columna `updated_by` tiene una foreign key a `user(id)`

#### Scenario: Seed data se inserta en la migración

- **WHEN** se ejecuta el `upgrade()` de la migración
- **THEN** la tabla `system_config` contiene 5 filas: `horario_apertura` = `"08:00"`, `horario_cierre` = `"22:00"`, `zona_entrega` = `"{\"lat\": -34.6037, \"lng\": -58.3816, \"radio_km\": 5}"`, `costo_envio` = `"150.00"`, `mensaje_bienvenida` = `"¡Bienvenido a Food Store!"`
- **AND** todas las filas seed tienen `updated_by = NULL`

### Requirement: GET /admin/configuracion — Leer configuración del sistema

El sistema DEBE exponer un endpoint `GET /admin/configuracion` que devuelva todas las claves de configuración con sus valores y metadatos de auditoría. Solo accesible por usuarios con rol ADMIN.

#### Scenario: Admin obtiene la configuración completa con auditoría

- **WHEN** un usuario con rol ADMIN hace `GET /admin/configuracion`
- **THEN** el sistema retorna HTTP 200 con body:
  ```json
  {
    "configuracion": {
      "horario_apertura": "08:00",
      "horario_cierre": "22:00",
      "costo_envio": "150.00",
      ...
    },
    "auditoria": {
      "horario_apertura": {
        "updated_by": null,
        "updated_by_name": null,
        "updated_at": "2026-06-16T00:00:00Z"
      },
      ...
    }
  }
  ```
- **AND** el objeto `auditoria` contiene una entrada por cada clave con `updated_by`, `updated_by_name` y `updated_at`

#### Scenario: No hay claves de configuración (tabla vacía)

- **WHEN** un admin hace `GET /admin/configuracion` y la tabla `system_config` está vacía
- **THEN** el sistema retorna HTTP 200 con `configuracion: {}` y `auditoria: {}`

#### Scenario: Usuario sin rol ADMIN es rechazado

- **WHEN** un usuario sin rol ADMIN (CLIENT, STOCK, PEDIDOS o no autenticado) hace `GET /admin/configuracion`
- **THEN** el sistema retorna HTTP 403 Forbidden

### Requirement: PUT /admin/configuracion — Modificar configuración del sistema

El sistema DEBE exponer un endpoint `PUT /admin/configuracion` que reciba un diccionario de claves y valores, haga upsert de cada clave, registre la auditoría, y retorne la configuración completa actualizada. Solo accesible por ADMIN.

#### Scenario: Admin actualiza una clave existente

- **WHEN** un admin hace `PUT /admin/configuracion` con body `{ "configuracion": { "costo_envio": "200.00" } }`
- **THEN** el sistema actualiza la fila `costo_envio` con `valor = "200.00"`, `updated_by = <admin_id>`, `updated_at = <timestamp actual>`
- **AND** retorna HTTP 200 con la configuración completa (incluyendo las claves no modificadas)
- **AND** en `auditoria.costo_envio`, `updated_by` es el UUID del admin y `updated_by_name` es su nombre

#### Scenario: Admin agrega una nueva clave

- **WHEN** un admin hace `PUT /admin/configuracion` con body `{ "configuracion": { "tasa_descuento": "10" } }`
- **THEN** el sistema inserta una nueva fila con `clave = "tasa_descuento"`, `valor = "10"`, `updated_by = <admin_id>`, `updated_at = <timestamp actual>`
- **AND** retorna HTTP 200 con la configuración completa incluyendo la nueva clave

#### Scenario: Admin actualiza múltiples claves en una sola request

- **WHEN** un admin hace `PUT /admin/configuracion` con body `{ "configuracion": { "horario_apertura": "07:00", "horario_cierre": "23:00" } }`
- **THEN** el sistema actualiza ambas filas independientemente, cada una con su propia auditoría
- **AND** retorna HTTP 200 con toda la configuración reflejando los cambios

#### Scenario: Usuario sin rol ADMIN es rechazado en PUT

- **WHEN** un usuario sin rol ADMIN hace `PUT /admin/configuracion` con cualquier body válido
- **THEN** el sistema retorna HTTP 403 Forbidden
- **AND** no se modifica ninguna fila en la base de datos

### Requirement: Seed Initial Configuration

La migración Alembic DEBE insertar 5 parámetros de configuración iniciales para que el sistema funcione con valores por defecto sin intervención manual.

#### Scenario: Migración siembra 5 parámetros por defecto

- **WHEN** se ejecuta `alembic upgrade head` que incluye la migración de `system_config`
- **THEN** la tabla contiene exactamente 5 filas con las claves: `horario_apertura`, `horario_cierre`, `zona_entrega`, `costo_envio`, `mensaje_bienvenida`
- **AND** cada fila tiene `updated_by = NULL`
- **AND** cada fila tiene `updated_at` con la fecha y hora de ejecución de la migración

#### Scenario: Rollback de la migración elimina la tabla

- **WHEN** se ejecuta `alembic downgrade -1` sobre la migración de `system_config`
- **THEN** la tabla `system_config` se elimina completamente
- **AND** ninguna otra tabla resulta afectada

### Requirement: Página de Configuración (Frontend)

El sistema DEBE proporcionar una página en `/admin/configuracion` accesible solo para ADMIN donde se muestre un formulario con todos los parámetros de configuración y se permita guardar cambios.

#### Scenario: Admin carga la página de configuración

- **WHEN** un usuario con rol ADMIN navega a `/admin/configuracion`
- **THEN** el sistema renderiza un formulario con un campo de entrada por cada clave de configuración obtenida del backend
- **AND** cada campo muestra el valor actual obtenido de `GET /admin/configuracion`
- **AND** debajo de cada campo se muestra "Última modificación: [nombre o 'Sistema'] el [fecha]" usando los datos de `auditoria`

#### Scenario: Admin modifica y guarda configuración

- **WHEN** el admin modifica uno o más valores y hace clic en "Guardar cambios"
- **THEN** el sistema envía `PUT /admin/configuracion` con las claves modificadas
- **AND** muestra un toast de éxito: "Configuración guardada correctamente"
- **AND** los campos de auditoría se actualizan en la UI reflejando el nuevo `updated_by_name` y `updated_at`

#### Scenario: Página en estado de carga

- **WHEN** la query `useQuery(['admin', 'configuracion'], fetchConfig)` está en estado `isLoading`
- **THEN** el sistema muestra `Skeleton` lines como placeholder de los inputs mientras los datos se cargan

#### Scenario: Error al cargar la configuración

- **WHEN** la query de configuración falla con un error de red o del servidor
- **THEN** el sistema muestra un componente `ErrorDisplay` con el mensaje de error y un botón "Reintentar" que dispara `refetch()`

#### Scenario: Usuario sin rol ADMIN es redirigido

- **WHEN** un usuario sin rol ADMIN intenta acceder a `/admin/configuracion`
- **THEN** el componente `ProtectedRoute` redirige al usuario o muestra un mensaje de acceso denegado
- **AND** no se realiza ninguna llamada al endpoint de configuración

### Requirement: Navegación — Ítem Configuración en Sidebar

El sistema DEBE mostrar un ítem "Configuración" en la sección de administración del sidebar, visible solo para usuarios con rol ADMIN.

#### Scenario: Admin ve el ítem Configuración en el sidebar

- **WHEN** un usuario con rol ADMIN está autenticado
- **THEN** el sidebar muestra un ítem con etiqueta "Configuración", ícono ⚙️, y enlace a `/admin/configuracion`
- **AND** el ítem aparece en la sección "Administración" del sidebar

#### Scenario: Usuario no-ADMIN no ve el ítem Configuración

- **WHEN** un usuario sin rol ADMIN (CLIENT, STOCK, o PEDIDOS) está autenticado
- **THEN** el ítem "Configuración" NO aparece en el sidebar
