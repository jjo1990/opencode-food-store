# payment-query-and-retry Specification

## Purpose

TBD - created by archiving change implement-payment-query-and-retry. Update Purpose after archive.

## Requirements

### Requirement: Consultar historial de pagos

The system SHALL expose an endpoint `GET /api/v1/pagos/{pedido_id}` that returns the payment history for a given order.

#### Scenario: Successful query — client owns the order

- **WHEN** an authenticated client sends `GET /api/v1/pagos/{pedido_id}` where the pedido belongs to them
- **THEN** the system SHALL return HTTP 200 with an array of payment records
- **AND** each payment SHALL include `mp_payment_id`, `mp_status`, `status_detail`, and `created_at`
- **AND** the array SHALL be ordered by `created_at DESC` (most recent first)

#### Scenario: Successful query — admin

- **WHEN** an authenticated ADMIN sends `GET /api/v1/pagos/{pedido_id}`
- **THEN** the system SHALL return all payments for that pedido regardless of ownership

#### Scenario: Pedido not found

- **WHEN** the pedido does not exist or is soft-deleted
- **THEN** the system SHALL return HTTP 404

#### Scenario: Pedido belongs to another user

- **WHEN** a non-admin user queries payments for another user's pedido
- **THEN** the system SHALL return HTTP 404

#### Scenario: No payments exist for pedido

- **WHEN** the pedido exists but has no associated payments
- **THEN** the system SHALL return HTTP 200 with an empty array

### Requirement: Reintentar pago rechazado

The system SHALL expose an endpoint `POST /api/v1/pagos/reintentar` that allows a client to create a new payment attempt when the previous one was rejected.

#### Scenario: Successful retry

- **GIVEN** a pedido in `PENDIENTE` state
- **GIVEN** the last payment for that pedido has `mp_status = "rejected"`
- **WHEN** the client sends `POST /api/v1/pagos/reintentar` with `{ pedido_id, card_token }`
- **THEN** the system SHALL generate a new `idempotency_key`
- **AND** the system SHALL call `MercadoPago SDK payment.create()` with the pedido items
- **AND** the system SHALL INSERT a new `Pago` record with the new status
- **AND** the system SHALL return HTTP 201 with `{ mp_payment_id, status, status_detail }`

#### Scenario: Retry when last payment was approved

- **GIVEN** the last payment for a pedido has `mp_status = "approved"`
- **WHEN** the client sends `POST /api/v1/pagos/reintentar`
- **THEN** the system SHALL return HTTP 422 with an error "El pago ya fue aprobado"

#### Scenario: Retry for non-PENDIENTE pedido

- **GIVEN** a pedido that is in `CONFIRMADO` or any state other than `PENDIENTE`
- **WHEN** the client sends `POST /api/v1/pagos/reintentar`
- **THEN** the system SHALL return HTTP 422

#### Scenario: Retry by non-owner

- **GIVEN** a pedido belonging to another user
- **WHEN** a non-admin client sends `POST /api/v1/pagos/reintentar`
- **THEN** the system SHALL return HTTP 404

#### Scenario: Retry with invalid token

- **WHEN** the client sends `POST /api/v1/pagos/reintentar` with an empty or invalid `card_token`
- **THEN** the system SHALL return HTTP 422 with validation error
