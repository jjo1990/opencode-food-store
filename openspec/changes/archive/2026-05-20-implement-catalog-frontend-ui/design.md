## Context

El frontend actual está prácticamente en blanco: solo existe un esqueleto de auth (LoginForm, RegisterForm, authStore, ProtectedRoute, Navigation/Sidebar) pero sin router configurado, sin Tailwind, sin TanStack Query, sin componentes compartidos. El `App.tsx` es un placeholder.

El backend del catálogo está completo y archivado (Changes 17-20): categorías jerárquicas, ingredientes, productos CRUD, y la API pública con role-aware filtering (`GET /api/v1/catalog/productos` con filtros, `GET /api/v1/categorias` con árbol).

Este change es el **primer módulo frontend real** y establece la base de componentes, routing y fetching que todos los módulos siguientes van a consumir.

## Goals / Non-Goals

**Goals:**

- Implementar el catálogo público de productos navegable por cualquier usuario (autenticado o no)
- Crear componentes base reutilizables (Button, Card, Input, Spinner, Skeleton, Pagination, ErrorDisplay, EmptyState)
- Configurar Router + Providers (TanStack Query, Toaster) con layout compartido
- Configurar Tailwind CSS con design tokens (colores, spacing, tipografía)
- Grilla responsive de productos con cards, badges, skeleton loaders
- Filtros: categoría (desde árbol jerárquico), búsqueda textual (debounce 300ms), rango de precio
- Paginación con controles anterior/siguiente + selector de página
- Página de detalle de producto con descripción, ingredientes (alérgenos resaltados), precio
- Estado UI del catálogo en Zustand (filtros activos, paginación, ordenamiento)
- Data fetching con TanStack Query (useQuery con refetch en cambio de filtros)

**Non-Goals:**

- Carrito de compras (es el Change 25)
- Autenticación desde el frontend (ya existe esqueletada, se completa en otro change)
- Navegación por roles (es el Change 16, existe esqueletada)
- SEO / SSR (la app es SPA)
- Tests unitarios (se agregan en change separado de testing)
- Versión mobile nativa (responsive sí, pero PWA queda fuera)

## Decisions

### 1. Tailwind CSS como framework de estilos

**Decisión**: Usar Tailwind CSS v3 con PostCSS.
**Alternativa considerada**: CSS Modules, Styled Components.
**Por qué**: El proyecto ya lo tiene como dependencia en `package.json` (mencionado en AGENTS.md) y es el estándar del equipo. Tailwind permite prototipado rápido, consistencia con design tokens, y no requiere archivos CSS separados.

### 2. Feature-Sliced Design (FSD) estricto

**Decisión**: Mantener la estructura FSD: `pages/ → features/ → entities/ → shared/`.
**Por qué**: Ya es la convención del proyecto. El catálogo se organiza como:

- `pages/CatalogPage.tsx` — orquesta la página completa
- `features/catalog/` — ProductGrid, ProductCard, ProductFilters, CategoryNav, ProductDetail
- `entities/product/` — tipos Product, ProductFilters (interfaces compartidas)
- `entities/category/` — tipo Category (interfaz compartida)
- `shared/api/catalogApi.ts` — funciones de fetching
- `shared/components/` — componentes base (Button, Card, Input, etc.)

### 3. TanStack Query para data fetching

**Decisión**: Usar `@tanstack/react-query` v5 para toda la comunicación con el backend.
**Alternativa considerada**: RTK Query, SWR, fetch + Zustand.
**Por qué**: La AGENTS.md lo especifica explícitamente como estándar. TanStack Query maneja caching, refetching, stale-while-revalidate, y estados loading/error de manera nativa. El store de Zustand solo maneja estado UI (filtros activos, página actual), NO duplica datos del servidor.

### 4. Axios instance compartido

**Decisión**: Crear un `shared/api/client.ts` que exporte un Axios instance base con `VITE_API_BASE_URL`, y que `catalogApi.ts` use ese instance.
**Alternativa considerada**: Usar fetch nativo, crear instance separado por módulo.
**Por qué**: Ya existe un Axios instance en `shared/api/authApi.ts` con interceptors (JWT + error handling). Extraemos la creación del client a un archivo compartido para que catalogApi y futuros módulos reutilicen la misma configuración base sin duplicar interceptors.

### 5. ProductDetail como página independiente

**Decisión**: El detalle de producto va en `pages/ProductDetailPage.tsx` (ruta `/catalog/:slug`), NO como modal.
**Alternativa considerada**: Modal/drawer sobre el catálogo.
**Por qué**: Una página dedicada permite URLs compartibles, mejor UX para ver la información completa (ingredientes, alérgenos, descripción larga), y es más simple de implementar. El botón "Agregar al carrito" redirige al login si no está autenticado (futuro).

### 6. CategoryNav con tree expandible inline

**Decisión**: El árbol de categorías se renderiza como sidebar expandible usando el array plano que devuelve `GET /api/v1/categorias` (ya en formato árbol anidado).
**Alternativa considerada**: Select dropdown, breadcrumbs.
**Por qué**: La API ya devuelve el árbol jerárquico. Mostrarlo como tree expandible en la sidebar del catálogo permite navegación rápida por la jerarquía. Es más informativo que un dropdown plano.

### 7. Paginación server-side con estado en URL

**Decisión**: Los parámetros de paginación (`page`, `page_size`) se sincronizan con la URL vía query params, y los filtros también.
**Alternativa considerada**: Paginación client-side, estado solo en Zustand.
**Por qué**: La API ya soporta paginación server-side. Sincronizar con la URL permite compartir URLs con filtros aplicados y mantiene el estado al navegar hacia atrás. Los valores se leen de la URL al montar el componente y se escriben en Zustand para los controles de UI.

## Risks / Trade-offs

| Riesgo                                                                                                                                             | Mitigación                                                                                                                                        |
| -------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| **El frontend no tiene Tailwind instalado** — puede haber problemas de configuración con Vite/PostCSS                                              | Incluir la configuración completa en el setup: `tailwind.config.ts`, `postcss.config.js`, directivas `@tailwind` en CSS                           |
| **El auth store existe pero el router no** — al configurar rutas públicas vs protegidas, las públicas (catálogo) deben funcionar sin autenticación | El catálogo es completamente público. La ruta no requiere ProtectedRoute. Solo se usa `get_optional_current_user()` del backend (ya implementado) |
| **El tree de categorías puede tener muchos niveles** — la navegación puede volverse profunda y el tree UI complejo                                 | Limitar a 3 niveles en UI (colapsados por defecto). Si hay más, indicar con "..." y expandir al click                                             |
| **Sin design system existente** — los componentes base creados ahora se convertirán en el estándar visual del proyecto                             | Documentar tokens de Tailwind (colores primary/secondary/accent, border-radius, spacing) y usarlos consistentemente en todos los componentes      |
| **Dependencia de paquetes no instalados** — react-router-dom, axios, @tanstack/react-query, tailwindcss no están en package.json                   | El apply phase debe instalar TODO antes de empezar a codificar                                                                                    |
