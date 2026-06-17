# ui-accessibility Specification

## Purpose

Especifica las mejoras de accesibilidad WCAG AA para Food Store. Cubre skip-to-content link, focus-visible global en reemplazo de focus rings, ARIA labels en icon buttons, focus trap en Modal (Tab/Shift+Tab cicla dentro, focus retorna al trigger al cerrar), semantic HTML en páginas (main, section), screen reader text para charts y secciones visuales, touch targets ≥44×44px en todos los elementos interactivos, y corrección de contraste de color (mínimo 4.5:1 para texto normal).

## ADDED Requirements

### Requirement: All icon buttons MUST have aria-label attributes

The system MUST provide descriptive `aria-label` attributes on every icon-only button to make them accessible to screen readers.

#### Scenario: Header cart button has aria-label

- **WHEN** the Header renders the cart button
- **THEN** the button has `aria-label="Carrito de compras"` or `aria-label="Carrito de compras, {N} items"` when items are present

#### Scenario: Modal close button has aria-label

- **WHEN** a Modal is open
- **THEN** the close button has `aria-label="Cerrar"`

#### Scenario: ThemeToggle has dynamic aria-label

- **WHEN** `theme` is `'light'`
- **THEN** the ThemeToggle has `aria-label="Cambiar a modo oscuro"`
- **WHEN** `theme` is `'dark'`
- **THEN** the ThemeToggle has `aria-label="Cambiar a modo claro"`

#### Scenario: Hamburger menu button has dynamic aria-label

- **WHEN** mobile menu is closed
- **THEN** the hamburger button has `aria-label="Abrir menú"`
- **WHEN** mobile menu is open
- **THEN** the hamburger button has `aria-label="Cerrar menú"`

#### Scenario: Edit and delete icon buttons have aria-labels

- **WHEN** a table row renders action buttons
- **THEN** the edit button has `aria-label="Editar"`
- **AND** the delete button has `aria-label="Eliminar"`

#### Scenario: Sidebar toggle button has aria-label

- **WHEN** the Sidebar collapse toggle is rendered
- **THEN** it has `aria-label="Colapsar menú"` or `aria-label="Expandir menú"` based on collapsed state

#### Scenario: Pagination buttons have aria-labels

- **WHEN** pagination controls are rendered
- **THEN** previous/next buttons have `aria-label="Página anterior"` and `aria-label="Página siguiente"`
- **AND** page number buttons have `aria-label="Ir a página {N}"`

---

### Requirement: All focus rings MUST use focus-visible instead of focus

The system MUST replace all `focus:ring-*` classes with `focus-visible:ring-*` so that focus rings only appear during keyboard navigation, not on mouse clicks.

#### Scenario: Keyboard Tab shows focus ring

- **WHEN** the user navigates with Tab key
- **THEN** the focused element shows a visible focus ring via `focus-visible:ring-2`

#### Scenario: Mouse click does not show focus ring

- **WHEN** the user clicks an element with the mouse
- **THEN** no focus ring appears on that element

#### Scenario: Shared components use focus-visible

- **WHEN** inspecting `Button.tsx`, `Input.tsx`, and `Modal.tsx`
- **THEN** all focus-related classes use the `focus-visible:` prefix, not `focus:`

#### Scenario: Admin page buttons use focus-visible

- **WHEN** inspecting any admin page (users, products, orders, ingredients, categories)
- **THEN** all interactive elements use `focus-visible:ring-*` instead of `focus:ring-*`

---

### Requirement: Modal MUST implement focus trap

The system MUST trap keyboard focus within the Modal when it is open, cycling Tab/Shift+Tab between the first and last focusable elements.

#### Scenario: Tab cycles within modal

- **WHEN** a Modal is open and the user presses Tab on the last focusable element
- **THEN** focus moves to the first focusable element inside the modal

#### Scenario: Shift+Tab cycles backwards within modal

- **WHEN** a Modal is open and the user presses Shift+Tab on the first focusable element
- **THEN** focus moves to the last focusable element inside the modal

#### Scenario: Tab does not escape to background elements

- **WHEN** a Modal is open and the user repeatedly presses Tab
- **THEN** focus never leaves the modal to reach elements behind the overlay

#### Scenario: Focus trap does not interfere with Escape key

- **WHEN** a Modal is open and the user presses Escape
- **THEN** the Modal closes normally via its existing Escape handler

---

### Requirement: Modal MUST return focus to trigger element on close

The system MUST save a reference to the element that triggered the Modal and restore focus to it when the Modal closes.

#### Scenario: Focus returns after modal close

- **WHEN** a user opens a Modal by clicking a button
- **AND** then closes the Modal (Escape, close button, or overlay click)
- **THEN** focus returns to the original button that opened the Modal

#### Scenario: Focus returns even on Escape close

- **WHEN** a user opens a Modal and presses Escape to close it
- **THEN** focus returns to the original trigger element

---

### Requirement: ConfirmationModal MUST inherit focus trap from Modal

The system MUST ensure `ConfirmationModal` inherits the focus trap behavior because it uses `Modal` internally.

#### Scenario: ConfirmationModal traps focus

- **WHEN** a `ConfirmationModal` is open
- **THEN** Tab cycles between the cancel and confirm buttons without escaping to the background

