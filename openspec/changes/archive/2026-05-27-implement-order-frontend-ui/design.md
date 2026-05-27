## Context

El frontend tiene:

- Patrón FSD establecido con entities → hooks → features → pages
- API client module en `shared/api/` con Axios + interceptores JWT
- Shared components: Skeleton, EmptyState, ErrorDisplay, Pagination, Modal, Badge (via Button variant)
- Rutas protegidas con ProtectedRoute + allowedRoles
- Header con navegación dinámica por rol

Lo que NO existe:

- Entity `order` (ni types ni hooks)
- API module para pedidos
- Componentes de visualización de pedidos (listado, detalle, timeline)
- Ruta `/orders` para CLIENT
- Contenido real en `/pedidos` (es un stub)

## Goals / Non-Goals

**Goals:**

- API module `shared/api/pedidosApi.ts` (fetchOrders, fetchOrder)
- Entity `entities/order/` (Order types, useOrders, useOrder hooks)
- `OrderList` component: tabla responsive con badges de estado por color
- `OrderDetail` component: modal expandible con timeline visual + snapshots
- `OrderConfirmation` component: pantalla post-creación
- Páginas `/orders` y `/orders/:id` para CLIENT
- Actualizar `/pedidos` y agregar `/pedidos/:id` para PEDIDOS/ADMIN
- Timeline visual con markers: PENDIENTE → CONFIRMADO → EN_PREP → EN_CAMINO → ENTREGADO

**Non-Goals:**

- Botones de acción "Avanzar Estado" (eso va en Change 34 — FSM)
- Botón "Pagar" (Change 36 — payment UI)
- Notificaciones toast post-creación (ya las maneja TanStack Query)
- Cancelar pedido desde UI (Change 34)

## Decisions

### 1. OrderDetail como modal, no página separada

**Decisión**: El detalle se abre en un modal/drawer desde la lista, usando el componente Modal compartido.
**Por qué**: Es más rápido y fluido que navegar a otra página. Consistente con el patrón de direcciones (AddressList → AddressForm modal).
**Excepción**: Si el usuario llega directo a `/orders/:id`, se renderiza una página completa con el mismo contenido.

### 2. Badges de estado con colores semánticos

**Decisión**: Cada estado tiene un color específico:

- PENDIENTE → yellow/amber
- CONFIRMADO → blue
- EN_PREPARACION → indigo
- EN_CAMINO → purple
- ENTREGADO → green (success)
- CANCELADO → red (danger)

**Por qué**: El color comunica el estado instantáneamente, sin necesidad de leer el texto.

### 3. Timeline visual como componente separado

**Decisión**: El `OrderTimeline` es un componente compartido que renderiza la secuencia de estados con conectores verticales, checkmarks y timestamps.
**Por qué**: Es reutilizable en detalle de pedido (CLIENT), admin, y potencialmente en notificaciones.

### 4. Ordenamiento DESC por created_at en listados

**Decisión**: Los pedidos más recientes aparecen primero (orden natural para el usuario).
**Por qué**: El usuario siempre quiere ver su último pedido primero. El backend ya ordena así.

## Risks / Trade-offs

| Riesgo                                             | Mitigación                                                   |
| -------------------------------------------------- | ------------------------------------------------------------ |
| Timeline con muchos estados se ve apretado         | Scroll vertical con altura máxima `max-h-96 overflow-y-auto` |
| Modal de detalle con mucha información abruma      | Separar en secciones: Info general → Items → Timeline        |
| CLIENT sin pedidos anteriores (empty state)        | EmptyState con ilustración y CTA "Ir al catálogo"            |
| La API de pedidos puede cambiar en Changes futuros | Los hooks encapsulan la API, solo cambiar el api module      |
