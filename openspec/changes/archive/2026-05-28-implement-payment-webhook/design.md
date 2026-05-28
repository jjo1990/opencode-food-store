## Context

El módulo `pagos/` ya existe con un endpoint `POST /api/v1/pagos/crear` que:

- Recibe un `pedido_id` y `card_token`
- Crea una preferencia de pago en MercadoPago vía SDK
- Registra un registro `Pago` en BD con `idempotency_key` y `mp_status`

Pero el sistema **nunca recibe la respuesta asincrónica** de MercadoPago. El webhook IPN es el mecanismo por el cual MP notifica el resultado real del pago. Sin esto:

- Pedidos quedan en PENDIENTE para siempre
- Stock nunca se descuenta
- No se puede implementar la FSM de pedidos (Change 34)

## Goals / Non-Goals

**Goals:**

- Recibir notificaciones IPN de MercadoPago en `POST /api/v1/pagos/webhook`
- Validar autenticidad del webhook via `X-Signature`
- Consultar API de MP para confirmar estado real (nunca confiar en el body)
- Si `approved`: transacción atómica que actualiza Pago, avanza Pedido a CONFIRMADO, descuenta stock, registra historial
- Si `rejected`/`pending`: solo actualizar `mp_status` en Pago
- Idempotencia total (mismo payment_id no se procesa dos veces)

**Non-Goals:**

- No se implementan reintentos de pago desde el webhook (eso es Change 33)
- No se implementan transiciones FSM adicionales (eso es Change 34)
- No se implementa UI de frontend para pagos (eso es Change 36)
- No se modifican endpoints existentes

## Decisions

### Decision 1: Sin autenticación en el webhook

El endpoint `POST /api/v1/pagos/webhook` NO lleva autenticación JWT porque MercadoPago no puede enviar tokens de sesión. La seguridad se delega a:

1. **Firma `X-Signature`**: validación del header contra `MP_WEBHOOK_SECRET`
2. **Consulta de verificación**: llamar GET a MP API para confirmar estado (nunca confiar solo en el body del webhook)

### Decision 2: Verificación contra API de MercadoPago

**Alternativa considerada**: Confiar solo en el body del webhook.
**Descartada por**: Es un riesgo de seguridad conocido — un atacante podría simular un webhook falso.
**Decisión**: Siempre hacer GET `https://api.mercadopago.com/v1/payments/{payment_id}` con el access token para verificar el estado real. Si la API no responde, retornar 502 y dejar que MP reintente.

### Decision 3: Transacción manual (no UoW)

El proyecto no usa Unit of Work. Los servicios manejan `commit()`/`rollback()` manualmente (patrón existente en `pedidos/service.py`). Mantenemos consistencia con ese patrón.

### Decision 4: SELECT FOR UPDATE para stock

Al decrementar stock, usamos `SELECT ... FOR UPDATE` para evitar race conditions. Mismo patrón usado en `pedidos/service.py` para la validación de stock durante creación de pedido.

### Decision 5: Mismo service, distinto método

El nuevo método `procesar_webhook()` se agrega a `PagoService` existente en lugar de crear un service nuevo. Cohesión: toda la lógica de pagos en un solo service.

### Decision 6: Actor SISTEMA en historial

Cuando el webhook produce una transición PENDIENTE → CONFIRMADO, el `actor_id` en `HistorialEstadoPedido` se deja NULL para representar "SISTEMA" (la transición no fue hecha por un usuario humano). El frontend/timeline muestra "SISTEMA" cuando `actor_id IS NULL`.

## Risks / Trade-offs

| Risk                                                                                        | Mitigation                                                                                                                        |
| ------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| **Webhook falso**: atacante envía webhooks maliciosos                                       | Validación `X-Signature` + consulta verificación a MP API                                                                         |
| **Race condition**: webhook llega mientras payment-creation aún no commiteó el Pago         | Idempotencia por `mp_payment_id` — si el Pago no existe aún, ignorar                                                              |
| **Stock insuficiente**: entre creación del pedido y aprobación del pago, se vendió el stock | Rollback total de la transacción + log. Pedido queda en PENDIENTE                                                                 |
| **MP API caída**: no se puede verificar el estado real                                      | Retornar 502 → MP reintenta automáticamente el webhook                                                                            |
| **Webhook duplicado**: MP envía el mismo evento múltiples veces                             | Idempotencia: si `mp_payment_id` ya tiene `mp_status` seteado, retornar 200 sin procesar                                          |
| **Timeouts**: MP espera respuesta rápida (< 5s)                                             | Responder 200 inmediatamente, procesar lógica pesada dentro de la misma request (es rápido — consultas SQL + 1 llamada HTTP a MP) |

## Flujo del webhook

```
MercadoPago                      Food Store
    │                                │
    │  POST /api/v1/pagos/webhook    │
    │  { data.id, type, action }     │
    │──────────────────────────────> │
    │                                │
    │                           ┌────┤
    │                           │ 1. Validar X-Signature
    │                           │ 2. Extraer payment_id del body
    │                           │ 3. GET /v1/payments/{id} → MP API
    │                           │    (confirmar status real)
    │                           │ 4. Buscar Pago por mp_payment_id
    │                           │ 5. Si ya procesado → 200 (idempotencia)
    │                           │ 6. Según status real:
    │                           │    approved → transacción atómica:
    │                           │      a. Actualizar Pago.mp_status
    │                           │      b. UPDATE pedido SET estado = CONFIRMADO
    │                           │      c. SELECT ... FOR UPDATE producto
    │                           │      d. UPDATE producto SET stock -= cantidad
    │                           │      e. INSERT historial_estado
    │                           │      f. COMMIT
    │                           │    rejected/pending → solo Pago.mp_status
    │                           └────┤
    │                                │
    │  200 OK (ack)                  │
    │<────────────────────────────── │
```
