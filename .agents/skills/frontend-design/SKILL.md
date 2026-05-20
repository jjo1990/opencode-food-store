---
name: frontend-design
description: >
  Frontend development patterns for Food Store React + TypeScript + Vite project.
  Covers FSD structure, TanStack Query, Zustand, Axios client, shared UI components,
  Tailwind tokens, and URL state sync.
  Trigger: Creating or modifying any React component in frontend/src/.
license: Apache-2.0
metadata:
  author: gentleman-programming
  version: '1.0'
---

## When to Use

- Creating new pages, features, entities, or shared components
- Writing TanStack Query hooks (useQuery, useMutation)
- Creating or modifying Zustand stores
- Working with the Axios API client and interceptors
- Using Tailwind CSS classes with design tokens
- Implementing URL state synchronization
- Building forms with @tanstack/react-form

## Critical Patterns

### 1. FSD Import Flow (STRICT — no exceptions)

Imports flow ONLY downward. Never import from features into entities, or from pages into shared.

```
pages/   → imports from features/, entities/, shared/
features/ → imports from entities/, shared/
entities/ → imports from shared/, external libs only
shared/   → imports from external libs only (NO project imports)
```

### 2. Every Data-Fetching Component MUST Handle 4 States

Every component that receives TanStack Query data must handle:

```tsx
const { data, isLoading, isError, error, refetch } = useQuery(...);

if (isLoading) return <Skeleton variant="card" />;
if (isError) return <ErrorDisplay message={error?.message} onRetry={refetch} />;
if (!data || data.length === 0) return <EmptyState title="Sin resultados" description="..." />;
return <ActualContent data={data} />;
```

Pattern: **Loading → Error → Empty → Content**

### 3. TanStack Query — Server State ONLY

- All server data fetching uses `@tanstack/react-query` v5
- NEVER duplicate server data in Zustand stores
- QueryClient defaults: `staleTime: 30000` (30s), `retry: 1`
- Use `placeholderData: (prev) => prev` for paginated lists (keeps old data visible while fetching)
- Query keys follow: `[resource, ...filters]` pattern: `['products', filters]`, `['product', slug]`, `['categories']`
- Use `enabled: !!param` for conditional queries (e.g. product detail needs a slug)
- Extended `staleTime` for data that rarely changes (e.g. categories)

### 4. Zustand — Client/UI State ONLY

- Zustand stores hold ONLY UI state (filters, pagination, modals, toasts)
- NEVER store server data in Zustand (use TanStack Query)
- For generically-typed filters with a keyed setter, use a generic:

```tsx
interface Filters {
  search: string;
  categoriaId: string | null; /* ... */
}
interface State {
  filters: Filters;
  page: number;
  setFilter: <K extends keyof Filters>(key: K, value: Filters[K]) => void;
  clearFilters: () => void;
}
```

- Changing a filter ALWAYS resets `page` to 1
- Actions are plain functions in `set()` — no async thunks needed for UI state

### 5. Axios Client — Shared Instance

Use the shared client from `shared/api/client.ts` (default export: `client`). It includes:

- baseURL from `VITE_API_BASE_URL` env var (fallback: `http://localhost:8000/api/v1`)
- Request interceptor: attaches JWT from `authStore.accessToken`
- Response interceptor: toast error messages in Spanish, clears tokens on 401

API modules in `shared/api/` import `client` and export plain async functions:

```tsx
import client from './client';
export async function fetchProducts(filters: ProductFilters): Promise<ProductListResponse> {
  const { data } = await client.get('/catalog/productos', { params: filters });
  return data;
}
```

### 6. URL State Sync Pattern

Filters and pagination sync with URL search params (NOT with React state alone):

1. On mount: `parseFiltersFromURL()` → set Zustand state (ONE-TIME effect)
2. On filter change: update Zustand → `serializeFilters()` → `setSearchParams(qs, { replace: true })`
3. useCallback wrappers avoid recreating handlers on every render
4. `serializeFilters()` only includes params that differ from defaults

```tsx
// In page component:
useEffect(() => {
  const parsed = parseFiltersFromURL(searchParams);
  setFilter('search', parsed.filters.search);
  setPage(parsed.page);
}, []); // ONE-TIME on mount

const syncUrl = useCallback(() => {
  const filters = useCatalogStore.getState().filters;
  const qs = serializeFilters(filters, page, pageSize);
  setSearchParams(qs, { replace: true });
}, [setSearchParams]);
```

