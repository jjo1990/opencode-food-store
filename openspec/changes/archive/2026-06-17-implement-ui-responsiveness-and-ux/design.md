## Context

Food Store usa Tailwind CSS v3 con configuración en `frontend/tailwind.config.ts`. Los componentes compartidos viven en `frontend/src/shared/components/` (`Button`, `Modal`, `Card`, `Badge`, `Input`, `EmptyState`, `ErrorDisplay`, `Skeleton`, `SkeletonTable`, `SkeletonCard`, `Spinner`, `OrderBadge`, `ConfirmationModal`, `Header`, `Footer`, `Sidebar`, `Navigation`). El layout actual es un stacked column simple en `app/router.tsx` sin sidebar ni mobile nav. `react-hot-toast` v2.6.0 está configurado con `<Toaster>` en `app/providers.tsx`. Zustand v4 está instalado para stores existentes (`authStore`, `cartStore`). Change 45 (`implement-notifications-and-feedback`) ya completó Badge, ConfirmationModal, SkeletonTable/SkeletonCard, useToastAsync, y mejoras de extensibilidad — estos componentes existen y deben recibir dark variants.

**Restricciones existentes:**

- FSD estricto: `pages → features → entities → shared` (nunca al revés)
- TypeScript `strict: true`, no se permite `any`
- Solo Tailwind CSS, sin CSS modules
- Componentes compartidos exportan con named + default export
- `Modal` actual usa `createPortal` con escape key y click-outside
- `Header` actual tiene logo, search bar (opcional), cart button con badge, user dropdown (si autenticado), y role-based nav links
- `Sidebar` renderiza `Navigation` internamente con links colapsables por sección
- `Navigation` es un componente separado con links de admin/cliente según rol
- Zustand stores usan `persist` middleware para auth y cart
- `style.css` tiene estilos base de Tailwind (`@tailwind base/components/utilities`)
- Breakpoints Tailwind: sm=640px, md=768px, lg=1024px, xl=1280px, 2xl=1536px

**Lo que NO existe:**

- `darkMode` en tailwind.config
- Store `uiStore` — el estado de sidebar/nav es `useState` local en router.tsx
- `ThemeToggle` component
- `MobileDrawer` component
- `PageTransition` component
- Hamburger button en Header
- Responsive visibility en Sidebar
- Skip-to-content link
- `focus-visible` en ningún componente
- `aria-label` en icon buttons (solo 6 en total)
- Focus trap en Modal
- Semantic HTML en páginas de auth y dashboard
- Screen reader text para charts y secciones visuales
- Touch targets de 44×44px
- Contraste WCAG AA corregido
- `fontFamily` config en Tailwind
- Keyframes custom en Tailwind

## Goals / Non-Goals

**Goals:**

- Crear `uiStore` con Zustand + persist para theme, sidebarCollapsed, mobileMenuOpen
- Implementar dark mode con estrategia `class` de Tailwind y migrar todos los componentes
- Refactorizar Layout para responsive mobile-first con MobileDrawer
- Garantizar accesibilidad WCAG AA: skip-to-content, focus-visible, ARIA labels, focus trap, semantic HTML, screen reader text
- Asegurar touch targets ≥44×44px en todos los elementos interactivos
- Corregir todas las fallas de contraste (mínimo 4.5:1 para texto normal)
- Agregar animaciones de transición de página y configurar toast animations
- Configurar tipografía responsive con Inter font family

**Non-Goals:**

- No implementar `prefers-color-scheme` media query (el usuario elige explícitamente)
- No crear múltiples temas de color (solo light/dark)
- No migrar a Tailwind v4 en este change
- No tests automatizados (e2e, unit) en este change
- No cambios en backend
- No sistema de i18n para textos de UI
- No animaciones complejas con Framer Motion — solo CSS transitions + Tailwind
- No rediseñar páginas individuales — solo adaptar colores y estructura a dark mode y responsive
- No modificar `OrderBadge` variants (ya cubre 6 estados FSM de pedido)

## Decisions

### 1. UI Store — Zustand + Persist

**Decision:**

```ts
interface UIState {
  theme: 'light' | 'dark';
  sidebarCollapsed: boolean;
  mobileMenuOpen: boolean;
  toggleTheme: () => void;
  setSidebarCollapsed: (collapsed: boolean) => void;
  setMobileMenuOpen: (open: boolean) => void;
}
```

