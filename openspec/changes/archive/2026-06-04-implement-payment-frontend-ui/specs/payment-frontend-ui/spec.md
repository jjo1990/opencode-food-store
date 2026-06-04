## ADDED Requirements

### Requirement: Página de checkout

The system SHALL provide a `/checkout` page accessible to authenticated CLIENT users.

#### Scenario: Access checkout page

- **WHEN** an authenticated CLIENT navigates to `/checkout`
- **THEN** the system SHALL display the checkout page with cart summary, address selector, and payment form

#### Scenario: Unauthenticated access to checkout

- **WHEN** an unauthenticated user navigates to `/checkout`
- **THEN** the system SHALL redirect to login page

### Requirement: Cart summary in checkout

The checkout page SHALL display a summary of the cart items.

#### Scenario: Checkout shows cart items

- **WHEN** the checkout page loads
- **THEN** the system SHALL display each cart item with name, quantity, unit price, and subtotal
- **AND** the system SHALL display the subtotal, shipping cost, and total

#### Scenario: Empty cart redirects to catalog

- **WHEN** the checkout page loads and the cart is empty
- **THEN** the system SHALL redirect to `/catalog` with a message

### Requirement: Address selector in checkout

The checkout page SHALL allow the user to select a delivery address.

#### Scenario: Select existing address

- **WHEN** the checkout page loads
- **THEN** the system SHALL load and display the user's saved addresses
- **AND** the user SHALL be able to select one as the delivery address

#### Scenario: No addresses saved

- **WHEN** the user has no saved addresses
- **THEN** the system SHALL display a link to add a new address

### Requirement: Payment with MercadoPago

The checkout page SHALL integrate MercadoPago Checkout API via `@mercadopago/sdk-react` for card tokenization.

#### Scenario: Successful payment

- **WHEN** the user submits the payment form with valid card data
- **WHEN** MercadoPago tokenizes the card successfully
- **WHEN** `POST /api/v1/pagos/crear` returns `status: "approved"`
- **THEN** the system SHALL show a success page with the order ID and a link to track the order

#### Scenario: Failed payment

- **WHEN** `POST /api/v1/pagos/crear` returns `status: "rejected"`
- **THEN** the system SHALL show a failure page with the error detail
- **AND** the system SHALL show a "Reintentar" button that calls `POST /api/v1/pagos/reintentar`

#### Scenario: Pending payment

- **WHEN** `POST /api/v1/pagos/crear` returns `status: "pending"`
- **THEN** the system SHALL show a pending page with a polling message
- **AND** the system SHALL poll `GET /api/v1/pagos/{pedido_id}` every 5 seconds
- **AND** when the status changes from pending, the system SHALL update the UI accordingly

### Requirement: Payment retry

The system SHALL allow retrying a rejected payment from the failure page.

#### Scenario: Retry rejected payment

- **GIVEN** a rejected payment on the checkout page
- **WHEN** the user clicks "Reintentar" with a new card token
- **THEN** the system SHALL call `POST /api/v1/pagos/reintentar`
- **AND** if successful, the system SHALL show the success page
- **AND** if rejected again, the system SHALL remain on the failure page
