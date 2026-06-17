## Why

La UX de Food Store no está preparada para dispositivos móviles ni cumple con estándares de accesibilidad. El dark mode no existe — `darkMode` no está configurado en Tailwind, no hay `dark:` prefixes, ni store de tema. La navegación mobile está rota: el Header no tiene hamburger, el componente `Navigation` no se usa en el layout, el Sidebar es siempre visible (no responsive). Solo hay 6 `aria-label` en todo el frontend, cero uso de `focus-visible`, cero skip links, y solo 1 `sr-only`. Todos los elementos interactivos fallan el mínimo de 44×44px para touch targets — el más pequeño mide 24px (botones de tabla), y 32px (botones qty +/-). Hay ~5 fallas de contraste: `text-gray-400` sobre blanco (3.6:1), `text-primary` verde sobre blanco (2.4:1), `text-gray-300` en estados disabled. No existe `uiStore` — el estado de sidebar/nav es `useState` local, sin estado de tema compartido. La tipografía usa todos los defaults de Tailwind sin configuración.

## What Changes

- **Nuevo `uiStore`** en `src/stores/uiStore.ts` — Zustand + persist middleware con estado de `theme`, `sidebarCollapsed`, `mobileMenuOpen`, y acciones `toggleTheme`, `setSidebarCollapsed`, `setMobileMenuOpen`
- **Dark Mode con Tailwind** — `darkMode: 'class'` en `tailwind.config.ts`, migración de todos los colores hardcodeados a variantes `dark:`, nuevo `ThemeToggle` en `shared/components/ThemeToggle.tsx`, sincronización de clase `dark` en `<html>` vía `useEffect`
- **Layout responsive mobile-first** — Refactor de `router.tsx` Layout: Header con hamburger (`lg:hidden`), Sidebar `hidden lg:block`, nuevo `MobileDrawer` (portal, overlay, slide-from-left, Escape close, body scroll lock)
- **Accesibilidad** — Skip-to-content link, reemplazo global de `focus:ring-*` → `focus-visible:ring-*`, `aria-label` en todos los icon buttons (cart, close, theme, menu, edit, delete, pagination), semantic HTML en LoginPage/RegisterPage/DashboardPage/NotFoundPage, screen reader text en charts y secciones visuales, focus trap en Modal (Tab/Shift+Tab cicla dentro, focus retorna al trigger al cerrar)
- **Touch targets ≥44px** — Ajuste de padding en Button (sm/md/lg), icon buttons 44×44px, CartDrawer qty buttons 44×44px, table actions 44×44px, pagination 44×44px
- **Corrección de contraste** — `text-gray-400` → `text-gray-500` (3.6:1 → 5.3:1), `text-primary` → `text-primary-700` (#15803d, 5.5:1), ajuste de disabled states, mínimo `text-sm` para metadata
- **Animaciones** — PageTransition wrapper con `animate-fadeIn` (opacity 0→1 + translateY), keyframe custom en tailwind.config, configuración de animación en Toaster (react-hot-toast), transiciones hover en table rows
- **Tipografía** — `fontFamily: { sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'] }` en tailwind.config, responsive headings (`text-2xl lg:text-3xl`), body text mínimo `text-sm` (14px), preferencia `text-base` (16px)

## Capabilities

### New Capabilities

- `ui-darkmode`: Dark mode con estrategia `class` de Tailwind, ThemeToggle, uiStore con persistencia en localStorage, y migración completa de colores a variantes `dark:` en todos los componentes compartidos, layout, páginas admin y cliente.
- `ui-responsive-layout`: Layout responsive mobile-first con Header hamburger, Sidebar oculto en mobile, MobileDrawer con portal/overlay/slide/Escape/scroll-lock, y Navigation integrada.
- `ui-accessibility`: Accesibilidad WCAG AA: skip-to-content, focus-visible global, ARIA labels en icon buttons, focus trap en Modal, semantic HTML, screen reader text, touch targets ≥44px, y contraste corregido (mínimo 4.5:1 para texto normal, 3:1 para texto grande).
- `ui-animations`: PageTransition con fadeIn, keyframes custom en Tailwind, toast animations configuradas, hover transitions en tablas, y sidebar drawer transitions.

### Modified Capabilities

- `ui-feedback` (Change 45): Los componentes compartidos (Button, Modal, Badge, Card, etc.) reciben variantes `dark:` de color pero mantienen compatibilidad hacia atrás.

## Impact

- **Frontend**: `src/stores/uiStore.ts` (nuevo), `shared/components/ThemeToggle.tsx` (nuevo), `shared/components/MobileDrawer.tsx` (nuevo), `shared/components/PageTransition.tsx` (nuevo), `app/router.tsx` (modificado — Layout refactor), `app/providers.tsx` (modificado — dark class sync), `tailwind.config.ts` (modificado — darkMode, fontFamily, keyframes), `style.css` (modificado — dark body styles), `shared/components/Button.tsx` (modificado — dark variants + touch targets), `shared/components/Modal.tsx` (modificado — dark variants + focus trap), `shared/components/Card.tsx` (modificado — dark variants), `shared/components/Badge.tsx` (modificado — dark variants), `shared/components/Input.tsx` (modificado — dark variants), `shared/components/EmptyState.tsx` (modificado — dark variants), `shared/components/ErrorDisplay.tsx` (modificado — dark variants), `shared/components/Skeleton.tsx` + `SkeletonTable.tsx` + `SkeletonCard.tsx` (modificado — dark variants), `shared/components/Spinner.tsx` (modificado — dark variants), `shared/components/OrderBadge.tsx` (modificado — dark variants), `shared/components/ConfirmationModal.tsx` (modificado — dark variants + focus trap heredado), `shared/components/Header.tsx` (modificado — hamburger + ThemeToggle + dark), `shared/components/Footer.tsx` (modificado — dark), `shared/components/Sidebar.tsx` (modificado — responsive + dark), `shared/components/Navigation.tsx` (modificado — dark), `pages/client/LoginPage.tsx` (modificado — semantic HTML), `pages/client/RegisterPage.tsx` (modificado — semantic HTML), `pages/admin/DashboardPage.tsx` (modificado — semantic HTML), `pages/NotFoundPage.tsx` (modificado — semantic HTML), todas las páginas admin y cliente (modificado — dark backgrounds), feature components: `ProductGrid`, `CartDrawer`, etc. (modificado — dark variants + touch targets)
- **Backend**: Sin cambios
- **Base de datos**: Sin cambios
- **Dependencias**: `zustand` v4 ya instalado. Ninguna dependencia nueva.
- **Seguridad**: Sin impacto. La accesibilidad y el dark mode son puramente frontend.
