## Why

El backend del catálogo está completo (categorías, ingredientes, productos CRUD + API pública con role-aware filtering), pero los clientes no pueden navegar los productos porque **no existe una interfaz de usuario**. Sin el frontend del catálogo, el sistema es solo una API sin valor comercial visible.

Este change es el que **habilita la experiencia de compra**: el primer módulo frontend que ve un cliente real.

## What Changes

1. **Router + Providers** — Configurar React Router con layout compartido (Header/Nav/Footer), QueryClientProvider para TanStack Query, Toaster
2. **Catalog API client** — Cliente Axios para consumir `GET /api/v1/catalog/productos` con filtros (categoría, precio, búsqueda) y `GET /api/v1/categorias`
3. **Catalog store** — Zustand store para estado UI del catálogo (filtros activos, paginación, ordenamiento)
4. **ProductGrid** — Grilla responsive de productos con cards (imagen, nombre, precio, badge disponible/agotado)
5. **ProductDetail** — Página/modal de detalle con descripción, ingredientes (alérgenos resaltados), precio, botón "Agregar al carrito"
6. **CategoryNav** — Navegación jerárquica de categorías (tree expandible)
7. **Filters** — Filtros: selector de categoría, búsqueda con debounce 300ms, rango precio con sliders, botón limpiar
8. **Pagination** — Paginación con botones anterior/siguiente + selector de página
9. **Skeleton loaders** — Estados de carga durante fetch de datos
10. **Shared UI components** — Crear componentes base: Button, Card, Input, Spinner, Skeleton, Pagination, ErrorDisplay, EmptyState

## Capabilities

### New Capabilities

- `catalog-frontend`: Catálogo público de productos con navegación, filtros, búsqueda y detalle de producto — consumiendo `catalog-public-api`
- `shared-ui`: Componentes base reutilizables del design system (Button, Card, Input, Spinner, Skeleton, Pagination, ErrorDisplay, EmptyState)
- `frontend-core-setup`: Configuración base del frontend (Router, Providers, TanStack Query client, Axios client base)

### Modified Capabilities

- Ninguna. Es la primera interfaz frontend real.

## Impact

- **Dependencias NPM a agregar**: react-router-dom, axios, @tanstack/react-query, zustand (ya usado pero no instalado formalmente), tailwindcss, postcss, autoprefixer
- **Archivos nuevos**: ~20-25 archivos en frontend/src/ (app/, pages/catalog/, features/catalog/, entities/product/, entities/category/, shared/api/, shared/components/, stores/)
- **Archivos a modificar**: frontend/src/main.tsx (agregar providers), frontend/src/App.tsx (router), frontend/package.json, frontend/vite.config.ts (si necesita alias), frontend/tsconfig.json (si necesita paths)
- **Backend**: sin cambios
