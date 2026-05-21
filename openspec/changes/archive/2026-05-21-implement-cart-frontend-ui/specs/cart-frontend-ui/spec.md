## ADDED Requirements

### Requirement: Header shows cart button with item count

The system SHALL display a cart button in the Header with a badge showing the total number of items.

The badge SHALL use the cart store's `getTotalItems` selector.
The badge SHALL be a small red circle with white text, positioned at the top-right of the cart icon.
The cart button SHALL be visible to all users (authenticated or not).
Clicking the cart button SHALL open the CartDrawer.

#### Scenario: Cart badge shows correct count

- **WHEN** the cart has 3 items (total quantity 5)
- **THEN** the badge displays "5"

#### Scenario: Empty cart shows no badge

- **WHEN** the cart is empty
- **THEN** the cart icon is shown without a badge

### Requirement: CartDrawer slides in from the right

The system SHALL provide a CartDrawer component that slides in from the right edge of the screen.

The drawer SHALL have:

- An overlay (semi-transparent black) that closes the drawer on click
- A white panel with title "Mi Carrito" and a close (X) button
- Smooth slide animation using Tailwind `translate-x` and `transition-transform`
- A list of CartItemRow components
- A CartSummary footer with subtotal, envío, total, and action buttons
- Full width on mobile (100vw), max-w-lg on desktop

#### Scenario: Open drawer

- **WHEN** the user clicks the cart button in the header
- **THEN** the drawer slides in from the right with animation

#### Scenario: Close drawer via overlay

- **WHEN** the drawer is open and the user clicks the overlay
- **THEN** the drawer slides out

#### Scenario: Close drawer via X button

- **WHEN** the drawer is open and the user clicks the X button
- **THEN** the drawer slides out

### Requirement: CartDrawer shows each item with controls

The CartDrawer SHALL display each cart item with:

- Product image (small thumbnail)
- Product name
- Unit price formatted in ARS
- Quantity controls: minus (-) and plus (+) buttons
- Quantity number between the controls
- Line total (precio × cantidad)
- Remove button (trash icon or X)
- If the item has ingredients removed (personalizacion), show them as small text: "Sin: [ingrediente1], [ingrediente2]"
- Disabled minus button at quantity 1 (prevents going below 1 via minus)

#### Scenario: Update quantity via plus

- **WHEN** the user clicks the plus (+) button on an item
- **THEN** the quantity increases by 1
- **AND** the line total updates

#### Scenario: Update quantity via minus

- **WHEN** the user clicks the minus (-) button on an item with quantity > 1
- **THEN** the quantity decreases by 1

#### Scenario: Remove item

- **WHEN** the user clicks the remove button on an item
- **THEN** the item is removed from the cart immediately

### Requirement: CartDrawer shows totals and actions

The CartDrawer SHALL display a summary section at the bottom with:

- Subtotal: sum of (precio × cantidad) for all items
- Envío: flat rate (currently $0 for minimum viable)
- Total: subtotal + envío
- "Vaciar carrito" button (with confirmation dialog using Modal)
- "Ir a pagar" button (primary CTA, currently navigates to a placeholder)

#### Scenario: Empty cart shows empty state

- **WHEN** the cart is empty and the drawer is opened
- **THEN** the drawer shows "Tu carrito está vacío" with a "¡Explorar productos!" link to /catalog

#### Scenario: Clear cart with confirmation

- **WHEN** the user clicks "Vaciar carrito"
- **THEN** a confirmation modal appears: "¿Vaciar carrito?" / "Se eliminarán todos los items" / buttons "Cancelar" y "Vaciar"
- **WHEN** the user confirms
- **THEN** the cart is cleared and the drawer shows empty state

### Requirement: Product detail has functional add-to-cart

The ProductDetail component SHALL have a working "Agregar al carrito" button that adds the product to the cart store.

The button SHALL be disabled if the product is not available.
Upon add, the system SHALL show a success toast ("Agregado al carrito").

#### Scenario: Add available product to cart

- **WHEN** the user clicks "Agregar al carrito" on an available product
- **THEN** the product is added to the cart store (via addItem)
- **AND** a toast "Agregado al carrito" is shown

#### Scenario: Add unavailable product

- **WHEN** the product is not available (disponible = false)
- **THEN** the "Agregar al carrito" button is disabled

### Requirement: Cart is responsive

The CartDrawer SHALL adapt to mobile screens:

- Full width (w-screen) on mobile
- Max width (max-w-lg) on desktop (md breakpoint)
- Touch-friendly buttons (minimum 44px touch target)

#### Scenario: Mobile drawer

- **WHEN** the drawer is open on a screen < 768px
- **THEN** the drawer takes the full screen width
