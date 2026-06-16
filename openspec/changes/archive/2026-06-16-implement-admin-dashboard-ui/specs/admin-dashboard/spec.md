# Spec: admin-dashboard

## Overview

Dashboard administrativo que muestra KPIs del negocio (ventas, pedidos, usuarios), gráficos de tendencias (ventas por período, top productos, distribución de estados) y filtros de fecha/granularidad. Consume los endpoints de métricas del backend (`/api/v1/admin/metricas/*`). Solo accesible para usuarios con rol ADMIN.

## ADDED Requirements

### Requirement: Dashboard KPI summary cards

The system SHALL display four KPI cards in the admin dashboard showing: total sales (today and current month), pending orders count, registered users count, and delivered orders count.

#### Scenario: Admin loads dashboard and sees KPI summary

- **WHEN** an ADMIN user navigates to `/admin`
- **THEN** the system fetches `GET /admin/metricas/resumen`
- **AND** displays four stat cards with: total ventas (formatted as currency), pedidos pendientes count, usuarios registrados count, and órdenes entregadas count
- **AND** each card shows an icon, label, and value with appropriate color

#### Scenario: KPI data loads successfully with values

- **WHEN** the resumen endpoint returns `{ total_ventas: 45000.50, cantidad_pedidos: 120, pedidos_por_estado: { PENDIENTE: 15, CONFIRMADO: 30, EN_PREPARACION: 25, EN_CAMINO: 20, ENTREGADO: 25, CANCELADO: 5 }, usuarios_registrados: 89 }`
- **THEN** the cards display: "Ventas Totales: $45,000.50", "Pedidos Pendientes: 15", "Usuarios: 89", "Entregados: 25"

#### Scenario: KPI endpoint fails

- **WHEN** the resumen endpoint returns an error
- **THEN** the system displays an `ErrorDisplay` component with error message and a "Reintentar" button
- **AND** the retry button triggers a refetch

#### Scenario: KPI data is loading

- **WHEN** the resumen query is in loading state
- **THEN** the system displays `Skeleton` placeholders in each of the four card positions

### Requirement: Sales time-series line chart

The system SHALL display a line chart showing sales over time with configurable date range and granularity (day/week/month).

#### Scenario: Admin views sales chart with default 30-day range

- **WHEN** an ADMIN user loads the dashboard with default filters (last 30 days, granularity = day)
- **THEN** the system fetches `GET /admin/metricas/ventas?fecha_inicio=<30d ago>&fecha_fin=<today>&granularidad=day`
- **AND** displays a `LineChart` with two lines: "Ventas ($)" (monto_total) and "Pedidos" (cantidad_pedidos)
- **AND** the X axis shows dates formatted as DD/MM and the Y axis shows amounts

#### Scenario: Admin changes granularity to week

- **WHEN** the admin selects granularity "week" from the dropdown
- **THEN** the `granularidad` Zustand filter updates to "week"
- **AND** the ventas query refetches with `granularidad=week`
- **AND** the chart updates to show weekly aggregation with X axis labels as "Sem N"

#### Scenario: Admin changes date range

- **WHEN** the admin picks a new `fecha_inicio` or `fecha_fin` via date inputs
- **THEN** the corresponding Zustand filter updates
- **AND** the ventas query refetches with the new date range

#### Scenario: No sales data for selected period

- **WHEN** the ventas endpoint returns `{ items: [] }` (no sales in selected range)
- **THEN** the chart area displays an `EmptyState` with title "Sin datos de ventas" and description "No hay ventas registradas en el período seleccionado"

#### Scenario: Sales data is loading

- **WHEN** the ventas query is in loading state
- **THEN** the chart area displays a `Skeleton` variant="card" placeholder

### Requirement: Top products bar chart

The system SHALL display a horizontal bar chart showing the top 10 most sold products by quantity.

#### Scenario: Admin views top products chart

