# Tasks: implement-ui-responsiveness-and-ux

## 1. UI Store (state management)

- [ ] 1.1 Create `frontend/src/stores/uiStore.ts` with Zustand store: `theme` ('light' | 'dark'), `sidebarCollapsed` (boolean), `mobileMenuOpen` (boolean)
- [ ] 1.2 Add `persist` middleware for `theme` (localStorage key: `ui-storage`), omit `sidebarCollapsed` and `mobileMenuOpen` from persistence
- [ ] 1.3 Add `toggleTheme` action — flips between 'light' and 'dark'
- [ ] 1.4 Add `setSidebarCollapsed(collapsed: boolean)` action
- [ ] 1.5 Add `setMobileMenuOpen(open: boolean)` action

## 2. Dark Mode Infrastructure

- [ ] 2.1 Add `darkMode: 'class'` to `tailwind.config.ts`
- [ ] 2.2 Add `fontFamily: { sans: ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'sans-serif'] }` to `tailwind.config.ts`
- [ ] 2.3 Add `fadeIn` keyframe and `animate-fadeIn` animation to `tailwind.config.ts` extend
- [ ] 2.4 Create `frontend/src/shared/components/ThemeToggle.tsx` with sun SVG (dark mode) / moon SVG (light mode)
- [ ] 2.5 ThemeToggle: `min-h-[44px] min-w-[44px]`, dynamic `aria-label`, `transition-colors`
- [ ] 2.6 Add dark class management in `app/providers.tsx` — `useEffect` reads `uiStore.theme`, adds/removes `dark` class on `document.documentElement`
- [ ] 2.7 Place `ThemeToggle` in `Header` widget
- [ ] 2.8 Update `Toaster` config in `app/providers.tsx` for dark mode — dynamic `style` based on `theme` or `toastOptions` with appropriate dark backgrounds
- [ ] 2.9 Update `style.css` body for dark mode: `dark:bg-gray-950 dark:text-gray-100`

## 3. Dark Mode — Shared Components

- [ ] 3.1 Add `dark:` variants to `Badge`: background opacity adjustments (e.g., `dark:bg-green-900/30 dark:text-green-300`)
- [ ] 3.2 Add `dark:` variants to `Button`: `dark:ring-offset-gray-900`, dark variant colors for ghost/secondary
- [ ] 3.3 Add `dark:` variants to `Card`: `dark:bg-gray-800 dark:border-gray-700`
- [ ] 3.4 Add `dark:` variants to `Input`: `dark:bg-gray-800 dark:border-gray-600 dark:text-gray-100 dark:placeholder-gray-400`
- [ ] 3.5 Add `dark:` variants to `EmptyState`: `dark:bg-gray-800 dark:text-gray-300`
- [ ] 3.6 Add `dark:` variants to `ErrorDisplay`: `dark:bg-red-900/20 dark:text-red-300`
- [ ] 3.7 Add `dark:` variants to `Modal`: `dark:bg-gray-800` on panel, overlay unchanged (`bg-black/50`)
- [ ] 3.8 Add `dark:` variants to `Skeleton`: `dark:bg-gray-700` instead of `bg-gray-200`
- [ ] 3.9 Add `dark:` variants to `SkeletonTable`: inherit from `Skeleton` dark changes + `dark:border-gray-700`
- [ ] 3.10 Add `dark:` variants to `SkeletonCard`: inherit from `Skeleton` dark changes + `dark:border-gray-700`
- [ ] 3.11 Add `dark:` variant to `Spinner`: border color visible on dark backgrounds
- [ ] 3.12 Add `dark:` variants to `OrderBadge`: variant colors with dark mode opacity adjustments
- [ ] 3.13 Add `dark:` variants to `ConfirmationModal`: inherit from `Modal` dark changes

## 4. Dark Mode — Layout Components

- [ ] 4.1 Add `dark:` variants to `Header`: `dark:bg-gray-900 dark:border-gray-700`, invert text/search colors
- [ ] 4.2 Add `dark:` variants to `Footer`: `dark:bg-gray-900 dark:border-gray-700 dark:text-gray-400`
- [ ] 4.3 Add `dark:` variants to `Sidebar`: `dark:bg-gray-900 dark:border-gray-700`, link hover `dark:hover:bg-gray-700`, text `dark:text-gray-300`
- [ ] 4.4 Add `dark:` variants to `Navigation`: link hover `dark:hover:bg-gray-700`, active link `dark:bg-gray-700`

## 5. Dark Mode — Pages & Features

- [ ] 5.1 Add `dark:` variants to all admin pages containers (Users, Products, Orders, Ingredients, Categories, Dashboard)
- [ ] 5.2 Add `dark:` variants to all client pages (CatalogPage, ProductDetailPage, ProfilePage, CartPage, OrderHistoryPage, etc.)
- [ ] 5.3 Add `dark:` variants to feature components (ProductGrid, CartDrawer, etc.)
- [ ] 5.4 Add `dark:` variants to NotFoundPage

