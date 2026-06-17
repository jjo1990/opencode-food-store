# ui-responsive-layout Specification

## Purpose
TBD - created by archiving change implement-ui-responsiveness-and-ux. Update Purpose after archive.
## Requirements
### Requirement: Header MUST show hamburger button on mobile

The system MUST render a hamburger menu button in the Header that is only visible on mobile viewports.

#### Scenario: Hamburger button visible on mobile

- **WHEN** the viewport width is less than 1024px (lg breakpoint)
- **THEN** the Header renders a hamburger button with class `lg:hidden`
- **AND** the button has `aria-label="Abrir menú"` when mobile menu is closed
- **AND** the button has `aria-label="Cerrar menú"` when mobile menu is open

#### Scenario: Hamburger button hidden on desktop

- **WHEN** the viewport width is 1024px or greater
- **THEN** the hamburger button is hidden (`lg:hidden` applies, so it's display:none)

#### Scenario: Hamburger click toggles mobile menu

- **WHEN** the user clicks the hamburger button
- **THEN** `uiStore.mobileMenuOpen` toggles between `true` and `false`
- **AND** the `MobileDrawer` opens or closes accordingly

---

### Requirement: Sidebar MUST be hidden on mobile and visible on desktop

The system MUST control Sidebar visibility with responsive classes so it only appears on desktop screens.

#### Scenario: Sidebar hidden below lg breakpoint

- **WHEN** the viewport width is less than 1024px
- **THEN** the desktop Sidebar instance has class `hidden lg:block` and is not visible

#### Scenario: Sidebar visible at lg breakpoint and above

- **WHEN** the viewport width is 1024px or greater
- **THEN** the desktop Sidebar is visible (`lg:block` overrides `hidden`)

#### Scenario: Sidebar accepts className prop

- **WHEN** the Layout renders `<Sidebar className="hidden lg:block" />`
- **THEN** the Sidebar component applies the provided className alongside its own classes

---

### Requirement: MobileDrawer MUST slide from left with overlay

The system MUST provide a `MobileDrawer` component that animates in from the left side with a semi-transparent overlay.

#### Scenario: MobileDrawer opens on mobile menu toggle

- **WHEN** `uiStore.mobileMenuOpen` is set to `true`
- **THEN** the MobileDrawer panel slides in from the left (`translate-x-0`)
- **AND** a semi-transparent overlay (`bg-black/50`) appears behind it

#### Scenario: MobileDrawer panel content is Sidebar

- **WHEN** the MobileDrawer is open
- **THEN** the drawer contains a `Sidebar` component with `collapsed={false}` (always fully expanded in mobile)

#### Scenario: MobileDrawer uses portal rendering

- **WHEN** the MobileDrawer renders
- **THEN** its content is portaled to `document.body` to avoid z-index issues

#### Scenario: MobileDrawer has transition animation

- **WHEN** the MobileDrawer opens or closes
- **THEN** the transition uses `transition-transform duration-300` for smooth sliding

---

### Requirement: MobileDrawer MUST close on overlay click

The system MUST close the MobileDrawer when the user clicks the dark overlay outside the panel.

#### Scenario: Overlay click closes drawer

- **WHEN** the MobileDrawer is open and the user clicks the overlay area (outside the panel)
- **THEN** `uiStore.setMobileMenuOpen(false)` is called
- **AND** the drawer slides out and the overlay fades away

#### Scenario: Panel click does not close drawer

- **WHEN** the MobileDrawer is open and the user clicks inside the panel content
- **THEN** the drawer remains open (event propagation is stopped)

---

### Requirement: MobileDrawer MUST close on Escape key

The system MUST close the MobileDrawer when the user presses the Escape key.

#### Scenario: Escape key closes drawer

- **WHEN** the MobileDrawer is open and the user presses the Escape key
- **THEN** `uiStore.setMobileMenuOpen(false)` is called

#### Scenario: Escape key has no effect when drawer is closed

- **WHEN** the MobileDrawer is closed and the user presses the Escape key
- **THEN** nothing happens (no error, no state change)

---

### Requirement: Body scroll MUST be locked when MobileDrawer is open

The system MUST prevent background page scrolling while the MobileDrawer is open.

#### Scenario: Body scroll locked when drawer opens

- **WHEN** `mobileMenuOpen` becomes `true`
- **THEN** `document.body.style.overflow` is set to `'hidden'`

#### Scenario: Body scroll restored when drawer closes

- **WHEN** `mobileMenuOpen` becomes `false`
- **THEN** `document.body.style.overflow` is restored to its original value

#### Scenario: Body scroll restored on unmount

- **WHEN** the MobileDrawer component unmounts while open
- **THEN** `document.body.style.overflow` is restored (cleanup in useEffect return)

---

### Requirement: ThemeToggle MUST be visible in Header

The system MUST include the `ThemeToggle` component inside the Header so users can switch between light and dark mode from any page.

#### Scenario: ThemeToggle is present in Header

- **WHEN** the application renders the Header on any page
- **THEN** the `ThemeToggle` button is visible among the header actions (cart, user menu, etc.)

#### Scenario: ThemeToggle is accessible on mobile

- **WHEN** the viewport is mobile (< 1024px)
- **THEN** the `ThemeToggle` remains visible in the Header alongside the hamburger button

---

### Requirement: Layout MUST have skip-to-content link as first focusable element

The system MUST render a skip-to-content link before the Header that becomes visible on keyboard focus.

#### Scenario: Skip link is the first tabbable element

- **WHEN** the user presses Tab on any page
- **THEN** the first element to receive focus is the "Saltar al contenido" skip link

#### Scenario: Skip link navigates to main content

- **WHEN** the user activates the skip link (Enter)
- **THEN** focus moves to the `<main id="main-content">` element

#### Scenario: Skip link is visually hidden when not focused

- **WHEN** the skip link does not have focus
- **THEN** it is visually hidden with `sr-only` class
- **AND** when focused, it becomes visible with `focus:not-sr-only` styles

---

### Requirement: Navigation component MUST be integrated into Sidebar

The system MUST render the `Navigation` component inside the `Sidebar`, both on desktop and inside the `MobileDrawer`.

#### Scenario: Navigation renders inside desktop Sidebar

- **WHEN** on desktop (≥1024px)
- **THEN** `Navigation` is rendered as a child of the desktop `Sidebar`

#### Scenario: Navigation renders inside MobileDrawer

- **WHEN** on mobile (< 1024px) and the MobileDrawer is open
- **THEN** `Navigation` is rendered as a child of the `Sidebar` inside the `MobileDrawer`

#### Scenario: Navigation links navigate and close mobile drawer

- **WHEN** the user taps a navigation link inside the MobileDrawer
- **THEN** the page navigates to the target route
- **AND** the MobileDrawer closes automatically

