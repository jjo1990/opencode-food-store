# ui-animations Specification

## Purpose

Especifica las animaciones y transiciones de Food Store. Cubre el PageTransition wrapper con fadeIn (opacity + translateY), keyframes custom en tailwind.config, configuración de animaciones de toast en react-hot-toast, transiciones hover en filas de tabla, y transiciones de sidebar/drawer.

## ADDED Requirements

### Requirement: PageTransition MUST fade in content on mount

The system MUST provide a `PageTransition` wrapper component that animates page content with a fade-in effect when the route changes.

#### Scenario: Content fades in on page load

- **WHEN** a page wrapped in `<PageTransition>` mounts
- **THEN** the content animates from `opacity: 0` to `opacity: 1`
- **AND** the content simultaneously animates `translateY` from `4px` to `0`

#### Scenario: Animation duration is 300ms

- **WHEN** the fadeIn animation plays
- **THEN** the animation duration is 300ms with an `ease-out` timing function

#### Scenario: PageTransition wraps Outlet in Layout

- **WHEN** the Layout renders the main content area
- **THEN** the `<Outlet />` is wrapped in a `<PageTransition>` component

---

### Requirement: fadeIn keyframe MUST be defined in Tailwind config

The system MUST define a custom `fadeIn` keyframe in `tailwind.config.ts` under `theme.extend.keyframes`.

#### Scenario: fadeIn keyframe exists in config

- **WHEN** inspecting `tailwind.config.ts`
- **THEN** `theme.extend.keyframes.fadeIn` is defined with `0% { opacity: '0', transform: 'translateY(4px)' }` and `100% { opacity: '1', transform: 'translateY(0)' }`

#### Scenario: animate-fadeIn class is available

- **WHEN** `theme.extend.animation.fadeIn` is defined as `'fadeIn 0.3s ease-out'`
- **THEN** the class `animate-fadeIn` can be used on any element and triggers the animation

---

### Requirement: Toast MUST have enter and exit animations configured

The system MUST configure `react-hot-toast` with appropriate enter and exit animations for a polished user experience.

#### Scenario: Toast enters with animation

- **WHEN** a toast is triggered
- **THEN** the toast appears with a smooth enter animation (slide from top by default from react-hot-toast)

#### Scenario: Toast exits with animation

- **WHEN** a toast is dismissed or expires
- **THEN** the toast disappears with a smooth exit animation (fade out by default)

#### Scenario: Toast animations respect reduced motion

- **WHEN** the user has `prefers-reduced-motion: reduce` enabled
- **THEN** toast animations should be disabled or minimized

---

### Requirement: Table rows MUST animate on hover

The system MUST add a smooth color transition to table rows when hovered.

#### Scenario: Table row background transitions on hover

- **WHEN** the user hovers over a table row
- **THEN** the row background color changes with a `transition-colors duration-150` effect

#### Scenario: Transition does not affect layout

- **WHEN** the hover transition plays
- **THEN** only colors change (background, text) and no layout shift occurs

---

### Requirement: Sidebar collapse MUST use smooth transition

The system MUST animate the Sidebar width change when toggling between collapsed and expanded states.

#### Scenario: Sidebar width transitions smoothly

- **WHEN** `sidebarCollapsed` changes from `false` to `true`
- **THEN** the Sidebar width animates with `transition-all duration-300`

#### Scenario: Sidebar text/icons hide during collapse

- **WHEN** the Sidebar collapses
- **THEN** text labels fade or hide while icons remain visible, using the existing collapse transition

---

### Requirement: MobileDrawer MUST have smooth open/close transition

The system MUST animate the MobileDrawer panel sliding in from the left and the overlay fading in.

#### Scenario: Panel slides from left on open

- **WHEN** `<MobileDrawer isOpen={true}>`
- **THEN** the panel uses `transition-transform duration-300` to slide from `-translate-x-full` to `translate-x-0`

#### Scenario: Overlay fades in on open

- **WHEN** `<MobileDrawer isOpen={true}>`
- **THEN** the overlay uses `transition-opacity duration-300` to fade from `opacity-0` to `opacity-100`

#### Scenario: Panel slides out on close

- **WHEN** `<MobileDrawer isOpen={false}>`
- **THEN** the panel slides back to `-translate-x-full` and the overlay fades to `opacity-0`
