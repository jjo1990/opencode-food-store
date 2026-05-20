# Tasks: implement-catalog-frontend-ui

## 1. Project Setup — Dependencies & Config

- [x] 1.1 Install NPM dependencies: react-router-dom, @tanstack/react-query, axios, zustand, @tanstack/react-query-devtools, react-hot-toast, tailwindcss, postcss, autoprefixer
- [x] 1.2 Configure Tailwind CSS: create `tailwind.config.ts` with design tokens (colors primary/secondary/accent, font, spacing, border-radius), `postcss.config.js`, add `@tailwind` directives to stylesheet
- [x] 1.3 Extract shared Axios client from existing `authApi.ts` into `shared/api/client.ts` (base URL, JWT interceptor, error toast handler), re-export from authApi
- [x] 1.4 Create `shared/api/catalogApi.ts` with functions: `fetchProducts(filters)`, `fetchProductBySlug(slug)`, `fetchCategories()` using the shared client

## 2. Shared UI Components

- [x] 2.1 Create `shared/components/Button.tsx` — variants (primary, secondary, ghost, danger), states (disabled, loading), support `as="a"` prop
- [x] 2.2 Create `shared/components/Card.tsx` — container with shadow, border-radius, padding, optional hoverable effect
- [x] 2.3 Create `shared/components/Input.tsx` — label, placeholder, error state with red border and error message
- [x] 2.4 Create `shared/components/Spinner.tsx` — animated rotating circle with size variants (sm/md/lg)
- [x] 2.5 Create `shared/components/Skeleton.tsx` — animated pulse placeholder with variants (text, circle, card)
- [x] 2.6 Create `shared/components/Pagination.tsx` — Anterior/Siguiente buttons, page numbers with ellipsis, disabled states at boundaries
- [x] 2.7 Create `shared/components/ErrorDisplay.tsx` — error message with icon, optional retry button
- [x] 2.8 Create `shared/components/EmptyState.tsx` — title, description, icon, optional action button

## 3. Core Frontend Setup

- [x] 3.1 Create `app/router.tsx` with React Router: routes for `/catalog`, `/catalog/:slug`, and 404 catch-all, wrapped in shared layout (Header/Outlet/Footer)
- [x] 3.2 Create `app/providers.tsx` — QueryClientProvider (staleTime: 30s, retry: 1) + Toaster + Router, compose providers
- [x] 3.3 Update `main.tsx` to use Providers wrapper
- [x] 3.4 Update `App.tsx` to render the Router instead of placeholder
- [x] 3.5 Create shared layout components: `Header.tsx` (logo, nav links, auth status) and `Footer.tsx`

## 4. Domain Entities

- [x] 4.1 Create `entities/product/types.ts` — Product interface (id, nombre, slug, descripcion, precio, stock_cantidad, disponible, imagenes[], categorias[], ingredientes[])
- [x] 4.2 Create `entities/category/types.ts` — Category interface (id, nombre, slug, children: Category[])
- [x] 4.3 Create `entities/product/api.ts` — TanStack Query hooks: `useProducts(filters)`, `useProduct(slug)` with query keys, enabled conditions
- [x] 4.4 Create `entities/category/api.ts` — TanStack Query hook: `useCategories()` with staleTime extended (categorías cambian poco)

## 5. Catalog Feature Components

- [x] 5.1 Create `features/catalog/components/ProductCard.tsx` — card with image placeholder, name, price formatted, disponibilidad badge, hover effect, Link to detail
- [x] 5.2 Create `features/catalog/components/ProductGrid.tsx` — responsive grid (1/2/3-4 cols) rendering ProductCards, loading state with Skeletons, error state with ErrorDisplay, empty state with EmptyState
- [x] 5.3 Create `features/catalog/components/CategoryNav.tsx` — sidebar tree: expandable/collapsible nodes, active category highlight, "Todas las categorías" option
- [x] 5.4 Create `features/catalog/components/ProductFilters.tsx` — search input with debounce 300ms, price range inputs, category selector (wired), "Limpiar filtros" button
- [x] 5.5 Create `features/catalog/components/PaginationBar.tsx` — wrapper around shared Pagination component wired to catalog store
- [x] 5.6 Create `features/catalog/components/ProductDetail.tsx` — product info display: image, name, price, description, ingredient list (allergens highlighted), availability badge

## 6. Catalog Store (UI State)

- [x] 6.1 Create `stores/catalogStore.ts` — Zustand store with: filters (search, categoriaId, precioMin, precioMax), pagination (page, pageSize), actions (setFilter, clearFilters, setPage, nextPage, prevPage)
- [x] 6.2 Implement URL sync utils — read filters from URL search params on mount, write filters to URL on change

## 7. Pages

- [x] 7.1 Create `pages/CatalogPage.tsx` — orchestrates CategoryNav sidebar + ProductFilters bar + ProductGrid + PaginationBar, wires catalogStore to TanStack Query hooks, syncs URL params
- [x] 7.2 Create `pages/ProductDetailPage.tsx` — fetches product by slug from URL param, renders ProductDetail component with loading/error/not-found states
- [x] 7.3 Create `pages/NotFoundPage.tsx` — 404 page with message and "Volver al inicio" link
