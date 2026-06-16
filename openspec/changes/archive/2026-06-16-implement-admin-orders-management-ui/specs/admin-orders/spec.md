# admin-orders Specification

## Purpose

Interfaz de gestión de pedidos en el panel de administración, accesible en `/admin/orders` para usuarios con roles ADMIN o PEDIDOS. Permite listar, filtrar, buscar y visualizar en detalle todos los pedidos del sistema, así como transicionar pedidos entre estados según las reglas de la máquina de estados (FSM).

## Requirements

### Requirement: Order List with Pagination

El sistema MUST mostrar una tabla paginada de pedidos accesible en `/admin/orders` para usuarios con rol ADMIN o PEDIDOS.

#### Scenario: Admin views first page of orders

- **GIVEN** existen 50 pedidos registrados en el sistema
- **WHEN** un ADMIN navega a `/admin/orders`
- **THEN** el sistema muestra una tabla con 20 pedidos (page size default)
- **AND** muestra controles de paginación "Anterior" y "Siguiente"
- **AND** muestra "Mostrando 1–20 de 50"
- **AND** el botón "Anterior" está deshabilitado (primera página)

#### Scenario: Admin navigates to next page

- **GIVEN** el admin está en la página 1 de pedidos con 50 totales
- **WHEN** hace click en "Siguiente"
- **THEN** el sistema carga y muestra los pedidos 21–40
- **AND** el botón "Anterior" se habilita
- **AND** el botón "Siguiente" permanece habilitado

#### Scenario: Table columns

- **WHEN** la tabla de pedidos se renderiza con datos
- **THEN** muestra columnas: ID (UUID truncado), Cliente, Monto ($ formateado), Estado (OrderBadge), Fecha (DD/MM/YYYY)
- **AND** cada estado se muestra con el badge de color correspondiente (PENDIENTE=amber, CONFIRMADO=blue, EN_PREPARACION=indigo, EN_CAMINO=purple, ENTREGADO=green, CANCELADO=red)
- **AND** la columna "Cliente" muestra el nombre del cliente o "—" si no tiene nombre registrado
- **AND** cada fila tiene un botón "Ver detalle" en la columna de acciones

---

### Requirement: Search by Order ID

El sistema MUST permitir buscar pedidos por ID con debounce de 300ms.

#### Scenario: Admin searches by full order ID

- **GIVEN** existe un pedido con ID `a1b2c3d4-...`
- **WHEN** el admin escribe `a1b2c3d4` en el input de búsqueda por ID
- **THEN** después de 300ms sin escribir, la tabla se actualiza mostrando solo ese pedido
- **AND** la página se resetea a 1

#### Scenario: Admin searches by partial order ID

- **GIVEN** existen pedidos con IDs que contienen `abc`
- **WHEN** el admin escribe `abc` en el input de búsqueda por ID
- **THEN** la tabla muestra todos los pedidos cuyo ID contenga `abc`

#### Scenario: Admin clears order ID search

- **GIVEN** hay una búsqueda por ID activa filtrando resultados
- **WHEN** el admin borra el contenido del input de búsqueda por ID
- **THEN** la tabla vuelve a mostrar todos los pedidos sin filtro de ID

#### Scenario: Debounce prevents premature API call

- **WHEN** el admin escribe rápidamente 5 caracteres en el input de búsqueda por ID
- **THEN** solo se realiza UNA llamada a la API 300ms después del último keystroke

---

### Requirement: Search by Client Name

El sistema MUST permitir buscar pedidos por nombre de cliente con debounce de 300ms.

#### Scenario: Admin searches by partial client name

- **GIVEN** existen pedidos de clientes "María García" y "Mario López"
- **WHEN** el admin escribe "Mar" en el input de búsqueda por cliente
- **THEN** después de 300ms, la tabla muestra los pedidos de ambos clientes
- **AND** la página se resetea a 1

#### Scenario: Admin searches by full client name

- **GIVEN** existe un pedido del cliente "Juan Pérez"
- **WHEN** el admin escribe "Juan Pérez" en el input de búsqueda por cliente
- **THEN** la tabla muestra solo los pedidos de ese cliente

#### Scenario: Admin clears client name search

- **GIVEN** hay una búsqueda por cliente activa
- **WHEN** el admin borra el contenido del input de búsqueda por cliente
- **THEN** la tabla vuelve a mostrar todos los pedidos sin filtro de cliente

