# order-history-audittrail Specification

## Purpose

TBD - created by archiving change implement-order-history-audittrail. Update Purpose after archive.

## Requirements

### Requirement: Consultar historial de estados del pedido

The system SHALL expose an endpoint `GET /api/v1/pedidos/{pedido_id}/historial` that returns the state transition history for an order.

#### Scenario: CLIENT queries own order history

- **GIVEN** a Pedido with historial entries
- **WHEN** the owner CLIENT sends `GET /api/v1/pedidos/{id}/historial`
- **THEN** the system SHALL return HTTP 200 with an array ordered by `created_at ASC`
- **AND** each entry SHALL include `estado_desde`, `estado_nuevo`, `actor_id`, `actor_nombre`, `motivo`, `created_at`
- **AND** entries where `actor_id IS NULL` SHALL have `actor_nombre = "SISTEMA"`

#### Scenario: ADMIN queries any order history

- **WHEN** an ADMIN sends `GET /api/v1/pedidos/{id}/historial` for any pedido
- **THEN** the system SHALL return the historial regardless of ownership

#### Scenario: Non-owner CLIENT queries

- **WHEN** a CLIENT sends `GET /api/v1/pedidos/{id}/historial` for another user's pedido
- **THEN** the system SHALL return HTTP 404

#### Scenario: Historian entries are append-only

- **GIVEN** existing historial entries for a pedido
- **THEN** the endpoint SHALL only support GET (no POST/PUT/DELETE for historial)