## 6. Responsive Layout Refactor

- [ ] 6.1 Add `className` prop support to `Sidebar` component (merged with existing classes, not overridden)
- [ ] 6.2 Refactor Layout in `app/router.tsx`: add Sidebar + MobileDrawer + skip-to-content structure
- [ ] 6.3 Add hamburger button to `Header` — visible `lg:hidden`, with `aria-label` dynamic ("Abrir menú" / "Cerrar menú")
- [ ] 6.4 Hamburger button calls `uiStore.setMobileMenuOpen(!mobileMenuOpen)` on click
- [ ] 6.5 Create `frontend/src/shared/components/MobileDrawer.tsx` with props: `isOpen`, `onClose`, `children`
- [ ] 6.6 MobileDrawer: `createPortal` to `document.body`
- [ ] 6.7 MobileDrawer: overlay with `bg-black/50`, `transition-opacity duration-300`, click-to-close
- [ ] 6.8 MobileDrawer: panel slides from left with `transition-transform duration-300` (`-translate-x-full` ↔ `translate-x-0`)
- [ ] 6.9 MobileDrawer: Escape key closes drawer
- [ ] 6.10 MobileDrawer: body scroll lock on open (`document.body.style.overflow = 'hidden'`), restore on close/unmount
- [ ] 6.11 MobileDrawer: `role="dialog"`, `aria-modal="true"` on panel, `aria-hidden` on overlay when closed
- [ ] 6.12 MobileDrawer: render `Sidebar` with `collapsed={false}` inside the drawer panel
- [ ] 6.13 Update desktop `Sidebar` usage in Layout to `className="hidden lg:block"`
- [ ] 6.14 Wire `mobileMenuOpen` close on navigation link click inside MobileDrawer (optional but ideal UX)

## 7. Accessibility — General

- [ ] 7.1 Add skip-to-content link in Layout: `<a href="#main-content" className="sr-only focus:not-sr-only ...">Saltar al contenido</a>`
- [ ] 7.2 Add `id="main-content"` to the `<main>` element in Layout (for skip link target), with `tabIndex={-1}` for programmatic focus
- [ ] 7.3 Replace all `focus:ring-*` with `focus-visible:ring-*` in `Button.tsx`
- [ ] 7.4 Replace all `focus:ring-*` with `focus-visible:ring-*` in `Input.tsx`
- [ ] 7.5 Replace all `focus:ring-*` with `focus-visible:ring-*` in `Modal.tsx` (close button)
- [ ] 7.6 Replace all `focus:ring-*` with `focus-visible:ring-*` in `Badge.tsx` (if applicable)
- [ ] 7.7 Replace all `focus:ring-*` with `focus-visible:ring-*` in all admin pages (buttons, inputs, selects, search fields)
- [ ] 7.8 Add `aria-label` to Header cart button: `"Carrito de compras"` or `"Carrito de compras, {N} items"`
- [ ] 7.9 Add `aria-label` to Modal close button: `"Cerrar"` (if not already present)
- [ ] 7.10 Add `aria-label` to all icon buttons in table rows (edit: `"Editar"`, delete: `"Eliminar"`)
- [ ] 7.11 Add `aria-label` to pagination buttons: previous `"Página anterior"`, next `"Página siguiente"`, page N `"Ir a página {N}"`
- [ ] 7.12 Add `aria-label` to Sidebar toggle button: `"Colapsar menú"` / `"Expandir menú"`
- [ ] 7.13 Add screen reader text (`sr-only`) to charts on DashboardPage and admin pages
- [ ] 7.14 Add `sr-only` headings to sections that use visual-only indicators (icons without text labels)
- [ ] 7.15 Add `aria-label` or `<caption>` to data tables

## 8. Accessibility — Semantic HTML

- [ ] 8.1 Fix `LoginPage`: wrap content in `<main>`, form in `<section>` with heading
- [ ] 8.2 Fix `RegisterPage`: wrap content in `<main>`, form in `<section>` with heading
- [ ] 8.3 Fix `DashboardPage`: wrap content in `<main>`, stat cards in `<section>`, charts in `<section>` with headings
- [ ] 8.4 Fix `NotFoundPage`: wrap content in `<main>`

## 9. Accessibility — Modal Focus Trap

- [ ] 9.1 Save `document.activeElement` as `triggerRef` when Modal opens
- [ ] 9.2 Implement focus trap in `Modal.tsx`: query all focusable elements within modal, cycle Tab/Shift+Tab between first and last
- [ ] 9.3 Ensure Escape key still closes modal (existing behavior + focus trap coexistence)
- [ ] 9.4 Restore focus to `triggerRef.current` when Modal closes (on Escape, close button, or overlay click)
- [ ] 9.5 Verify `ConfirmationModal` inherits focus trap from `Modal`