### 7. Debounced Search Pattern

Search input uses local state + debounced callback to avoid API calls on every keystroke:

```tsx
const [localSearch, setLocalSearch] = useState(search);
useEffect(() => {
  setLocalSearch(search);
}, [search]);
const debouncedSearch = useCallback(
  (() => {
    let timer: ReturnType<typeof setTimeout>;
    return (value: string) => {
      clearTimeout(timer);
      timer = setTimeout(() => onSearchChange(value), 300);
    };
  })(),
  [onSearchChange]
);
```

### 8. Shared Component Contract

Every shared component in `shared/components/`:

- Accepts `className?: string` for Tailwind extension
- Is fully typed with interfaces (NO `any`)
- Default exports + named exports (support both)
- Pure presentational — NO data fetching, NO store access
- Uses Tailwind exclusively, no CSS modules or inline styles

### 9. Tailwind Design Tokens

Custom tokens defined in `tailwind.config.ts`:

| Token        | Value                  | Usage                                  |
| ------------ | ---------------------- | -------------------------------------- |
| `primary`    | `#22c55e` (green-500)  | Main CTAs, links, price, active states |
| `secondary`  | `#eab308` (yellow-500) | Badges, accents                        |
| `accent`     | `#f59e0b` (amber-500)  | Highlights, warnings                   |
| `rounded-lg` | `0.75rem`              | Cards, buttons, inputs                 |
| `rounded-xl` | `1rem`                 | Cards with image, modals               |

Full palette: `primary-50` through `primary-900`, same for secondary and accent.

### 10. Layout Pattern

All pages use a shared layout via router:

```tsx
// In router.tsx — Layout wraps all routes
function Layout() {
  return (
    <div className="flex min-h-screen flex-col">
      <Header />
      <main className="flex-1">
        <Outlet />
      </main>
      <Footer />
    </div>
  );
}
```

Content containers: `mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8`

## Code Examples

### Complete Page Pattern (loading/error/empty/data)

```tsx
export function MyPage() {
  const { data, isLoading, isError, error, refetch } = useMyData();

  if (isLoading) return <Skeleton variant="card" count={6} />;
  if (isError) return <ErrorDisplay message={(error as Error).message} onRetry={refetch} />;
  if (!data || data.length === 0)
    return <EmptyState title="Sin datos" description="No hay elementos" />;

  return <DataGrid items={data} />;
}
```

### TanStack Query Hook Pattern

```tsx
export function useProducts(filters: ProductFilters) {
  return useQuery<ProductListResponse>({
    queryKey: ['products', filters],
    queryFn: () => fetchProducts(filters),
    placeholderData: (prev) => prev,
  });
}

export function useProduct(slug: string) {
  return useQuery<Product>({
    queryKey: ['product', slug],
    queryFn: () => fetchProductBySlug(slug),
    enabled: !!slug,
  });
}
```

### Entity Types Pattern

```tsx
// entities/product/types.ts — flat types matching API response
export interface Product {
  id: string;
  nombre: string;
  slug: string;
  precio: number;
  disponible: boolean;
  imagenes: { url: string; orden: number }[];
  // ... more fields
}

export interface ProductListResponse {
  items: Product[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}
```

### Zustand Store Pattern

```tsx
import { create } from 'zustand';

interface State {
  /* UI-only state */
}
interface Actions {
  /* updaters */
}

export const useStore = create<State & Actions>()((set) => ({
  // initial state
  // actions use set() only — no async
}));
```

### API Client Module Pattern

```tsx
import client from './client';

export async function fetchProducts(filters: ProductFilters): Promise<ProductListResponse> {
  const { data } = await client.get('/catalog/productos', { params: filters });
  return data;
}
```

## Commands

```bash
# Type-check the frontend
npx tsc --noEmit

# Lint (once configured)
npx eslint src/

# Build
npm run build

# Dev server
npm run dev
```

## Resources

- **Spec-driven development**: See `openspec/` directory for active changes
- **Backend API docs**: `http://localhost:8000/docs` (Swagger)
- **Project conventions**: See `AGENTS.md` root

## Related Skills

- `tailwind-design-system` — UI tokens, component variants, and visual patterns if available