Store en `frontend/src/stores/uiStore.ts` usando Zustand con `persist` middleware. `theme` se persiste en localStorage bajo key `ui-storage`. `sidebarCollapsed` y `mobileMenuOpen` son efímeros (no persisten).

**Rationale**: Zustand ya está instalado y en uso para `authStore` y `cartStore`. El `persist` middleware es el mismo que usa `authStore`. Separar estado de UI de stores de dominio sigue el principio de separación de concerns. `theme` en localStorage permite recordar la preferencia entre sesiones. `sidebarCollapsed` y `mobileMenuOpen` son estado de sesión que no necesita persistir — reinician al recargar.

**Alternativa considerada**: Usar React Context para theme y useState para sidebar. Rechazada — Zustand evita prop drilling y re-renders innecesarios. Context causaría re-render de todo el árbol en cada cambio de theme.

### 2. Dark Mode — `class` Strategy

**Decision**: Usar `darkMode: 'class'` en `tailwind.config.ts`.

```ts
// tailwind.config.ts
export default {
  darkMode: 'class',
  // ...
}
```

El `<html>` recibe la clase `dark` dinámicamente vía `useEffect` en `app/providers.tsx`:

```tsx
useEffect(() => {
  const root = document.documentElement;
  if (theme === 'dark') {
    root.classList.add('dark');
  } else {
    root.classList.remove('dark');
  }
}, [theme]);
```

Todos los colores hardcodeados migran a usar `dark:` variants:

| Light | Dark |
|-------|------|
| `bg-white` | `dark:bg-gray-900` |
| `bg-gray-50` | `dark:bg-gray-800` |
| `bg-gray-100` | `dark:bg-gray-700` |
| `text-gray-900` | `dark:text-gray-100` |
| `text-gray-700` | `dark:text-gray-300` |
| `text-gray-500` | `dark:text-gray-400` |
| `text-gray-400` | `dark:text-gray-500` |
| `border-gray-200` | `dark:border-gray-700` |
| `border-gray-100` | `dark:border-gray-800` |

**Rationale**: La estrategia `class` da control explícito desde JS (uiStore) y no depende de la preferencia del SO. `media` strategy (`prefers-color-scheme`) sería automática pero no permitiría override manual. La sintaxis `dark:` de Tailwind es la forma idiomática y el compilador purga las clases no usadas en producción.

**Alternativa considerada**: CSS custom properties (`--color-bg`, etc.) toggled via class. Rechazada — Tailwind `dark:` prefixes ya son el mecanismo nativo y evitan mantener un sistema paralelo de variables.

### 3. ThemeToggle Component

**Decision**: Componente en `shared/components/ThemeToggle.tsx`:

```tsx
function ThemeToggle() {
  const { theme, toggleTheme } = useUIStore();
  return (
    <button
      onClick={toggleTheme}
      aria-label={theme === 'dark' ? 'Cambiar a modo claro' : 'Cambiar a modo oscuro'}
      className="min-h-[44px] min-w-[44px] inline-flex items-center justify-center rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
    >
      {theme === 'dark' ? <SunIcon /> : <MoonIcon />}
    </button>
  );
}
```

SVG inline para moon (path con círculo y crescent) y sun (círculo con rays). Sin dependencias de librerías de íconos.

**Rationale**: SVGs inline evitan dependencias externas (lucide-react, heroicons). Moon en light mode (indica "cambiar a dark"), Sun en dark mode (indica "cambiar a light") — patrón estándar. Touch target 44×44px desde el inicio.

### 4. Responsive Layout — MobileDrawer

**Decision**: Refactorizar `app/router.tsx` Layout para estructura responsive:

```tsx
function Layout() {
  const { sidebarCollapsed, mobileMenuOpen, setMobileMenuOpen } = useUIStore();
  
  return (
    <div className="flex min-h-screen flex-col bg-white dark:bg-gray-950">
      <SkipToContent />
      <Header onMenuToggle={() => setMobileMenuOpen(!mobileMenuOpen)} />
      <div className="flex flex-1">
        <Sidebar collapsed={sidebarCollapsed} className="hidden lg:block" />
        <MobileDrawer isOpen={mobileMenuOpen} onClose={() => setMobileMenuOpen(false)}>
          <Sidebar collapsed={false} />
        </MobileDrawer>
        <main id="main-content" className="flex-1">
          <PageTransition>
            <Outlet />
          </PageTransition>
        </main>
      </div>
      <Footer />
    </div>
  );
}
```

