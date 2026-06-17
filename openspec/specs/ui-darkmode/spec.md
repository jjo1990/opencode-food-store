# ui-darkmode Specification

## Purpose
TBD - created by archiving change implement-ui-responsiveness-and-ux. Update Purpose after archive.
## Requirements
### Requirement: Tailwind config MUST enable class-based dark mode

The system MUST configure `darkMode: 'class'` in `tailwind.config.ts` so that dark variants are activated by the presence of the `dark` class on the `<html>` element.

#### Scenario: darkMode is set to class in config

- **WHEN** inspecting `tailwind.config.ts`
- **THEN** the configuration contains `darkMode: 'class'`

#### Scenario: dark: prefixes compile correctly

- **WHEN** a component uses `className="bg-white dark:bg-gray-900"`
- **THEN** the `dark:bg-gray-900` class compiles and is available in the final CSS

---

### Requirement: ThemeToggle MUST render sun icon in dark mode and moon icon in light mode

The system MUST provide a `ThemeToggle` component that displays a sun SVG icon when the theme is `dark` and a moon SVG icon when the theme is `light`, indicating the action that will occur on click.

#### Scenario: ThemeToggle shows moon icon in light mode

- **WHEN** `uiStore.theme` is `'light'`
- **THEN** the `ThemeToggle` renders a moon SVG icon
- **AND** the button's `aria-label` is "Cambiar a modo oscuro"

#### Scenario: ThemeToggle shows sun icon in dark mode

- **WHEN** `uiStore.theme` is `'dark'`
- **THEN** the `ThemeToggle` renders a sun SVG icon
- **AND** the button's `aria-label` is "Cambiar a modo claro"

#### Scenario: ThemeToggle is placed in Header

- **WHEN** the application loads on any page
- **THEN** the `ThemeToggle` button is visible in the `Header` component

---

### Requirement: uiStore MUST persist theme to localStorage

The system MUST save the user's theme preference to localStorage so it survives page reloads.

#### Scenario: Theme persists after page reload

- **WHEN** the user toggles theme to `'dark'`
- **AND** the page is reloaded
- **THEN** `uiStore.theme` is `'dark'`
- **AND** the `<html>` element has the `dark` class

#### Scenario: First visit defaults to light theme

- **WHEN** a user visits the application for the first time (no localStorage entry)
- **THEN** `uiStore.theme` defaults to `'light'`
- **AND** the `<html>` element does NOT have the `dark` class

---

### Requirement: Toggle action MUST switch theme and update html class

The system MUST toggle between `'light'` and `'dark'` when `toggleTheme()` is called and MUST add or remove the `dark` class on `document.documentElement`.

#### Scenario: Toggle from light to dark

- **WHEN** `uiStore.theme` is `'light'` and `toggleTheme()` is called
- **THEN** `uiStore.theme` becomes `'dark'`
- **AND** the `<html>` element gains the class `dark`

#### Scenario: Toggle from dark to light

- **WHEN** `uiStore.theme` is `'dark'` and `toggleTheme()` is called
- **THEN** `uiStore.theme` becomes `'light'`
- **AND** the `dark` class is removed from the `<html>` element

---

### Requirement: Shared components MUST support dark mode variants

The system MUST apply `dark:` color variants to all shared components so they adapt to dark theme.

#### Scenario: Button has dark variants

- **WHEN** `theme` is `'dark'`
- **THEN** `Button` renders with `dark:ring-offset-gray-900` and appropriate dark background/text colors

#### Scenario: Card has dark variants

- **WHEN** `theme` is `'dark'`
- **THEN** `Card` renders with `dark:bg-gray-800 dark:border-gray-700`

#### Scenario: Input has dark variants

- **WHEN** `theme` is `'dark'`
- **THEN** `Input` renders with `dark:bg-gray-800 dark:border-gray-600 dark:text-gray-100`

#### Scenario: Badge has dark variants

