## ADDED Requirements

### Requirement: Cart holds a list of items

The system SHALL maintain a list of CartItem objects in the cart store.

Each CartItem SHALL contain:

- `producto_id`: string (UUID)
- `nombre`: string
- `imagen_url`: string | null
- `precio`: number
- `cantidad`: number (≥ 1)
- `personalizacion`: string[] (IDs de ingredientes a remover)

#### Scenario: Initial state is empty

- **WHEN** the cart store is initialized
- **THEN** the items array is empty

### Requirement: User can add an item to the cart

The system SHALL provide an `addItem` action that adds a product to the cart.

If the same `producto_id` already exists in the cart with the same `personalizacion`, the system SHALL increment the `cantidad` instead of adding a duplicate entry.

If the product does not exist in the cart, the system SHALL append a new CartItem.

#### Scenario: Add new product to empty cart

- **WHEN** addItem is called with { producto_id: "abc", nombre: "Pizza Margherita", precio: 1500, cantidad: 1, personalizacion: [] }
- **THEN** the cart contains 1 item with cantidad=1

#### Scenario: Add existing product increments quantity

- **WHEN** addItem is called twice with the same producto_id and personalizacion
- **THEN** the cart contains 1 item with cantidad=2

#### Scenario: Add same product with different personalization creates separate entry

- **WHEN** addItem is called with producto_id="abc", personalizacion=[] and then with producto_id="abc", personalizacion=["ingredient-1"]
- **THEN** the cart contains 2 separate items

### Requirement: User can update item quantity

The system SHALL provide an `updateQuantity` action that sets the cantidad of a specific CartItem.

If the resulting cantidad is ≤ 0, the item SHALL be removed from the cart.

#### Scenario: Update quantity to valid value

- **WHEN** updateQuantity("abc", 3) is called
- **THEN** the item's cantidad becomes 3

#### Scenario: Update quantity to zero removes item

- **WHEN** updateQuantity("abc", 0) is called
- **THEN** the item is removed from the cart

### Requirement: User can remove an item

The system SHALL provide a `removeItem` action that removes a CartItem by its producto_id and personalizacion.

#### Scenario: Remove existing item

- **WHEN** removeItem("abc", []) is called on an existing item
- **THEN** the item is removed from the cart

### Requirement: User can clear the cart

The system SHALL provide a `clearCart` action that removes all items from the cart.

#### Scenario: Clear cart with items

- **WHEN** clearCart() is called
- **THEN** the items array is empty

### Requirement: Cart is persisted to localStorage

The system SHALL persist the cart items to localStorage using Zustand's persist middleware.

The storage key SHALL be `food-store-cart`.

The cart SHALL survive browser close, page refresh, and logout/login.

#### Scenario: Cart survives page refresh

- **WHEN** items are added to the cart
- **WHEN** the page is refreshed
- **THEN** the cart items are restored from localStorage

### Requirement: Cart provides derived selectors

The system SHALL provide computed selectors for common calculations.

`totalItems` SHALL return the sum of all item quantities.
`totalPrice` SHALL return the sum of (precio × cantidad) for all items.
`getItem(producto_id, personalizacion)` SHALL return a specific CartItem or undefined.

#### Scenario: totalItems calculation

- **WHEN** the cart has 2 items (cantidad 2 and 3)
- **THEN** totalItems returns 5

#### Scenario: totalPrice calculation

- **WHEN** the cart has items: Pizza $1500 x 2, Empanada $300 x 3
- **THEN** totalPrice returns 3900 (1500*2 + 300*3)

#### Scenario: getItem finds matching item

- **WHEN** getItem("abc", []) is called and the item exists
- **THEN** it returns the CartItem

#### Scenario: getItem returns undefined for non-existent item

- **WHEN** getItem("nonexistent", []) is called
- **THEN** it returns undefined
