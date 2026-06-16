# admin-users Specification

## Purpose

TBD - created by archiving change implement-admin-users-ui. Update Purpose after archive.

## Requirements

### Requirement: User List with Pagination

El sistema MUST mostrar una tabla paginada de usuarios accesible en `/admin/users` para usuarios con rol ADMIN.

#### Scenario: Admin views first page of users

- **GIVEN** existen 30 usuarios registrados en el sistema
- **WHEN** un ADMIN navega a `/admin/users`
- **THEN** el sistema muestra una tabla con 15 usuarios (page size default)
- **AND** muestra controles de paginación "Anterior" y "Siguiente"
- **AND** muestra "Mostrando 1–15 de 30"
- **AND** el botón "Anterior" está deshabilitado (primera página)

#### Scenario: Admin navigates to next page

- **GIVEN** el admin está en la página 1 de usuarios
- **WHEN** hace click en "Siguiente"
- **THEN** el sistema carga y muestra los usuarios 16–30
- **AND** el botón "Anterior" se habilita
- **AND** el botón "Siguiente" se deshabilita (última página)

#### Scenario: Table columns

- **WHEN** la tabla de usuarios se renderiza con datos
- **THEN** muestra columnas: ID (UUID truncado), Nombre, Email, Roles (badges), Estado (activo/inactivo), Fecha de registro
- **AND** cada rol se muestra como un badge de color (ADMIN=rojo, STOCK=azul, PEDIDOS=amarillo, CLIENT=verde)
- **AND** el estado "activo" se muestra con badge verde, "inactivo" con badge rojo

---

### Requirement: Search by Name or Email

El sistema MUST permitir buscar usuarios por nombre o email con debounce de 300ms.

#### Scenario: Admin searches by partial name

- **GIVEN** existen usuarios "María García" y "Mario López"
- **WHEN** el admin escribe "Mar" en el input de búsqueda
- **THEN** después de 300ms sin escribir, la tabla se actualiza mostrando ambos usuarios
- **AND** la página se resetea a 1

#### Scenario: Admin searches by email

- **GIVEN** existe un usuario con email "maria@test.com"
- **WHEN** el admin escribe "maria@test" en el input de búsqueda
- **THEN** la tabla muestra solo ese usuario

#### Scenario: Admin clears search

- **GIVEN** hay una búsqueda activa filtrando resultados
- **WHEN** el admin borra el contenido del input de búsqueda
- **THEN** la tabla vuelve a mostrar todos los usuarios sin filtro de búsqueda

#### Scenario: Debounce prevents premature API call

- **WHEN** el admin escribe rápidamente 5 caracteres
- **THEN** solo se realiza UNA llamada a la API 300ms después del último keystroke

---

### Requirement: Filter by Role

El sistema MUST permitir filtrar usuarios por rol.

#### Scenario: Admin filters by ADMIN role

- **GIVEN** existen usuarios con distintos roles
- **WHEN** el admin selecciona "ADMIN" en el filtro de rol
- **THEN** la tabla muestra solo usuarios que tienen el rol ADMIN
- **AND** la página se resetea a 1

#### Scenario: Admin clears role filter

- **GIVEN** hay un filtro de rol activo
- **WHEN** el admin selecciona la opción "Todos los roles"
- **THEN** la tabla muestra usuarios de todos los roles

#### Scenario: Role filter options

- **WHEN** se renderiza el selector de rol
- **THEN** muestra opciones: "Todos los roles", "ADMIN", "STOCK", "PEDIDOS", "CLIENT"

---

### Requirement: Filter by Status

El sistema MUST permitir filtrar usuarios por estado (activo/inactivo/todos).

#### Scenario: Admin filters by inactive users

- **GIVEN** existen usuarios activos e inactivos
- **WHEN** el admin selecciona "Inactivos" en el filtro de estado
- **THEN** la tabla muestra solo usuarios inactivos

#### Scenario: Default status filter

- **WHEN** el admin navega a `/admin/users` por primera vez
- **THEN** el filtro de estado está en "Activos" por defecto