---

### Requirement: Touch targets MUST be at least 44×44px

The system MUST ensure all interactive elements have minimum dimensions of 44×44px to comply with WCAG 2.5.5 (AAA) target size guidelines.

#### Scenario: Button sm meets 44px minimum height

- **WHEN** a `<Button size="sm">` is rendered
- **THEN** the button has `min-h-[44px]` via adjusted padding (`px-4 py-3`)

#### Scenario: Button md meets 44px minimum height

- **WHEN** a `<Button size="md">` is rendered
- **THEN** the button has `min-h-[44px]` via adjusted padding (`px-5 py-3`)

#### Scenario: Icon buttons are 44×44px

- **WHEN** any icon-only button is rendered (cart, close, theme, menu, edit, delete)
- **THEN** the button has `min-h-[44px] min-w-[44px]` with centered content via flex

#### Scenario: CartDrawer qty buttons are 44×44px

- **WHEN** the CartDrawer quantity increase/decrease buttons are rendered
- **THEN** each button has `min-h-[44px] min-w-[44px]`

#### Scenario: Table action buttons are 44×44px

- **WHEN** action buttons (edit, delete) appear in table rows
- **THEN** each button has `min-h-[44px] min-w-[44px]`

#### Scenario: Pagination buttons are 44×44px

- **WHEN** pagination controls are rendered
- **THEN** each page number and arrow button has `min-h-[44px] min-w-[44px]`

---

### Requirement: LoginPage, RegisterPage, and DashboardPage MUST use semantic HTML

The system MUST wrap page content in proper semantic HTML elements (`<main>`, `<section>`) instead of generic `<div>` containers.

#### Scenario: LoginPage uses main and section

- **WHEN** LoginPage is rendered
- **THEN** the page content is wrapped in a `<main>` element
- **AND** the form is inside a `<section>` with an accessible heading

#### Scenario: RegisterPage uses main and section

- **WHEN** RegisterPage is rendered
- **THEN** the page content is wrapped in a `<main>` element
- **AND** the form is inside a `<section>` with an accessible heading

#### Scenario: DashboardPage uses main and section

- **WHEN** DashboardPage is rendered
- **THEN** the page content is wrapped in a `<main>` element
- **AND** stat cards, charts, and tables are inside `<section>` elements with headings

#### Scenario: NotFoundPage uses main

- **WHEN** NotFoundPage is rendered
- **THEN** the page content is wrapped in a `<main>` element

---

### Requirement: Screen reader text MUST be provided for visual-only elements

The system MUST add `sr-only` text descriptions for charts, icons, and sections that rely on visual presentation.

#### Scenario: Charts have sr-only descriptions

- **WHEN** a chart is rendered on DashboardPage or admin pages
- **THEN** there is an `sr-only` element describing the chart content (e.g., "Gráfico de ventas por día")

#### Scenario: Visual section headings have sr-only text when needed

- **WHEN** a section uses only an icon or visual indicator as heading
- **THEN** an `sr-only` text heading is provided alongside the visual indicator

#### Scenario: Table captions are accessible

- **WHEN** a data table is rendered
- **THEN** the table includes a `<caption>` element or `aria-label` describing the table content

---

### Requirement: Color contrast MUST meet WCAG AA minimum

The system MUST ensure all text elements have a contrast ratio of at least 4.5:1 against their background for normal text, and 3:1 for large text.

#### Scenario: Body text uses text-gray-500 instead of text-gray-400

- **WHEN** descriptive or secondary text is rendered on white background
- **THEN** it uses `text-gray-500` (#6b7280, 5.3:1 ratio) instead of `text-gray-400` (#9ca3af, 3.6:1 ratio)

#### Scenario: Green primary text uses primary-700

- **WHEN** green text is rendered on light backgrounds (prices, CTAs, status indicators)
- **THEN** it uses `text-primary-700` (#15803d, 5.5:1 ratio) instead of `text-primary` (#22c55e, 2.4:1 ratio)

#### Scenario: Disabled text is distinguishable

- **WHEN** form inputs or buttons are in a disabled state
- **THEN** the disabled text uses `text-gray-400` (#9ca3af) which is at least borderline distinguishable from the background

#### Scenario: Dark mode text has sufficient contrast

- **WHEN** `theme` is `'dark'`
- **THEN** body text (`dark:text-gray-300` #d1d5db on `dark:bg-gray-900` #111827) has a contrast ratio ≥ 4.5:1
- **AND** secondary text (`dark:text-gray-400` #9ca3af on `dark:bg-gray-800` #1f2937) has a contrast ratio ≥ 4.5:1

---

### Requirement: MobileDrawer MUST have ARIA attributes

The system MUST add appropriate ARIA attributes to the MobileDrawer for screen reader support.

#### Scenario: MobileDrawer has role and aria-modal

- **WHEN** the MobileDrawer is open
- **THEN** the drawer panel has `role="dialog"` and `aria-modal="true"`

#### Scenario: Overlay has aria-hidden when closed

- **WHEN** the MobileDrawer is closed
- **THEN** the overlay has `aria-hidden="true"` to hide it from screen readers
- **WHEN** the MobileDrawer is open
- **THEN** the overlay removes `aria-hidden` or sets it to `"false"`
