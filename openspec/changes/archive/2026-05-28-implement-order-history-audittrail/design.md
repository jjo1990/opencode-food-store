## Context

El modelo `HistorialEstadoPedido` ya existe con campos: id, pedido_id, estado_desde, estado_nuevo, actor_id (nullable FK → User), motivo, created_at. Ya se registran entradas al:

1. Crear pedido (PENDIENTE, actor=user)
2. Webhook aprobado (CONFIRMADO, actor=NULL = SISTEMA)
3. FSM avanzar estado (cualquier transición, actor=user)

Lo que falta: un endpoint dedicado que devuelva estas entradas con el nombre del actor resuelto.

## Goals / Non-Goals

**Goals:**

- Endpoint `GET /api/v1/pedidos/{id}/historial` con orden cronológico ascendente
- Cada entrada incluye `actor_nombre` (resuelto de `User.full_name` o "SISTEMA")
- Ownership check: CLIENT ve solo su pedido, ADMIN/PEDIDOS ven todos

**Non-Goals:**

- No se modifica el historial (append-only, no UPDATE/DELETE)
- No se modifican endpoints existentes

## Decisions

### Decision 1: JOIN con User para obtener nombre

Se hace un `LEFT JOIN` con la tabla `User` para resolver `actor_nombre`. Si `actor_id IS NULL`, se retorna "SISTEMA".

### Decision 2: Nuevo schema separado

Se crea `HistorialResponse` (no reutilizar `HistorialRead` existente) porque el endpoint actual de detalle usa `HistorialRead` con `actor_id` solamente. El nuevo schema tiene `actor_nombre` adicional.