---

### Requirement: Filter by Order State

El sistema MUST permitir filtrar pedidos por estado.

#### Scenario: Admin filters by PENDIENTE state

- **GIVEN** existen pedidos en distintos estados
- **WHEN** el admin selecciona "Pendiente" en el filtro de estado
- **THEN** la tabla muestra solo pedidos en estado PENDIENTE
- **AND** la página se resetea a 1

#### Scenario: Default state filter

- **WHEN** el admin navega a `/admin/orders` por primera vez
- **THEN** el filtro de estado está en "Todos" por defecto (sin filtrar)

#### Scenario: Admin clears state filter

- **GIVEN** hay un filtro de estado activo
- **WHEN** el admin selecciona "Todos" en el filtro de estado
- **THEN** la tabla muestra pedidos de todos los estados

#### Scenario: State filter options

- **WHEN** se renderiza el selector de estado
- **THEN** muestra opciones: "Todos", "Pendiente", "Confirmado", "En Preparación", "En Camino", "Entregado", "Cancelado"

---

### Requirement: Filter by Date Range

El sistema MUST permitir filtrar pedidos por rango de fechas de creación.

#### Scenario: Admin filters by date range

- **GIVEN** existen pedidos creados en distintas fechas
- **WHEN** el admin selecciona `fecha_inicio = 2026-06-01` y `fecha_fin = 2026-06-15`
- **THEN** la tabla muestra solo pedidos creados entre esas fechas (inclusive)
- **AND** la página se resetea a 1

#### Scenario: Admin sets only start date

- **GIVEN** existen pedidos creados en distintas fechas
- **WHEN** el admin selecciona solo `fecha_inicio = 2026-06-10` (sin fecha_fin)
- **THEN** la tabla muestra pedidos creados desde el 10 de junio en adelante

#### Scenario: Admin sets only end date

- **GIVEN** existen pedidos creados en distintas fechas
- **WHEN** el admin selecciona solo `fecha_fin = 2026-06-10` (sin fecha_inicio)
- **THEN** la tabla muestra pedidos creados hasta el 10 de junio inclusive

#### Scenario: Admin clears date filters

- **GIVEN** hay filtros de fecha activos
- **WHEN** el admin borra los valores de fecha_inicio y fecha_fin
- **THEN** la tabla muestra todos los pedidos sin filtro de fecha

---

### Requirement: Hover Preview on Row

El sistema MUST mostrar un preview de datos rápidos al hacer hover sobre una fila de la tabla.

#### Scenario: Admin hovers over order row

- **GIVEN** la tabla de pedidos está renderizada con datos
- **WHEN** el admin hace hover sobre una fila de pedido
- **THEN** se muestra un tooltip con: nombre del cliente, dirección de entrega
- **AND** el tooltip aparece a la derecha de la fila sin bloquear la vista de otras filas

#### Scenario: Admin hovers over order with missing data

- **GIVEN** un pedido no tiene cliente_nombre ni direccion_calle
- **WHEN** el admin hace hover sobre esa fila
- **THEN** el tooltip muestra "Cliente: No registrado" y "Dirección: No especificada"

#### Scenario: Admin moves mouse away from row

- **GIVEN** el tooltip de hover preview está visible
- **WHEN** el admin mueve el mouse fuera de la fila
- **THEN** el tooltip desaparece inmediatamente

---

### Requirement: Order Detail Modal

El sistema MUST abrir un modal de detalle al hacer click en "Ver detalle" en una fila de la tabla.

#### Scenario: Admin clicks "Ver detalle" on an order

- **GIVEN** el admin ve la tabla de pedidos con datos
- **WHEN** hace click en "Ver detalle" en la fila de un pedido
- **THEN** se abre un modal con título "Pedido #{id_truncado}"
- **AND** muestra el OrderBadge con el estado actual
- **AND** muestra la información del pedido: monto total, fecha, cliente, dirección

#### Scenario: Detail modal shows items with snapshots

- **GIVEN** el modal de detalle está abierto para un pedido con 3 items
- **THEN** muestra una tabla con columnas: Producto (nombre_snapshot), Precio unitario, Cantidad, Subtotal
- **AND** cada fila muestra el nombre y precio tal como estaban al momento del pedido (snapshot)

#### Scenario: Detail modal shows history timeline

