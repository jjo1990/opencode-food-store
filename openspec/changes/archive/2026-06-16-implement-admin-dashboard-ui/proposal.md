# Proposal: implement-admin-dashboard-ui

## Why

El admin necesita visibilidad inmediata del estado del negocio (ventas, pedidos, productos, usuarios) sin tener que consultar múltiples secciones ni construir reportes manualmente. Los endpoints de métricas del backend ya están completos (Change 40), pero el frontend solo muestra un placeholder "Próximamente". Sin dashboard, los endpoints están infrautilizados y el admin opera a ciegas.

## What Changes

- Reemplazar el placeholder `AdminDashboardPage.tsx` con un dashboard completo de 4 widgets de métricas
- Instalar `recharts` como dependencia de visualización de gráficos
- Crear módulo `features/dashboard/` con componentes de gráficos y hooks de consulta
- Crear `shared/api/dashboardApi.ts` con 4 funciones fetch para cada endpoint de métricas
- Crear `stores/dashboardStore.ts` (Zustand) para filtros de fecha y granularidad
- Crear componentes: `StatCard`, `VentasLineChart`, `ProductosTopBarChart`, `PedidosEstadoPieChart`, `DashboardFilters`
- Usar KPI cards para: Total ventas (hoy/mes), Pedidos pendientes, Usuarios registrados, Órdenes entregadas
- Usar `LineChart` de recharts para ventas por día/semana/mes con selector de granularidad
- Usar `BarChart` para top 10 productos vendidos
- Usar `PieChart` para distribución de pedidos por estado con porcentajes
- Layout responsive con Tailwind grid: 4 columnas en desktop, 2 en tablet, 1 en mobile

## Capabilities

### New Capabilities

- `admin-dashboard`: Dashboard administrativo con KPIs, gráficos de ventas (LineChart), top productos (BarChart), distribución de pedidos (PieChart), y filtros de rango de fechas y granularidad.

### Modified Capabilities

(Ninguna — no se modifican specs existentes; es una capacidad nueva)

## Impact

- **frontend/src/pages/admin/AdminDashboardPage.tsx**: reemplazo completo del placeholder
- **frontend/src/features/dashboard/**: nuevo módulo FSD con hooks y componentes de gráficos
- **frontend/src/shared/api/dashboardApi.ts**: nuevo módulo de API
- **frontend/src/stores/dashboardStore.ts**: nuevo store Zustand
- **frontend/package.json**: nueva dependencia `recharts`
- **Backend**: sin cambios (endpoints ya existen en Change 40)
- **Router**: sin cambios (ruta `/admin` ya configurada con `ProtectedRoute allowedRoles={['ADMIN']}`)
- **Navigation/Sidebar**: sin cambios (ítem Dashboard ya existe)
