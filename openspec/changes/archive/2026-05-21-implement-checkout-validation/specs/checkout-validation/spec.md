## ADDED Requirements

### Requirement: System validates cart items before order creation

The system SHALL provide an endpoint `POST /api/v1/checkout/validar` that receives a list of cart items and returns validation results.

The request SHALL contain:

- `items`: array de `{ producto_id: string, cantidad: number, precio_snapshot: number, personalizacion: string[] }`

The response SHALL contain:

- `valido`: boolean (true if no errors, only warnings are ok)
- `errores`: string[] (blocking issues)
- `advertencias`: string[] (non-blocking notifications)
- `detalles`: ItemValidado[] (per-item validation result)

Each ItemValidado SHALL contain:

- `producto_id`: string
- `nombre`: string
- `valido`: boolean
- `errores`: string[]
- `advertencias`: string[]

#### Scenario: All items valid

- **WHEN** all items have valid products that are available, with sufficient stock and valid personalizations
- **THEN** the response has `valido: true` and empty `errores`

#### Scenario: Product does not exist

- **WHEN** an item references a producto_id that does not exist or is soft-deleted
- **THEN** the item's `valido` is false
- **AND** the error includes "Producto {id} no encontrado"

#### Scenario: Product not available

- **WHEN** an item references a product with `disponible = false`
- **THEN** the item's error includes "{nombre} no está disponible actualmente"

#### Scenario: Insufficient stock

- **WHEN** the requested cantidad exceeds stock_cantidad
- **THEN** the item's error includes "{nombre} tiene stock insuficiente (disponible: {stock}, solicitado: {cantidad})"

#### Scenario: Invalid personalization

- **WHEN** an item includes an ingrediente_id that is not associated with the product
- **THEN** the item's error includes "Ingrediente {id} no válido para {nombre}"

#### Scenario: Non-removable ingredient in personalization

- **WHEN** an item includes an ingrediente_id that exists on the product but es_removible = false
- **THEN** the item's error includes "El ingrediente {nombre} no se puede remover de {producto}"

#### Scenario: Price has changed

- **WHEN** the precio_snapshot differs from the current precio_base
- **THEN** a warning is added: "El precio de {nombre} cambió de ${snapshot} a ${actual}"
- **AND** the item's `valido` remains true (warning is non-blocking)

#### Scenario: Multiple items with different issues

- **WHEN** the request contains multiple items with different validation issues
- **THEN** all items are validated independently
- **AND** the response contains all errors and warnings for all items