- **WHEN** `theme` is `'dark'`
- **THEN** `Badge` adjusts background opacity for dark mode (e.g., `dark:bg-green-900/30 dark:text-green-300`)

#### Scenario: Modal has dark variants

- **WHEN** `theme` is `'dark'`
- **THEN** `Modal` content renders with `dark:bg-gray-800` and the overlay remains `bg-black/50`

#### Scenario: EmptyState has dark variants

- **WHEN** `theme` is `'dark'`
- **THEN** `EmptyState` renders with `dark:bg-gray-800 dark:text-gray-300`

#### Scenario: ErrorDisplay has dark variants

- **WHEN** `theme` is `'dark'`
- **THEN** `ErrorDisplay` renders with `dark:bg-red-900/20 dark:text-red-300`

#### Scenario: Skeleton and SkeletonTable have dark variants

- **WHEN** `theme` is `'dark'`
- **THEN** `Skeleton` renders with `dark:bg-gray-700` instead of `bg-gray-200`

#### Scenario: Spinner has dark variant

- **WHEN** `theme` is `'dark'`
- **THEN** `Spinner` border color adjusts for visibility on dark backgrounds

#### Scenario: OrderBadge has dark variants

- **WHEN** `theme` is `'dark'`
- **THEN** `OrderBadge` variant colors have appropriate dark mode opacity adjustments

#### Scenario: ConfirmationModal has dark variants

- **WHEN** `theme` is `'dark'`
- **THEN** `ConfirmationModal` inherits `Modal` dark variants and buttons adjust correctly

---

### Requirement: Layout components MUST support dark mode

The system MUST apply `dark:` variants to Header, Footer, Sidebar, and Navigation.

#### Scenario: Header has dark variants

- **WHEN** `theme` is `'dark'`
- **THEN** `Header` renders with `dark:bg-gray-900 dark:border-gray-700` and text colors invert appropriately

#### Scenario: Footer has dark variants

- **WHEN** `theme` is `'dark'`
- **THEN** `Footer` renders with `dark:bg-gray-900 dark:border-gray-700`

#### Scenario: Sidebar has dark variants

- **WHEN** `theme` is `'dark'`
- **THEN** `Sidebar` renders with `dark:bg-gray-900 dark:border-gray-700` and link text uses `dark:text-gray-300 dark:hover:text-gray-100`

#### Scenario: Navigation has dark variants

- **WHEN** `theme` is `'dark'`
- **THEN** `Navigation` link hover states use `dark:hover:bg-gray-700`

---

### Requirement: All pages MUST render correctly in dark mode

The system MUST apply dark backgrounds to all admin pages, client pages, and feature components.

#### Scenario: Admin pages have dark backgrounds

- **WHEN** `theme` is `'dark'` and navigating to any admin page
- **THEN** the page container renders with `dark:bg-gray-950` and content cards with `dark:bg-gray-800`

#### Scenario: Client pages have dark backgrounds

- **WHEN** `theme` is `'dark'` and navigating to CatalogPage, ProfilePage, or any client page
- **THEN** the page renders with appropriate dark background and text colors

#### Scenario: Feature components adapt to dark mode

- **WHEN** `theme` is `'dark'`
- **THEN** `ProductGrid` cards, `CartDrawer` panel, and other feature components render with dark backgrounds

#### Scenario: Body element has dark background

- **WHEN** `theme` is `'dark'`
- **THEN** the `<body>` element or root layout has `dark:bg-gray-950 dark:text-gray-100`

---

### Requirement: Toaster MUST adapt to dark mode

The system MUST configure the `<Toaster>` to use dark-appropriate styles when the theme is dark.

#### Scenario: Toaster shows dark toast in dark mode

- **WHEN** `theme` is `'dark'` and a toast is triggered
- **THEN** the toast renders with dark background and light text

#### Scenario: Toaster shows light toast in light mode

- **WHEN** `theme` is `'light'` and a toast is triggered
- **THEN** the toast renders with the default light style

