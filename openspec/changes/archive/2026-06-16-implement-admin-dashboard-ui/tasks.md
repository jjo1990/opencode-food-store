# Tasks: implement-admin-dashboard-ui

## 1. Setup & Dependencies

- [x] 1.1 Install recharts: `npm install recharts` in `frontend/`
- [x] 1.2 Create `features/dashboard/` directory structure (hooks/, components/)
- [x] 1.3 Create `shared/api/dashboardApi.ts` with TypeScript interfaces matching backend schemas
- [x] 1.4 Create `stores/dashboardStore.ts` with Zustand store for fechaInicio, fechaFin, granularidad

## 2. API Client

- [x] 2.1 Implement `fetchDashboardResumen()` → `GET /admin/metricas/resumen` with return type `MetricsResumenResponse`
- [x] 2.2 Implement `fetchDashboardVentas(fechaInicio, fechaFin, granularidad)` → `GET /admin/metricas/ventas` with query params
- [x] 2.3 Implement `fetchDashboardProductosTop()` → `GET /admin/metricas/productos-top`
- [x] 2.4 Implement `fetchDashboardPedidosEstado()` → `GET /admin/metricas/pedidos-por-estado`

## 3. TanStack Query Hooks

- [x] 3.1 Implement `useDashboardResumen()` hook with queryKey `['dashboard', 'resumen']` and `staleTime: 30000`
- [x] 3.2 Implement `useDashboardVentas(filters)` hook with queryKey `['dashboard', 'ventas', fechaInicio, fechaFin, granularidad]` and `enabled` guard
- [x] 3.3 Implement `useDashboardProductosTop()` hook with queryKey `['dashboard', 'productos-top']`
- [x] 3.4 Implement `useDashboardPedidosEstado()` hook with queryKey `['dashboard', 'pedidos-estado']`

## 4. UI Components

- [x] 4.1 Create `StatCard` component: icon, label, value, color accent, loading skeleton state, accepts `className`
- [x] 4.2 Create `DashboardFilters` component: two `<input type="date">` + button tabs for granularidad, reads/writes `dashboardStore`
- [x] 4.3 Create `VentasLineChart` component: `LineChart` with dual Y axis, tooltip, legend, loading/error/empty states
- [x] 4.4 Create `ProductosTopBarChart` component: horizontal `BarChart`, truncate labels, tooltip, loading/error/empty states
- [x] 4.5 Create `PedidosEstadoPieChart` component: `PieChart` with legend, percentage tooltip, loading/error/empty states

## 5. Page Assembly

- [x] 5.1 Replace `AdminDashboardPage.tsx` placeholder with full dashboard layout
- [x] 5.2 Layout KPI cards in responsive grid (4-col desktop, 2-col tablet, 1-col mobile)
- [x] 5.3 Layout `VentasLineChart` with `DashboardFilters` in a full-width section above other charts
- [x] 5.4 Layout `ProductosTopBarChart` and `PedidosEstadoPieChart` side by side on desktop, stacked on mobile
- [x] 5.5 Add manual refetch button at top-right corner of dashboard

## 6. Polish & Verify

- [x] 6.1 Verify all 4 TanStack Query hooks handle loading/error/empty/content states correctly
- [x] 6.2 Verify responsive layout at 3 breakpoints (mobile <640px, tablet 640-1023px, desktop >=1024px)
- [x] 6.3 Verify chart colors match Tailwind tokens (primary, secondary, accent)
- [x] 6.4 Verify date format compatibility with backend (`YYYY-MM-DD` as ISO date string)
- [x] 6.5 Run `npx tsc --noEmit` in `frontend/` — no TypeScript errors
