## Context

El módulo `pedidos/` se creó en Change 28 con solo el endpoint de creación. El repository tiene métodos transaccionales (create, commit, rollback) pero ningún método de lectura. Los schemas tienen `PedidoRead` y `PedidoDetail` pero `PedidoDetail` nunca se usa. El service solo tiene `crear_pedido()`.

La lógica de ownership es clave: CLIENT solo ve sus propios pedidos, ADMIN y PEDIDOS ven todos. Esto debe aplicarse tanto en listado como en detalle.

## Goals / Non-Goals

**Goals:**

- `GET /api/v1/pedidos` con paginación (skip/limit), filtro por `estado_codigo`, y role-aware
- `GET /api/v1/pedidos/{id}` con detalle completo: items (snapshots), historial ordenado ASC
- Ownership check: CLIENT solo accede a sus pedidos, ADMIN/PEDIDOS a cualquiera
- Soft-delete filter: no retornar pedidos eliminados lógicamente

**Non-Goals:**

- Transiciones de estado (eso va en Change 34 — FSM)
- Frontend (Change 30)
- Filtros por fecha (se pueden agregar después, el diseño lo soporta)

## Decisions

### 1. Eager loading con selectinload

**Decisión**: Usar `selectinload(Pedido.detalles)` y `selectinload(Pedido.historial)` en el get_by_id para evitar N+1 queries.
**Por qué**: El detalle del pedido siempre necesita items e historial. Cargarlos en una query extra es más eficiente que lazy loading con múltiples queries.

### 2. Paginación estilo skip/limit (consistente con productos)

**Decisión**: Usar `skip` y `limit` como query params, igual que el módulo de productos existente.
**Por qué**: Consistencia con el resto de la API. El frontend ya sabe manejar este formato.

### 3. Role check en service, no en router

**Decisión**: El service recibe el `User` actual y decide si filtra por `usuario_id` o no, según los roles del usuario.
**Por qué**: Mantiene la lógica de negocio en el service (no en el router). El router solo inyecta dependencias.

### 4. Historial ordenado ASC por created_at

**Decisión**: El historial en `PedidoDetail` se retorna ordenado cronológicamente (`ORDER BY created_at ASC`).
**Por qué**: El historial debe leerse como una línea de tiempo. ASC muestra la evolución natural: estado inicial → estado actual.

## Risks / Trade-offs

| Riesgo                                             | Mitigación                                              |
| -------------------------------------------------- | ------------------------------------------------------- |
| Pedido sin detalles (edge case de datos corruptos) | El service retorna lista vacía en vez de error          |
| Rendimiento en listados con muchos pedidos         | Paginación obligatoria (skip/limit) limita el resultado |
| Carga del historial completo siempre               | `selectinload` carga en una query separada, no anidada  |