**Key changes:**
- `Sidebar` agrega `className` prop para `hidden lg:block` (visible solo en desktop)
- `Header` agrega hamburger button con `lg:hidden`
- `Navigation` se renderiza dentro de `Sidebar` (ya lo hace actualmente)
- `MobileDrawer` nuevo componente que envuelve el mismo `Sidebar`

**Rationale**: El Sidebar se reusa tanto en desktop como en mobile drawer — mismo componente, mismo contenido, solo cambia el wrapper. Esto evita duplicar la lógica de navegación. La prop `className` en Sidebar permite control externo de visibilidad sin acoplar el componente a breakpoints.

### 5. MobileDrawer Component

**Decision**: `shared/components/MobileDrawer.tsx`:

```tsx
interface MobileDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  children: ReactNode;
}
```

- `createPortal` a `document.body`
- Overlay: `fixed inset-0 bg-black/50 z-40 transition-opacity` + `opacity-0`/`opacity-100`
- Panel: `fixed inset-y-0 left-0 w-64 bg-white dark:bg-gray-900 z-50 transform transition-transform duration-300` + `-translate-x-full`/`translate-x-0`
- Escape key → `onClose()`
- Click overlay → `onClose()`
- Body scroll lock: `document.body.style.overflow = 'hidden'` al abrir, restaurar al cerrar/desmontar
- `aria-hidden` en overlay cuando cerrado
- `aria-modal` y `role="dialog"` en panel

**Rationale**: Portal-based para evitar problemas de z-index con otros elementos posicionados. Slide desde la izquierda es el patrón estándar de mobile nav. Body scroll lock evita scroll del fondo mientras el drawer está abierto. Las transiciones usan `transition-transform duration-300` para suavidad. ARIA attributes para accesibilidad del drawer.

### 6. Accessibility — Focus-Visible

**Decision**: Reemplazar todas las ocurrencias de `focus:ring-*` con `focus-visible:ring-*` en:
- `Button.tsx` — `focus-visible:ring-2 focus-visible:ring-offset-2`
- `Input.tsx` — `focus-visible:ring-2 focus-visible:border-primary-500`
- `Modal.tsx` — close button `focus-visible:ring-2`
- `Badge.tsx` — si aplica
- Todas las páginas admin — botones de acción, inputs de búsqueda, selects

**Rationale**: `focus:ring` muestra el anillo también en clicks de mouse, lo cual es visualmente molesto e innecesario. `focus-visible` solo muestra el anillo cuando el navegador detecta navegación por teclado (Tab). Esto es el comportamiento recomendado por WCAG 2.4.7 Focus Visible. Tailwind v3 soporta `focus-visible:` nativamente.

### 7. Accessibility — Focus Trap in Modal

**Decision**: Implementar focus trap en `Modal.tsx`:

```tsx
// Al abrir el modal
const triggerRef = useRef(document.activeElement);
// Focus trap: Tab/Shift+Tab cicla dentro del modal
const handleKeyDown = (e: KeyboardEvent) => {
  if (e.key === 'Escape') { onClose(); return; }
  if (e.key !== 'Tab') return;
  
  const focusable = modalRef.current.querySelectorAll(
    'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
  );
  const first = focusable[0] as HTMLElement;
  const last = focusable[focusable.length - 1] as HTMLElement;
  
  if (e.shiftKey && document.activeElement === first) {
    e.preventDefault();
    last.focus();
  } else if (!e.shiftKey && document.activeElement === last) {
    e.preventDefault();
    first.focus();
  }
};
// Al cerrar: triggerRef.current?.focus()
```

**Rationale**: Sin focus trap, el Tab puede escapar del modal hacia elementos del fondo, rompiendo la experiencia de teclado y violando WCAG 2.4.3 Focus Order. Guardar `triggerRef` permite retornar el foco al elemento que abrió el modal, cumpliendo WCAG 2.4.3.

`ConfirmationModal` hereda el focus trap automáticamente porque usa `Modal` internamente.

### 8. Touch Targets — 44×44px Minimum

**Decision**: Ajustar todos los elementos interactivos al mínimo WCAG de 44×44px (AA):

**Button sizes ajustados:**
- `sm`: `px-4 py-3` → altura total ≥44px (antes `px-3 py-1.5` = ~30px)
- `md`: `px-5 py-3` → altura total ≥44px (antes `px-4 py-2` = ~36px)
- `lg`: `px-6 py-4` → altura total ≥52px (ya era aceptable)