- **WHEN** an ADMIN user loads the dashboard
- **THEN** the system fetches `GET /admin/metricas/productos-top`
- **AND** displays a horizontal `BarChart` with product names on the Y axis and cantidad_vendida on the X axis
- **AND** shows at most 10 products sorted by quantity sold descending

#### Scenario: Product names are long

- **WHEN** a product name exceeds 20 characters
- **THEN** the chart truncates the label to 20 chars + "..."
- **AND** the tooltip shows the full product name with cantidad_vendida and monto_total

#### Scenario: No products sold yet

- **WHEN** the productos-top endpoint returns `{ items: [] }`
- **THEN** the chart area displays an `EmptyState` with title "Sin productos vendidos" and description "Aún no hay ventas registradas en el sistema"

### Requirement: Order status distribution pie chart

The system SHALL display a pie chart showing the distribution of orders by their current state, including percentages.

#### Scenario: Admin views order status distribution

- **WHEN** an ADMIN user loads the dashboard
- **THEN** the system fetches `GET /admin/metricas/pedidos-por-estado`
- **AND** displays a `PieChart` where each slice represents one order state
- **AND** each slice shows the state name, count, and percentage in the tooltip
- **AND** a legend below the chart maps colors to state names

#### Scenario: Order status includes all FSM states

- **WHEN** the pedidos-por-estado endpoint returns items for states PENDIENTE, CONFIRMADO, EN_PREPARACION, EN_CAMINO, ENTREGADO, and CANCELADO
- **THEN** the pie chart displays all six states with distinct colors from the dashboard color palette
- **AND** percentages sum to 100%

#### Scenario: No orders exist yet

- **WHEN** the pedidos-por-estado endpoint returns `{ items: [] }`
- **THEN** the chart area displays an `EmptyState` with title "Sin pedidos" and description "Aún no hay pedidos registrados en el sistema"

### Requirement: Dashboard date filters

The system SHALL provide date range inputs and a granularity selector to filter the sales chart.

#### Scenario: Default filter values on first load

- **WHEN** an ADMIN user first loads the dashboard
- **THEN** the date filters default to: `fecha_inicio` = 30 days ago, `fecha_fin` = today, `granularidad` = "day"
- **AND** the sales chart fetches data with these defaults

#### Scenario: Admin changes date range and chart updates

- **WHEN** the admin selects new start and end dates via `<input type="date">` controls
- **THEN** the Zustand store updates `fechaInicio` and `fechaFin`
- **AND** the ventas query automatically refetches with the new date params

#### Scenario: Admin selects week granularity

- **WHEN** the admin selects "Semana" from the granularity `<select>` dropdown
- **THEN** the Zustand store updates `granularidad` to "week"
- **AND** the ventas query refetches with `granularidad=week`

### Requirement: Responsive dashboard layout

The system SHALL adapt the dashboard layout for desktop, tablet, and mobile viewports.

#### Scenario: Desktop viewport (>=1024px)

- **WHEN** the viewport width is >= 1024px
- **THEN** KPI cards display in a 4-column grid
- **AND** charts display in a 2-column grid with the sales chart spanning full width above the other two charts

#### Scenario: Tablet viewport (640px - 1023px)

- **WHEN** the viewport width is between 640px and 1023px
- **THEN** KPI cards display in a 2-column grid
- **AND** charts stack vertically in a single column

#### Scenario: Mobile viewport (<640px)

- **WHEN** the viewport width is < 640px
- **THEN** KPI cards display in a single column
- **AND** charts stack vertically with reduced height (250px for pie/bar, 200px for line)
- **AND** date filter inputs stack vertically

### Requirement: Admin-only access control

The system SHALL restrict dashboard access to users with the ADMIN role only.

#### Scenario: ADMIN user accesses dashboard

- **WHEN** a user with ADMIN role navigates to `/admin`
- **THEN** the dashboard page renders with all metrics and charts

#### Scenario: Non-ADMIN user attempts to access dashboard

- **WHEN** a user without ADMIN role navigates to `/admin`
- **THEN** the `ProtectedRoute` component redirects them or shows a forbidden message
- **AND** no metrics data is fetched
