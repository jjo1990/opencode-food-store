## Why

El dashboard administrativo necesita KPIs agregados (ventas totales, pedidos por estado, productos más vendidos, tendencias temporales) para que los administradores tomen decisiones informadas. Actualmente no existe ningún endpoint de agregación — los datos existen en las tablas pero no hay forma de consultarlos sin SQL directo. Este cambio desbloquea las historias US-056 a US-059.

## What Changes

- **Nuevo endpoint `GET /api/v1/admin/metricas/resumen`** — KPIs generales: total_ventas, cantidad_pedidos, pedidos_por_estado, usuarios_registrados
- **Nuevo endpoint `GET /api/v1/admin/metricas/ventas`** — ventas por período con granularidad configurable (día/semana/mes) y filtro de fechas
- **Nuevo endpoint `GET /api/v1/admin/metricas/productos-top`** — top 10 productos más vendidos por cantidad y monto
- **Nuevo endpoint `GET /api/v1/admin/metricas/pedidos-por-estado`** — distribución de pedidos con conteo y porcentaje
- **Nuevo `AdminMetricsRepository`** en `backend/app/admin/repository.py` — queries de agregación con SQLAlchemy func (SUM, COUNT, COALESCE, group_by)
- **Nuevos schemas Pydantic** en `backend/app/admin/schemas.py` para requests y responses
- **Nuevos métodos en `AdminService`** para cada endpoint de métricas
- **Nuevas rutas** en `backend/app/admin/router.py` bajo el prefijo `/admin/metricas`

## Capabilities

### New Capabilities

- `admin-metrics`: Endpoints de agregación para dashboard administrativo — KPIs generales, ventas por período, top productos, distribución de pedidos por estado. Acceso restringido a rol ADMIN.

### Modified Capabilities

<!-- Ninguna capacidad existente modifica sus requerimientos -->

## Impact

- **Backend**: `backend/app/admin/` — nuevos schemas, métodos en repository/service/router. Sin cambios en modelos ni migraciones.
- **Frontend**: No impactado en este change (consumirá los endpoints en un change futuro de dashboard UI).
- **Base de datos**: Solo queries de lectura (SELECT con agregación). Sin migraciones, sin nuevas tablas.
- **Dependencias**: Ninguna nueva. SQLAlchemy func ya está disponible como parte de SQLAlchemy.
- **Seguridad**: Todos los endpoints requieren `require_role("ADMIN")`. Sin exposición de datos sensibles adicional.
