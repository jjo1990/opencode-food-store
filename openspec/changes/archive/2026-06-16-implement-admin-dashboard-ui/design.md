# Design: implement-admin-dashboard-ui

## Context

El backend ya expone 4 endpoints de métricas bajo `/api/v1/admin/metricas/` (Change 40, completado). El frontend tiene un placeholder en `AdminDashboardPage.tsx` y `recharts` no está instalado. El proyecto usa FSD estricto con TanStack Query para estado servidor y Zustand para UI state.

**Restricciones existentes**:

- `staleTime: 30000` (30s) es el default del proyecto para TanStack Query
- Las páginas admin no tienen layout dedicado; cada una usa `max-w-7xl px-4 py-8` como container
- El `Sidebar` ya tiene el ítem Dashboard (`/admin`, icono 📊, sección admin)
- La navegación es lista plana (no nested children), agrupada por `section`
- Componentes compartidos disponibles: `Card`, `Spinner`, `Skeleton`, `ErrorDisplay`, `EmptyState`
- Tokens de color: `primary` (green-500), `secondary` (yellow-500), `accent` (amber-500)

## Goals / Non-Goals

**Goals:**

- Dashboard visual con 4 KPI cards, 3 gráficos (LineChart, BarChart, PieChart) y filtros de fecha/granularidad
- 100% fiel a los schemas de respuesta del backend (`MetricsResumenResponse`, `MetricsVentasResponse`, etc.)
- Responsive: 4-col → 2-col → 1-col según viewport
- Manejo de 4 estados: loading (Skeleton), error (ErrorDisplay), empty (EmptyState), data (gráficos)
- Filtros en Zustand; datos de servidor en TanStack Query; sin duplicación

**Non-Goals:**

- No modificar el backend (endpoints ya listos)
- No crear layout admin dedicado (se usa el container estándar)
- No polling automático (se usa `staleTime` de 30s, refetch manual con botón de refresco)
- No exportación de datos (fuera de scope para este change)
- No tests (cubiertos en change separado de testing)
- No animaciones complejas

## Decisions

### 1. Estructura de archivos (FSD)

```
features/dashboard/
├── hooks/useDashboardMetrics.ts      ← 4 hooks TanStack Query
└── components/
    ├── StatCard.tsx                   ← KPI card reutilizable
    ├── VentasLineChart.tsx            ← recharts LineChart
    ├── ProductosTopBarChart.tsx       ← recharts BarChart
    ├── PedidosEstadoPieChart.tsx      ← recharts PieChart
    └── DashboardFilters.tsx           ← filtros de fecha + granularidad

shared/api/dashboardApi.ts             ← 4 funciones fetch tipadas
stores/dashboardStore.ts               ← Zustand: fecha_inicio, fecha_fin, granularidad
pages/admin/AdminDashboardPage.tsx     ← reemplazo del placeholder
```

**Alternativa considerada**: poner todo en `pages/admin/dashboard/`. Rechazada — viola FSD; los gráficos son reutilizables y la lógica de queries pertenece a `features/`.

### 2. State management

**Zustand (dashboardStore)** — solo UI filters:

```ts
interface DashboardFilters {
  fechaInicio: string; // ISO date string, default: hace 30 días
  fechaFin: string; // ISO date string, default: hoy
  granularidad: 'day' | 'week' | 'month'; // default: 'day'
}
interface DashboardState {
  filters: DashboardFilters;
  setFilter: <K extends keyof DashboardFilters>(key: K, value: DashboardFilters[K]) => void;
}
```

**TanStack Query** — server data (4 hooks):

- `useDashboardResumen()` → `['dashboard', 'resumen']`
- `useDashboardVentas(filters)` → `['dashboard', 'ventas', filters]`
- `useDashboardProductosTop()` → `['dashboard', 'productos-top']`
- `useDashboardPedidosEstado()` → `['dashboard', 'pedidos-estado']`

**Por qué no polling**: los filtros cambian bajo demanda del admin; `staleTime: 30000` es suficiente. Se agrega un botón de refresco manual si el usuario quiere datos frescos.