## 10. Touch Target Fixes

- [ ] 10.1 Adjust `Button sm` padding to `px-4 py-3` (achieves `min-h-[44px]`)
- [ ] 10.2 Adjust `Button md` padding to `px-5 py-3` (achieves `min-h-[44px]`)
- [ ] 10.3 Adjust `Button lg` padding to `px-6 py-4` (achieves `min-h-[52px]`)
- [ ] 10.4 Apply `min-h-[44px] min-w-[44px] inline-flex items-center justify-center` to Header cart button
- [ ] 10.5 Apply `min-h-[44px] min-w-[44px] inline-flex items-center justify-center` to Sidebar toggle button
- [ ] 10.6 Apply `min-h-[44px] min-w-[44px] inline-flex items-center justify-center` to Modal close button
- [ ] 10.7 Apply `min-h-[44px] min-w-[44px]` to CartDrawer quantity increase/decrease buttons
- [ ] 10.8 Apply `min-h-[44px] min-w-[44px]` to table action buttons (edit, delete in rows)
- [ ] 10.9 Apply `min-h-[44px] min-w-[44px]` to pagination buttons

## 11. Contrast Fixes

- [ ] 11.1 Replace `text-gray-400` with `text-gray-500` for body/description/secondary text throughout the app
- [ ] 11.2 Replace `text-primary` (green) with `text-primary-700` for green text on light backgrounds (prices, CTAs, success indicators)
- [ ] 11.3 Replace `text-gray-300` disabled text with `text-gray-400` for better readability in disabled states
- [ ] 11.4 Ensure minimum font size `text-sm` (14px) for body text across all pages
- [ ] 11.5 Verify dark mode text contrast: `dark:text-gray-300` on `dark:bg-gray-900` and `dark:text-gray-400` on `dark:bg-gray-800`

## 12. Animations & Typography

- [ ] 12.1 Create `frontend/src/shared/components/PageTransition.tsx` — wraps children in `<div className="animate-fadeIn">`
- [ ] 12.2 Apply `PageTransition` to `<Outlet />` in Layout main content area
- [ ] 12.3 Configure toast enter/exit animation in `Toaster` component (react-hot-toast defaults or custom)
- [ ] 12.4 Add `transition-colors duration-150` to table row hover (if not already present)
- [ ] 12.5 Ensure Sidebar collapse uses `transition-all duration-300` (may already exist, verify and fix if missing)
- [ ] 12.6 Apply responsive heading sizes: `text-2xl lg:text-3xl` for page h1, `text-xl lg:text-2xl` for h2 across all pages

## 13. Verification

- [ ] 13.1 Run `npx tsc --noEmit` in `frontend/` — zero TypeScript errors
- [ ] 13.2 Verify dark mode toggle works: theme switches, all components adapt colors correctly on all pages (admin + client)
- [ ] 13.3 Verify dark mode persists after page reload (localStorage)
- [ ] 13.4 Verify responsive layout on mobile viewport (375px width): hamburger visible, sidebar hidden, drawer works
- [ ] 13.5 Verify responsive layout on tablet viewport (768px width): hamburger visible, sidebar hidden, drawer works
- [ ] 13.6 Verify desktop layout (1280px+): sidebar visible, hamburger hidden, no drawer
- [ ] 13.7 Verify keyboard navigation: Tab through all interactive elements on every page, focus rings visible only with keyboard
- [ ] 13.8 Verify skip-to-content link works: first Tab shows it, Enter navigates to main content
- [ ] 13.9 Verify Modal focus trap: Tab/Shift+Tab cycles within modal, does not escape to background
- [ ] 13.10 Verify focus returns to trigger element after Modal close (Escape, button, overlay)
- [ ] 13.11 Verify `ConfirmationModal` focus trap works (inherited from Modal)
- [ ] 13.12 Verify MobileDrawer focus trap: first focusable element in drawer receives focus on open
- [ ] 13.13 Verify all `aria-label` attributes present on icon buttons (cart, close, theme, menu, edit, delete, pagination, sidebar toggle)
- [ ] 13.14 Verify touch targets ≥44px on all interactive elements (use DevTools element inspector)
- [ ] 13.15 Verify color contrast passes WCAG AA (use axe DevTools or Chrome DevTools contrast checker)
- [ ] 13.16 Verify dark mode text contrast passes on dark backgrounds
- [ ] 13.17 Verify animations do not cause layout shift (CLS)
- [ ] 13.18 Verify semantic HTML: `LoginPage`, `RegisterPage`, `DashboardPage`, `NotFoundPage` use `<main>` and `<section>`
- [ ] 13.19 Verify FSD: no file in `shared/` imports from `pages/`, `features/`, or `entities/`
- [ ] 13.20 Verify `focus-visible` is used everywhere instead of `focus` (grep for `focus:ring` that should be `focus-visible:ring`)