- **GIVEN** el modal de detalle está abierto para un pedido con historial de cambios de estado
- **THEN** muestra el componente `OrderTimeline` con todas las transiciones registradas
- **AND** cada entrada del timeline muestra: estado, fecha/hora, actor, motivo (si existe)

#### Scenario: Detail modal action buttons for non-terminal orders

- **GIVEN** el modal de detalle está abierto para un pedido en estado PENDIENTE, CONFIRMADO, EN_PREPARACION o EN_CAMINO
- **THEN** el footer del modal muestra dos botones: "Avanzar Estado" y "Cancelar Pedido"

#### Scenario: Detail modal for terminal orders

- **GIVEN** el modal de detalle está abierto para un pedido en estado ENTREGADO o CANCELADO
- **THEN** el modal muestra un mensaje "Pedido en estado final"
- **AND** NO se muestran los botones "Avanzar Estado" ni "Cancelar Pedido"

#### Scenario: Detail modal loading state

- **GIVEN** el admin hace click en "Ver detalle"
- **WHEN** los datos del detalle están cargándose desde la API
- **THEN** el modal muestra un `<Spinner />` centrado

#### Scenario: Detail modal error state

- **GIVEN** el admin hace click en "Ver detalle"
- **WHEN** la API retorna error al obtener el detalle
- **THEN** el modal muestra un mensaje de error con botón "Reintentar"
- **AND** el botón "Reintentar" dispara un refetch del detalle

#### Scenario: Admin closes detail modal

- **GIVEN** el modal de detalle está abierto
- **WHEN** el admin hace click en la X, en el overlay, o presiona Escape
- **THEN** el modal se cierra y se regresa a la tabla de pedidos

---

### Requirement: Change Order State Modal with FSM Validation

El sistema MUST abrir un modal de cambio de estado al hacer click en "Avanzar Estado" o "Cancelar Pedido", mostrando solo las transiciones válidas según la máquina de estados y los roles del usuario.

#### Scenario: Admin opens change state modal via "Avanzar Estado"

- **GIVEN** el modal de detalle está abierto para un pedido en estado CONFIRMADO
- **WHEN** el admin (rol ADMIN) hace click en "Avanzar Estado"
- **THEN** se cierra el modal de detalle y se abre el modal de cambio de estado
- **AND** el dropdown de estados muestra solo las transiciones válidas para CONFIRMADO: "En Preparación" y "Cancelado"

#### Scenario: Admin opens change state modal via "Cancelar Pedido"

- **GIVEN** el modal de detalle está abierto para un pedido en estado CONFIRMADO
- **WHEN** el admin hace click en "Cancelar Pedido"
- **THEN** se abre el modal de cambio de estado con "Cancelado" pre-seleccionado en el dropdown

#### Scenario: FSM dropdown filters by user role — PEDIDOS role

- **GIVEN** un usuario con rol PEDIDOS abre el modal de cambio de estado para un pedido EN_PREPARACION
- **THEN** el dropdown muestra solo "En Camino" (CANCELADO requiere rol ADMIN para este estado)
- **AND** "Cancelado" NO aparece en el dropdown

#### Scenario: FSM dropdown filters by user role — ADMIN role

- **GIVEN** un usuario con rol ADMIN abre el modal de cambio de estado para un pedido EN_PREPARACION
- **THEN** el dropdown muestra "En Camino" y "Cancelado"

#### Scenario: FSM dropdown for PENDIENTE state

- **GIVEN** un usuario con rol ADMIN abre el modal de cambio de estado para un pedido PENDIENTE
- **THEN** el dropdown muestra solo "Cancelado" (única transición válida desde PENDIENTE)

#### Scenario: FSM dropdown for EN_CAMINO state

- **GIVEN** un usuario con rol ADMIN abre el modal de cambio de estado para un pedido EN_CAMINO
- **THEN** el dropdown muestra solo "Entregado" (CANCELADO no es válido desde EN_CAMINO)

#### Scenario: Motivo field when destination is CANCELADO

- **GIVEN** el modal de cambio de estado está abierto
- **WHEN** el admin selecciona "Cancelado" en el dropdown
- **THEN** aparece un textarea obligatorio etiquetado "Motivo de cancelación"
- **AND** el placeholder dice "Describí el motivo de la cancelación (obligatorio)"
- **AND** el botón "Confirmar" está deshabilitado hasta que se ingrese texto en el motivo

#### Scenario: Motivo field when destination is NOT CANCELADO

