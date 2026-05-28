## Context

El módulo `pagos/` ya existe con:

- `POST /api/v1/pagos/crear` — crea un pago en MP y registra en BD
- `POST /api/v1/pagos/webhook` — procesa notificaciones IPN de MP
- Modelo `Pago` con relación 1:N hacia `Pedido` (un pedido puede tener múltiples intentos de pago)
- El campo `mp_payment_id` es UNIQUE en BD (pero nullable para intentos fallidos sin ID de MP)

Ahora necesitamos:

1. Exponer el historial de pagos de un pedido
2. Permitir reintentar pagos rechazados creando un nuevo registro Pago con nueva `idempotency_key`

## Goals / Non-Goals

**Goals:**

- Endpoint `GET /api/v1/pagos/{pedido_id}` que retorna todos los pagos asociados a un pedido
- Endpoint `POST /api/v1/pagos/reintentar` que crea un nuevo intento de pago cuando el último fue rechazado
- Ownership check: el usuario solo ve/reintenta sus propios pagos (ADMIN ve todo)

**Non-Goals:**

- No se implementan campañas de descuento ni cupones en el reintento
- No se modifica el endpoint `POST /api/v1/pagos/crear` existente
- No se implementa polling automático desde frontend (eso es frontend, Change 36)

## Decisions

### Decision 1: Endpoint GET en mismo router de pagos

El endpoint GET se agrega al router existente de `pagos/` bajo el mismo prefijo `/api/v1/pagos/`. Cohesión: toda la lógica de pagos en un solo router.

### Decision 2: Un schema para response de historial

Se crea `PagoHistoryItem` con los campos relevantes de Pago (mp_payment_id, mp_status, status_detail, created_at) y `PagoHistoryResponse` con un array de items.

### Decision 3: El reintento reusa la lógica de crear_pago

En lugar de duplicar la lógica de llamada a MP SDK, el método `reintentar_pago` valida que haya un pago previo rechazado, luego construye el payload de MP con los mismos items del pedido (usando detalles ya persistidos) y llama a `self.sdk.payment().create()`.

### Decision 4: Validación de estado para reintento

Solo se permite reintentar si:

- Pedido existe y no está soft-deleted
- Pedido está en estado PENDIENTE (no fue aprobado ni cancelado)
- Hay al menos un pago previo rechazado (no approved)
- El usuario es propietario del pedido (o ADMIN)

### Decision 5: Misma idempotencia con nueva key

Cada reintento genera un nuevo `idempotency_key` UUID. La idempotencia funciona igual que en `crear_pago`: si la misma key se reenvía, retorna el pago existente. Como cada reintento tiene key única, no hay colisión.

## Risks / Trade-offs

| Risk                                       | Mitigation                                                                             |
| ------------------------------------------ | -------------------------------------------------------------------------------------- |
| **Reintentar un pago que ya fue aprobado** | Validar que último pago NO sea "approved"; si lo es, rechazar con 422                  |
| **Pedido avanzó de estado**                | Si pedido ya no está PENDIENTE, rechazar el reintento                                  |
| **MP rechaza el reintento**                | Se registra como nuevo Pago con status "rejected" y el cliente puede intentar de nuevo |
| **Card token expirado**                    | El frontend debe generar un nuevo token con el SDK de MP antes de reintentar           |