**Icon buttons (cart, close, theme, menu, edit, delete):**
- Clase base: `min-h-[44px] min-w-[44px] inline-flex items-center justify-center`
- Cart button, Sidebar toggle, Modal close, ThemeToggle, edit/delete icon buttons en tablas

**CartDrawer qty buttons:**
- `min-h-[44px] min-w-[44px]` con flex centrado

**Table action buttons:**
- `min-h-[44px] min-w-[44px]` para botones de editar/eliminar en filas

**Pagination buttons:**
- `min-h-[44px] min-w-[44px]` para cada número de página

**Rationale**: WCAG 2.5.5 Target Size (AAA) pide 44×44px. Aunque AA no lo requiere explícitamente, es una best practice para usabilidad en dispositivos táctiles. El ajuste de padding preserva la apariencia visual similar pero garantiza el área táctil mínima.

### 9. Contrast Fixes

**Decision**: Correcciones puntuales de combinaciones de color:

| Combinación | Antes | Ratio | Después | Ratio |
|-------------|-------|-------|---------|-------|
| Texto descriptivo sobre blanco | `text-gray-400` (#9ca3af) | 3.6:1 | `text-gray-500` (#6b7280) | 5.3:1 |
| Texto verde primario sobre blanco | `text-primary` (#22c55e) | 2.4:1 | `text-primary-700` (#15803d) | 5.5:1 |
| Texto disabled sobre blanco | `text-gray-300` (#d1d5db) | 1.9:1 | `text-gray-400` (#9ca3af) | 3.6:1 |

Para dark mode, verificar que `dark:text-gray-300` (#d1d5db) sobre `dark:bg-gray-900` (#111827) tiene contraste ≥4.5:1 (pasa: ~11.5:1). `dark:text-gray-400` (#9ca3af) sobre `dark:bg-gray-800` (#1f2937) también pasa (~5.1:1).

**Rationale**: WCAG AA requiere 4.5:1 para texto normal y 3:1 para texto grande (≥18px bold o ≥24px). `text-gray-400` falla para texto normal. `text-primary` verde claro falla catastróficamente. Las correcciones usan tokens existentes de la paleta Tailwind. `text-primary-700` mantiene la identidad verde pero con suficiente contraste.

Disabled text (`text-gray-300` → `text-gray-400`) está en una zona gris — WCAG exime elementos inactivos, pero `text-gray-400` (3.6:1) es más legible que `text-gray-300` (1.9:1).

### 10. Animations — PageTransition

**Decision**: Componente `PageTransition` en `shared/components/PageTransition.tsx`:

```tsx
function PageTransition({ children }: { children: ReactNode }) {
  return (
    <div className="animate-fadeIn">
      {children}
    </div>
  );
}
```

Keyframe en `tailwind.config.ts`:
```ts
extend: {
  keyframes: {
    fadeIn: {
      '0%': { opacity: '0', transform: 'translateY(4px)' },
      '100%': { opacity: '1', transform: 'translateY(0)' },
    },
  },
  animation: {
    fadeIn: 'fadeIn 0.3s ease-out',
  },
}
```

**Toast animations**: `react-hot-toast` ya tiene animaciones built-in. Se configura `toastOptions` con `style: { animation: '...' }` si es necesario, pero los defaults (slide from top) son suficientes.

**Table row hover**: `transition-colors duration-150` en `<tr>` (ya está en muchas tablas, verificar).

**Rationale**: Animaciones sutiles mejoran la percepción de rendimiento sin distraer. `fadeIn` con translateY da sensación de continuidad entre páginas. `0.3s` es rápido (no bloquea la interacción) pero visible. Keyframes en `tailwind.config` evitan CSS custom y mantienen todo en el sistema de diseño.

### 11. Typography

**Decision**: Configurar `fontFamily` en `tailwind.config.ts`:

```ts
fontFamily: {
  sans: ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'sans-serif'],
}
```

- Body text base: `text-base` (16px) heredado vía Tailwind default en `<body>`
- Dense data (tablas): `text-sm` (14px)
- Page headings: responsive — `text-2xl lg:text-3xl` para h1, `text-xl lg:text-2xl` para h2
- Metadata/secondary: `text-sm` como mínimo (nunca `text-xs` para cuerpo de texto)

**Rationale**: Inter es la tipografía recomendada por Tailwind y tiene excelente legibilidad en pantalla. La stack de fallback (`system-ui`, `-apple-system`) garantiza rendering nativo sin descargar fuentes. Los tamaños responsive aseguran headings proporcionales en mobile sin ser excesivamente grandes.

## Architecture

```
stores/
└── uiStore.ts              (NEW — Zustand + persist, theme/sidebar/mobileMenu)

shared/components/
├── ThemeToggle.tsx          (NEW — sun/moon SVG, toggles uiStore.theme)
├── MobileDrawer.tsx         (NEW — portal, overlay, slide, Escape, scroll lock)
├── PageTransition.tsx       (NEW — fadeIn wrapper)
├── Button.tsx               (MOD — dark variants + touch targets)
├── Modal.tsx                (MOD — dark variants + focus trap)
├── Card.tsx                 (MOD — dark variants)
├── Badge.tsx                (MOD — dark variants)
├── Input.tsx                (MOD — dark variants + focus-visible)
├── EmptyState.tsx           (MOD — dark variants)
├── ErrorDisplay.tsx         (MOD — dark variants)
├── Skeleton.tsx             (MOD — dark variants)
├── SkeletonTable.tsx        (MOD — dark variants)
├── SkeletonCard.tsx         (MOD — dark variants)
├── Spinner.tsx              (MOD — dark variants)
├── OrderBadge.tsx           (MOD — dark variants)
├── ConfirmationModal.tsx    (MOD — dark variants + focus trap inherited)
├── Header.tsx               (MOD — hamburger + ThemeToggle + dark + aria-labels)
├── Footer.tsx               (MOD — dark)
├── Sidebar.tsx              (MOD — hidden lg:block + dark)
└── Navigation.tsx           (MOD — dark)

app/
├── router.tsx               (MOD — Layout: Sidebar + MobileDrawer + SkipToContent)
├── providers.tsx            (MOD — dark class sync + Toaster dark config)
└── style.css                (MOD — dark body styles)

tailwind.config.ts           (MOD — darkMode, fontFamily, keyframes)

pages/
├── admin/*                  (MOD — dark backgrounds + semantic HTML)
├── client/*                 (MOD — dark backgrounds + semantic HTML)
└── NotFoundPage.tsx         (MOD — semantic HTML)

features/
└── **/*                     (MOD — dark variants + touch targets)
    ├── ProductGrid
    ├── CartDrawer (qty buttons)
    └── ...
```

## Risks / Trade-offs

| Risk | Mitigation |
| ---- | ---------- |
| `dark:` migration masiva puede omitir algún componente | Revisión sistemática por grupo (shared → layout → pages → features). Verificación visual con dark mode toggle en todas las páginas. |
| Touch target 44px en botones sm puede verse desproporcionado en escritorio | Es aceptable — 44px es estándar y los botones sm son para acciones secundarias. En escritorio el padding extra no perjudica. |
| Focus trap en Modal puede interferir con otros portales (ej: select dropdown, datepicker) | El querySelector solo captura elementos dentro del modal (`modalRef.current`). Si un dropdown renderiza en portal (fuera del modal), no será atrapado — eso es correcto porque el dropdown está en otra capa. |
| `window.matchMedia` no usado significa que el theme no sigue la preferencia del SO | Es intencional. El usuario elige explícitamente. Si en el futuro se quiere `prefers-color-scheme`, se puede agregar como fallback cuando no hay valor en localStorage. |
| MobileDrawer duplica el DOM del Sidebar (desktop + mobile) | Es aceptable — solo uno es visible a la vez. El costo de renderizar un Sidebar extra (lista de links) es insignificante. Alternativa con `useMediaQuery` y render condicional agregaría complejidad de hidratación. |
| `focus-visible` puede no funcionar en navegadores viejos (Safari < 15.4) | Safari 15.4+ lo soporta. Para navegadores sin soporte, `focus-visible` hace fallback a `focus` — no se pierde accesibilidad, solo se muestra el anillo también en clicks. |

## Open Questions

1. ¿Debería el Sidebar en mobile drawer tener `collapsed={false}` siempre, o también permitir colapsar secciones? (Siempre expandido en mobile — el drawer ya es compacto, colapsar secciones dentro sería confuso.)
2. ¿Debería `PageTransition` usar `AnimatePresence` de Framer Motion para animaciones de salida? (No en este change — solo fadeIn en mount. Exit animations requieren Framer Motion o state management complejo.)
3. ¿Debería persistir también `sidebarCollapsed` en localStorage? (No por ahora — es preferencia de sesión. Se puede agregar después si hay demanda.)
4. ¿Debería `ThemeToggle` tener animación de rotación al cambiar? (Nice to have. Agregar `transition-transform duration-300` con `rotate-180` en dark mode.)