#### Scenario: Admin selects "Todos"

- **WHEN** el admin selecciona "Todos" en el filtro de estado
- **THEN** la tabla muestra usuarios activos e inactivos

---

### Requirement: User Edit Modal

El sistema MUST abrir un modal de edición al hacer click en una fila de usuario activo.

#### Scenario: Admin clicks on active user row

- **GIVEN** el admin ve la tabla de usuarios con datos
- **WHEN** hace click en la fila de un usuario activo
- **THEN** se abre un modal con título "Editar Usuario"
- **AND** los campos se rellenan con los datos actuales del usuario

#### Scenario: Edit modal fields

- **GIVEN** el modal de edición está abierto
- **THEN** muestra campos: Nombre completo (text input), Email (email input), Teléfono (text input)
- **AND** muestra checkboxes para cada rol: CLIENT, STOCK, PEDIDOS, ADMIN (marcados según roles actuales)
- **AND** muestra un toggle "Usuario activo" (on/off según estado actual)
- **AND** muestra botones "Cancelar" y "Guardar cambios"

#### Scenario: Admin updates user name and saves

- **GIVEN** el modal de edición está abierto para el usuario "Juan Pérez"
- **WHEN** el admin cambia el nombre a "Juan Pablo Pérez"
- **AND** hace click en "Guardar cambios"
- **THEN** se envía PUT a `/admin/usuarios/{id}` con el nuevo nombre
- **AND** la tabla se actualiza mostrando el nuevo nombre
- **AND** se muestra toast "Usuario actualizado correctamente"
- **AND** el modal se cierra

#### Scenario: Admin cancels edit

- **GIVEN** el modal de edición está abierto con cambios sin guardar
- **WHEN** el admin hace click en "Cancelar"
- **THEN** el modal se cierra sin enviar cambios
- **AND** la tabla no se modifica

#### Scenario: Edit modal loads user detail

- **GIVEN** el admin hace click en una fila
- **WHEN** se está cargando el detalle del usuario desde la API
- **THEN** el modal muestra un spinner de carga
- **AND** los campos del formulario aparecen deshabilitados

#### Scenario: Edit modal detail fetch error

- **GIVEN** el admin hace click en una fila
- **WHEN** la API retorna error al obtener el detalle
- **THEN** el modal muestra un mensaje de error con botón "Reintentar"

---

### Requirement: Role Removal Critical Confirmation

El sistema MUST pedir confirmación explícita cuando se intenta quitar el rol ADMIN a un usuario.

#### Scenario: Admin unchecks ADMIN role

- **GIVEN** el modal de edición está abierto para un usuario con rol ADMIN
- **WHEN** el admin desmarca el checkbox "ADMIN"
- **THEN** NO se permite guardar inmediatamente
- **AND** aparece un mensaje de confirmación: "¿Estás seguro? Si quitás el rol ADMIN, este usuario perderá acceso al panel de administración."
- **AND** muestra botones "Confirmar" y "Cancelar"

#### Scenario: Admin confirms ADMIN removal

- **GIVEN** el mensaje de confirmación por quitar rol ADMIN está visible
- **WHEN** el admin hace click en "Confirmar"
- **THEN** el mensaje de confirmación desaparece
- **AND** el botón "Guardar cambios" se habilita normalmente

#### Scenario: Admin cancels ADMIN removal

- **GIVEN** el mensaje de confirmación por quitar rol ADMIN está visible
- **WHEN** el admin hace click en "Cancelar"
- **THEN** el checkbox ADMIN vuelve a marcarse
- **AND** el mensaje de confirmación desaparece

#### Scenario: No confirmation when ADMIN role not affected

- **GIVEN** el usuario editado NO tiene rol ADMIN
- **WHEN** el admin modifica otros campos o roles
- **THEN** no se muestra confirmación adicional
- **AND** el botón Guardar está siempre habilitado

---

### Requirement: User Deactivation (Soft Delete)

El sistema MUST permitir desactivar usuarios con confirmación previa.

