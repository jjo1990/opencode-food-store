# order-fsm-transitions Specification

## Purpose

TBD - created by archiving change implement-order-fsm-transitions. Update Purpose after archive.

## Requirements

### Requirement: Avanzar estado del pedido

The system SHALL expose an endpoint `PATCH /api/v1/pedidos/{pedido_id}/avanzar` that transitions an order to a new state following the FSM rules.

#### Scenario: Valid transition by authorized role

- **GIVEN** a Pedido in `PENDIENTE` state
- **WHEN** an ADMIN sends `PATCH /api/v1/pedidos/{id}/avanzar` with `{ "nuevo_estado": "CANCELADO" }`
- **THEN** the system SHALL change `Pedido.estado_codigo` to `CANCELADO`
- **AND** the system SHALL create a `HistorialEstadoPedido` entry with `estado_desde = "PENDIENTE"`, `estado_nuevo = "CANCELADO"`, `actor_id = admin.id`
- **AND** the system SHALL return the updated Pedido

#### Scenario: Invalid transition

- **GIVEN** a Pedido in `PENDIENTE` state
- **WHEN** an ADMIN sends `PATCH /api/v1/pedidos/{id}/avanzar` with `{ "nuevo_estado": "ENTREGADO" }`
- **THEN** the system SHALL return HTTP 422 with an error describing the invalid transition

#### Scenario: Transition from terminal state

- **GIVEN** a Pedido in `ENTREGADO` state
- **WHEN** any user sends `PATCH /api/v1/pedidos/{id}/avanzar`
- **THEN** the system SHALL return HTTP 422 with an error "El pedido está en un estado terminal"

#### Scenario: Pedido not found

- **WHEN** a request is made for a non-existent pedido
- **THEN** the system SHALL return HTTP 404

### Requirement: Restringir PENDIENTE → CONFIRMADO

The system SHALL NOT allow manual transition to CONFIRMADO via the endpoint. This transition is exclusive to the webhook.

#### Scenario: Manual transition to CONFIRMADO rejected

- **GIVEN** a Pedido in `PENDIENTE` state
- **WHEN** an ADMIN sends `PATCH /api/v1/pedidos/{id}/avanzar` with `{ "nuevo_estado": "CONFIRMADO" }`
- **THEN** the system SHALL return HTTP 422 with an error "La transición a CONFIRMADO solo puede realizarse vía webhook de pago"

### Requirement: Control de roles por transición

The system SHALL validate that the user has the required role for each transition.

#### Scenario: CLIENT cancels from CONFIRMADO

- **GIVEN** a Pedido in `CONFIRMADO` state
- **WHEN** a CLIENT sends `PATCH /api/v1/pedidos/{id}/avanzar` with `{ "nuevo_estado": "CANCELADO" }`
- **THEN** the system SHALL allow the transition

#### Scenario: CLIENT tries EN_CONFIRMADO → EN_PREPARACION

- **GIVEN** a Pedido in `CONFIRMADO` state
- **WHEN** a CLIENT sends `PATCH /api/v1/pedidos/{id}/avanzar` with `{ "nuevo_estado": "EN_PREPARACION" }`
- **THEN** the system SHALL return HTTP 403

#### Scenario: Non-owner CLIENT tries to advance

- **GIVEN** a Pedido belonging to another user
- **WHEN** a CLIENT sends `PATCH /api/v1/pedidos/{id}/avanzar`
- **THEN** the system SHALL return HTTP 404

### Requirement: Restaurar stock al cancelar

When a Pedido transitions to CANCELADO from CONFIRMADO or EN_PREPARACIÖN, the system SHALL restore the stock for each product atomically.

#### Scenario: Cancel from CONFIRMADO restores stock

- **GIVEN** a Pedido in `CONFIRMADO` state with items that consumed stock
- **WHEN** an authorized user cancels the pedido
- **THEN** the system SHALL increment `Producto.stock_cantidad` by the ordered quantity for each item
- **AND** the system SHALL use `SELECT FOR UPDATE` to prevent race conditions
- **AND** the system SHALL commit all changes atomically

#### Scenario: Cancel from PENDIENTE does NOT restore stock

- **GIVEN** a Pedido in `PENDIENTE` state (stock was never decremented)
- **WHEN** an authorized user cancels the pedido
- **THEN** the system SHALL NOT modify `Producto.stock_cantidad`

### Requirement: Registrar historial de transición

Every state transition SHALL create a `HistorialEstadoPedido` entry.

#### Scenario: Historial entry created

- **WHEN** a transition is successfully executed
- **THEN** the system SHALL create a `HistorialEstadoPedido` with `estado_desde` (previous state), `estado_nuevo`, `actor_id` (current user), and `motivo` (from request, if provided)
