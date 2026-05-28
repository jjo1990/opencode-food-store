## ADDED Requirements

### Requirement: Recibir notificación IPN

The system SHALL expose a public endpoint `POST /api/v1/pagos/webhook` that accepts JSON payloads from MercadoPago IPN.

#### Scenario: Webhook received successfully

- **WHEN** MercadoPago sends a POST request to `/api/v1/pagos/webhook` with a valid JSON body
- **THEN** the system SHALL return HTTP 200 within 5 seconds (MP expects fast acknowledgment)
- **AND** the system SHALL process the notification

#### Scenario: Invalid JSON body

- **WHEN** MercadoPago sends a request with malformed JSON body
- **THEN** the system SHALL return HTTP 400

### Requirement: Validar firma del webhook

The system SHALL validate the authenticity of incoming webhook requests using the `X-Signature` header.

#### Scenario: Valid signature

- **WHEN** a webhook request arrives with a valid `X-Signature` header matching the configured `MP_WEBHOOK_SECRET`
- **THEN** the system SHALL proceed with processing

#### Scenario: Invalid or missing signature

- **WHEN** a webhook request arrives without `X-Signature` or with an invalid signature
- **THEN** the system SHALL return HTTP 401

### Requirement: Consultar estado real del pago

The system SHALL NOT trust the webhook payload alone. It SHALL query the MercadoPago API directly using `GET /v1/payments/{payment_id}` to confirm the actual payment status.

#### Scenario: Payment confirmed via MP API

- **WHEN** the webhook is received
- **AND** the system queries the MercadoPago API for the payment status
- **AND** the API returns `status = "approved"`
- **THEN** the system SHALL proceed with payment approval flow

#### Scenario: MP API call fails

- **WHEN** the webhook is received
- **AND** the query to MercadoPago API fails (timeout, network error, 5xx)
- **THEN** the system SHALL return HTTP 502

#### Scenario: MP API returns different status than webhook

- **WHEN** the webhook body says `approved` but MP API returns `rejected`
- **THEN** the system SHALL trust the MP API response, NOT the webhook body

### Requirement: Procesar pago aprobado

When the payment is confirmed as `approved`, the system SHALL atomically:

1. Update the `Pago` record with `mp_payment_id` and `mp_status = "approved"`
2. Change the `Pedido.estado_codigo` from `PENDIENTE` to `CONFIRMADO`
3. Decrement `Producto.stock_cantidad` for each item in the order
4. Create a `HistorialEstadoPedido` entry with `estado_desde = "PENDIENTE"`, `estado_nuevo = "CONFIRMADO"`, `actor_id = NULL`
5. Commit all changes atomically — if any step fails, rollback everything

#### Scenario: Payment approved — full atomic flow

- **GIVEN** a Pedido in `PENDIENTE` state with items
- **GIVEN** all products have sufficient stock
- **WHEN** the webhook confirms payment is `approved`
- **THEN** the Pedido SHALL change to `CONFIRMADO`
- **AND** `stock_cantidad` SHALL decrease by the ordered quantity for each product
- **AND** a `HistorialEstadoPedido` SHALL be created with `estado_desde = "PENDIENTE"`, `estado_nuevo = "CONFIRMADO"`, `actor_id = NULL`

#### Scenario: Insufficient stock at approval time

- **GIVEN** a Pedido in `PENDIENTE` state
- **GIVEN** one product has less stock than the ordered quantity
- **WHEN** the webhook confirms payment is `approved`
- **THEN** the system SHALL rollback the entire transaction
- **AND** the Pedido SHALL remain `PENDIENTE`

### Requirement: Procesar pago rechazado o pendiente

When the payment status is `rejected` or `pending`, the system SHALL update the `Pago` record but SHALL NOT change the `Pedido` state.

#### Scenario: Payment rejected

- **WHEN** the webhook confirms payment status is `rejected`
- **THEN** the system SHALL update `Pago.mp_status = "rejected"`
- **AND** the Pedido SHALL remain `PENDIENTE`

#### Scenario: Payment pending

- **WHEN** the webhook confirms payment status is `pending`
- **THEN** the system SHALL update `Pago.mp_status = "pending"`
- **AND** the Pedido SHALL remain `PENDIENTE`

### Requirement: Idempotencia en webhooks

The system SHALL NOT process the same webhook notification more than once.

#### Scenario: Duplicate webhook

- **GIVEN** a webhook for `mp_payment_id` was already processed
- **WHEN** another webhook arrives with the same `mp_payment_id`
- **THEN** the system SHALL return HTTP 200 immediately without re-processing
