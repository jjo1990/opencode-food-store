# payment-creation Specification

## Purpose

TBD - created by archiving change implement-payment-creation. Update Purpose after archive.

## Requirements

### Requirement: Creación de pago con MercadoPago

El sistema SHALL proveer un endpoint `POST /api/v1/pagos/crear` que procese un pago a través de MercadoPago Checkout API usando un token de tarjeta generado por el frontend.

#### Scenario: Pago aprobado

- **WHEN** un cliente autenticado envía `POST /api/v1/pagos/crear` con un `pedido_id` válido (PENDIENTE, propio) y un `card_token` válido de MercadoPago
- **THEN** el sistema genera un `idempotency_key` UUID
- **AND** el sistema llama a MercadoPago SDK con `payment.create()` usando: items del pedido con snapshots, transaction_amount = total, external_reference = pedido_id, idempotency_key
- **AND** si MP responde con status="approved", el sistema registra el pago en tabla `pago` con mp_status="approved", mp_payment_id, external_reference, idempotency_key
- **AND** retorna HTTP 201 con `{ mp_payment_id, status: "approved", status_detail }`
- **AND** el estado del pedido NO cambia (sigue PENDIENTE — lo cambia el webhook)

#### Scenario: Pago rechazado

- **WHEN** MP responde con status="rejected"
- **THEN** el sistema registra el pago en tabla `pago` con mp_status="rejected"
- **AND** retorna HTTP 200 con `{ mp_payment_id, status: "rejected", status_detail }`
- **AND** el pedido permanece PENDIENTE (el cliente puede reintentar)

#### Scenario: Pago pendiente (efectivo)

- **WHEN** MP responde con status="pending"
- **THEN** el sistema registra el pago en tabla `pago` con mp_status="pending"
- **AND** retorna HTTP 200 con `{ mp_payment_id, status: "pending", status_detail }`

#### Scenario: Pedido no encontrado

- **WHEN** el `pedido_id` no existe, está soft-deleted, o no está en estado PENDIENTE
- **THEN** el sistema retorna HTTP 422 con error descriptivo

#### Scenario: Pedido no pertenece al usuario

- **WHEN** el `pedido_id` pertenece a otro usuario
- **THEN** el sistema retorna HTTP 404

#### Scenario: Idempotencia en duplicados

- **WHEN** una misma `idempotency_key` se envía dos veces (reintento del frontend)
- **THEN** el sistema detecta la clave duplicada y retorna el pago existente sin llamar a MP nuevamente