### 3. Recharts configuration

**Colores** (mapeados desde tokens de Tailwind):

- Primary: `#22c55e` (verde) — líneas de ventas, barras principales
- Secondary: `#eab308` (amarillo) — datos secundarios
- Accent: `#f59e0b` (ámbar) — highlights
- Gray: `#9ca3af` (gray-400) — ejes, grids
- Palette para PieChart: `['#22c55e', '#eab308', '#f59e0b', '#3b82f6', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4', '#f97316', '#84cc16']`

**LineChart (ventas)**:

- XAxis: `dataKey="fecha"`, tick formatter según granularidad (DD/MM para day, "Sem N" para week, "MMM YY" para month)
- YAxis: doble eje — izquierdo: monto_total (formateado como `$XX`), derecho: cantidad_pedidos (entero)
- Tooltip: customizado con `formatter` que muestra "$XX.XX" para montos
- Legend: "Ventas ($)" y "Pedidos"
- ResponsiveContainer: width="100%", height={350}

**BarChart (top productos)**:

- Layout: horizontal (eje Y = nombre, eje X = cantidad_vendida)
- max 10 items, truncar nombre > 20 chars
- Tooltip: nombre completo + cantidad + monto_total
- ResponsiveContainer: width="100%", height={400}

**PieChart (estados)**:

- Datos: label = estado, value = cantidad
- Labels: mostrar porcentaje en tooltip (formateado a 1 decimal)
- Legend: debajo del gráfico
- Colores: palette de 10 colores para cubrir los 6 estados del FSM
- ResponsiveContainer: width="100%", height={350}

### 4. Responsive layout

```html
<!-- KPI cards: 4 cols desktop, 2 tablet, 1 mobile -->
<div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
  <StatCard ... />
</div>

<!-- Charts: 2 cols desktop, 1 mobile -->
<div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
  <VentasLineChart ... />
  <!-- ocupa 2 cols en lg con filtros -->
  <ProductosTopBarChart ... />
  <PedidosEstadoPieChart ... />
</div>
```

El `VentasLineChart` con sus filtros ocupa ancho completo (col-span-2 en lg) porque el LineChart necesita espacio horizontal.

### 5. Date defaults y formato

- `fechaInicio`: `new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]`
- `fechaFin`: `new Date().toISOString().split('T')[0]`
- Formato en query params: `YYYY-MM-DD` (lo que espera el backend con tipo `date`)
- Los inputs de fecha usan `<input type="date">` nativo del navegador

### 6. Data flow

```
DashboardFilters (Zustand) ──fechaInicio, fechaFin, granularidad──▶ useDashboardVentas()
                                                                     useDashboardResumen()
                                                                     useDashboardProductosTop()
                                                                     useDashboardPedidosEstado()
                                                                         │
                                                                         ▼
                                                              dashboardApi.ts (fetch functions)
                                                                         │
                                                                         ▼
                                                              GET /api/v1/admin/metricas/*
```

Al cambiar un filtro → se actualiza Zustand → TanStack Query detecta cambio en queryKey → refetch automático.

## Risks / Trade-offs

| Risk                                                                                 | Mitigation                                                         |
| ------------------------------------------------------------------------------------ | ------------------------------------------------------------------ |
| `recharts` no está instalado → error en build                                        | Tarea 1.1: `npm install recharts` como primer paso                 |
| Endpoints pueden devolver arrays vacíos (sin ventas en período)                      | Cada gráfico maneja el estado empty con `EmptyState`               |
| PieChart con pocos estados vs palette de muchos colores                              | Usar solo los colores necesarios (slice del array de palette)      |
| Nombres de producto largos rompen el layout del BarChart                             | Truncar a 20 caracteres + "...", tooltip muestra nombre completo   |
| El admin podría necesitar fechas más allá de 30 días                                 | Los inputs de fecha son libres; 30 días es solo el default inicial |
| Migrar de placeholder a dashboard completo puede ser mucho código en un solo archivo | Separado en 7 archivos pequeños siguiendo FSD                      |