- **GIVEN** el modal de cambio de estado está abierto
- **WHEN** el admin selecciona "En Preparación", "En Camino" o "Entregado" en el dropdown
- **THEN** el textarea de motivo es opcional
- **AND** el placeholder dice "Motivo del cambio (opcional)"
- **AND** el botón "Confirmar" está habilitado sin necesidad de llenar el motivo

#### Scenario: Admin confirms state change

- **GIVEN** el modal de cambio de estado está abierto con un estado destino válido
- **WHEN** el admin hace click en "Confirmar"
- **THEN** se envía PATCH a `/admin/pedidos/{id}/estado` con `{ nuevo_estado, motivo }`
- **AND** se muestra un spinner en el botón mientras se procesa
- **AND** al completar exitosamente: se cierra el modal, se muestra toast "Estado del pedido actualizado correctamente", la tabla se actualiza

#### Scenario: State change fails with error

- **GIVEN** el admin intenta un cambio de estado
- **WHEN** la API retorna error (ej. 422 por transición inválida, 403 por permisos insuficientes)
- **THEN** se muestra un toast con el mensaje de error de la API
- **AND** el modal de cambio de estado permanece abierto para corregir

#### Scenario: Admin cancels state change

- **GIVEN** el modal de cambio de estado está abierto
- **WHEN** el admin hace click en "Cancelar"
- **THEN** el modal se cierra sin enviar cambios
- **AND** se regresa al modal de detalle del pedido

---

### Requirement: Loading, Error, and Empty States

El sistema MUST manejar correctamente los estados de carga, error y vacío.

#### Scenario: Loading state on initial page load

- **GIVEN** el admin navega a `/admin/orders`
- **WHEN** los datos están cargándose
- **THEN** se muestra un skeleton loader con 8 filas simulando la tabla

#### Scenario: Error state on API failure

- **GIVEN** la API retorna error 500 al cargar pedidos
- **WHEN** la query falla
- **THEN** se muestra mensaje "Error al cargar pedidos" con botón "Reintentar"

#### Scenario: Empty state with active filters

- **GIVEN** no hay pedidos que coincidan con los filtros activos
- **WHEN** la tabla intenta renderizar
- **THEN** se muestra "No se encontraron pedidos con esos filtros."

#### Scenario: Empty state without filters

- **GIVEN** no existen pedidos en el sistema
- **WHEN** la tabla intenta renderizar
- **THEN** se muestra "No hay pedidos registrados en el sistema."

---

### Requirement: Filter Reset on Filter Change

Todo cambio en cualquier filtro (búsqueda por ID, búsqueda por cliente, estado, fecha) MUST resetear la página a 1.

#### Scenario: Admin changes estado filter

- **GIVEN** el admin está en la página 3 de pedidos
- **WHEN** selecciona un nuevo estado en el filtro
- **THEN** la página se resetea a 1
- **AND** la query se dispara con `page=1` y el nuevo filtro de estado

#### Scenario: Admin changes date range

- **GIVEN** el admin está en la página 2 de pedidos
- **WHEN** selecciona una nueva fecha_inicio
- **THEN** la página se resetea a 1

#### Scenario: Admin types in search input

- **GIVEN** el admin está en la página 5 de pedidos
- **WHEN** escribe un término de búsqueda (y pasan los 300ms de debounce)
- **THEN** la página se resetea a 1

---

### Requirement: Admin and PEDIDOS Role Access

El sistema MUST restringir el acceso a `/admin/orders` a usuarios con roles ADMIN o PEDIDOS.

#### Scenario: ADMIN user accesses orders management

- **WHEN** un usuario con rol ADMIN navega a `/admin/orders`
- **THEN** la página de gestión de pedidos se renderiza normalmente

#### Scenario: PEDIDOS user accesses orders management

- **WHEN** un usuario con rol PEDIDOS navega a `/admin/orders`
- **THEN** la página de gestión de pedidos se renderiza normalmente
- **AND** el dropdown de cambio de estado solo muestra transiciones permitidas para el rol PEDIDOS

#### Scenario: CLIENT user attempts to access orders management

- **WHEN** un usuario con rol CLIENT intenta navegar a `/admin/orders`
- **THEN** el `ProtectedRoute` redirige o muestra mensaje de acceso denegado
- **AND** no se realiza ninguna llamada a la API admin de pedidos