#### Scenario: Admin deactivates user from modal

- **GIVEN** el modal de edición está abierto para un usuario activo
- **WHEN** el admin hace click en "Desactivar usuario"
- **THEN** se abre un modal de confirmación: "¿Desactivar a {nombre}? El usuario no podrá acceder al sistema pero sus datos se conservarán."

#### Scenario: Admin confirms deactivation

- **GIVEN** el modal de confirmación de desactivación está abierto
- **WHEN** el admin hace click en "Confirmar"
- **THEN** se envía DELETE a `/admin/usuarios/{id}`
- **AND** la tabla se actualiza mostrando el usuario como inactivo/eliminado
- **AND** se muestra toast de éxito
- **AND** los modales se cierran

#### Scenario: Admin cancels deactivation

- **GIVEN** el modal de confirmación de desactivación está abierto
- **WHEN** el admin hace click en "Cancelar"
- **THEN** no se envía DELETE
- **AND** se regresa al modal de edición

---

### Requirement: User Reactivation

El sistema MUST permitir reactivar usuarios previamente desactivados.

#### Scenario: Admin clicks on soft-deleted user

- **GIVEN** un usuario está marcado como soft-deleted (fila gris)
- **WHEN** el admin hace click en la fila
- **THEN** se abre un modal de confirmación: "¿Reactivar a {nombre}? El usuario recuperará el acceso al sistema."
- **AND** NO se abre el modal de edición (no se puede editar un usuario eliminado)
- **AND** muestra botones "Confirmar" y "Cancelar"

#### Scenario: Admin confirms reactivation

- **GIVEN** el modal de confirmación de reactivación está abierto
- **WHEN** el admin hace click en "Confirmar"
- **THEN** se envía PATCH a `/admin/usuarios/{id}/reactivar`
- **AND** la tabla se actualiza mostrando el usuario como activo
- **AND** se muestra toast de éxito

#### Scenario: Soft-deleted user visual distinction

- **GIVEN** la tabla de usuarios tiene datos
- **WHEN** un usuario está soft-deleted
- **THEN** su fila se muestra con fondo gris claro (`bg-gray-50`)
- **AND** el nombre aparece tachado (`line-through`)
- **AND** el texto es gris claro (`text-gray-400`)
- **AND** se muestra un badge adicional "Eliminado"

---

### Requirement: Loading, Error, and Empty States

El sistema MUST manejar correctamente los estados de carga, error y vacío.

#### Scenario: Loading state

- **GIVEN** el admin navega a `/admin/users`
- **WHEN** los datos están cargándose
- **THEN** se muestra un skeleton loader con 8 filas simuladas

#### Scenario: Error state

- **GIVEN** la API retorna error 500 al cargar usuarios
- **WHEN** la query falla
- **THEN** se muestra mensaje "Error al cargar usuarios" con botón "Reintentar"

#### Scenario: Empty state with filters

- **GIVEN** no hay usuarios que coincidan con los filtros activos
- **WHEN** la tabla intenta renderizar
- **THEN** se muestra "No se encontraron usuarios con esos filtros."

#### Scenario: Empty state without filters

- **GIVEN** no existen usuarios en el sistema
- **WHEN** la tabla intenta renderizar
- **THEN** se muestra "No hay usuarios registrados."

---

### Requirement: All Fields Optional in Update

El sistema MUST enviar solo los campos modificados en la actualización (todos los campos del schema `AdminUserUpdateRequest` son opcionales).

#### Scenario: Admin changes only phone number

- **GIVEN** el modal de edición está abierto
- **WHEN** el admin modifica solo el teléfono y guarda
- **THEN** el PUT incluye solo `{ telefono: "nuevo_numero" }` en el body
- **AND** los demás campos no se envían (o se envían con su valor actual, backend ignora nulls)

#### Scenario: Update error handling

- **GIVEN** el admin envía una actualización
- **WHEN** la API retorna error (ej. 422 por email duplicado)
- **THEN** se muestra toast con el mensaje de error
- **AND** el modal de edición permanece abierto para corregir
