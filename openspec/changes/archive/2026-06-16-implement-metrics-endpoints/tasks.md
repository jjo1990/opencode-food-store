## 1. Schemas — admin/schemas.py

- [x] 1.1 Crear `MetricsResumenResponse` con campos: total_ventas (float), cantidad_pedidos (int), pedidos_por_estado (dict[str, int]), usuarios_registrados (int)
- [x] 1.2 Crear `MetricsVentasItem` con campos: fecha (str), monto_total (float), cantidad_pedidos (int)
- [x] 1.3 Crear `MetricsVentasResponse` con campo items: list[MetricsVentasItem]
- [x] 1.4 Crear `MetricsProductoTopItem` con campos: producto_id (UUID), nombre (str), cantidad_vendida (int), monto_total (float)
- [x] 1.5 Crear `MetricsProductoTopResponse` con campo items: list[MetricsProductoTopItem]
- [x] 1.6 Crear `MetricsPedidosEstadoItem` con campos: estado (str), cantidad (int), porcentaje (float)
- [x] 1.7 Crear `MetricsPedidosEstadoResponse` con campo items: list[MetricsPedidosEstadoItem]
- [x] 1.8 Agregar los nuevos schemas al `__init__.py` de schemas si existe, o asegurar imports directos desde `admin.schemas`

## 2. Repository — admin/repository.py

- [x] 2.1 Crear clase `AdminMetricsRepository` con constructor que recibe `db: Session`
- [x] 2.2 Implementar `get_resumen()` — 4 queries: COUNT users, COUNT pedidos, COALESCE(SUM(total)), GROUP BY estado_codigo. Retorna dict con los 4 KPIs.
- [x] 2.3 Implementar `get_ventas_por_periodo(fecha_inicio, fecha_fin)` — query con DATE(created_at), SUM(total), COUNT(id) agrupado por dia, filtrado por rango de fechas y soft_deleted_at IS NULL. Retorna list[dict].
- [x] 2.4 Implementar `get_productos_top(limit=10)` — query con JOIN DetallePedido→Pedido, SUM(cantidad), SUM(subtotal) agrupado por producto_id y nombre_snapshot, filtrado por pedido.soft_deleted_at IS NULL, ordenado por cantidad DESC. Retorna list[dict].
- [x] 2.5 Implementar `get_pedidos_por_estado()` — query con GROUP BY estado_codigo y COUNT(id), filtrado por soft_deleted_at IS NULL. Retorna list[dict].

## 3. Service — admin/service.py

- [x] 3.1 Agregar `self.metrics_repo = AdminMetricsRepository(db)` en `__init__`
- [x] 3.2 Implementar `get_metrics_resumen()` — llama a `metrics_repo.get_resumen()`, construye y retorna `MetricsResumenResponse`
- [x] 3.3 Implementar `get_metrics_ventas(fecha_inicio, fecha_fin, granularidad)`:
  - Validar que fecha_inicio < fecha_fin
  - Validar que el rango no exceda 365 dias
  - Validar granularidad en {"day", "week", "month"}
  - Llamar a `metrics_repo.get_ventas_por_periodo()`
  - Post-procesar en Python: si granularidad es "week", agrupar por ISO week; si "month", agrupar por YYYY-MM; si "day", devolver directo
  - Formatear fecha segun granularidad
  - Retornar `MetricsVentasResponse`
- [x] 3.4 Implementar `get_metrics_productos_top()` — llama a `metrics_repo.get_productos_top()`, construye y retorna `MetricsProductoTopResponse`
- [x] 3.5 Implementar `get_metrics_pedidos_por_estado()` — llama a `metrics_repo.get_pedidos_por_estado()`, calcula total y porcentajes en Python, construye y retorna `MetricsPedidosEstadoResponse`

## 4. Router — admin/router.py

- [x] 4.1 Agregar imports de los nuevos schemas (MetricsResumenResponse, MetricsVentasResponse, MetricsProductoTopResponse, MetricsPedidosEstadoResponse)
- [x] 4.2 Agregar `GET /admin/metricas/resumen` con `response_model=MetricsResumenResponse`, `require_role("ADMIN")`
- [x] 4.3 Agregar `GET /admin/metricas/ventas` con `response_model=MetricsVentasResponse`, query params fecha_inicio/fecha_fin/granularidad, `require_role("ADMIN")`
- [x] 4.4 Agregar `GET /admin/metricas/productos-top` con `response_model=MetricsProductoTopResponse`, `require_role("ADMIN")`
- [x] 4.5 Agregar `GET /admin/metricas/pedidos-por-estado` con `response_model=MetricsPedidosEstadoResponse`, `require_role("ADMIN")`

## 5. Tests

- [x] 5.1 Crear test para `GET /admin/metricas/resumen` — verificar estructura de respuesta, valores con datos de prueba, respuesta con BD vacia, 403 sin rol ADMIN, 401 sin auth
- [x] 5.2 Crear test para `GET /admin/metricas/ventas` — verificar granularidad day/week/month, rango invalido, rango >365 dias, granularidad invalida, periodo sin datos
- [x] 5.3 Crear test para `GET /admin/metricas/productos-top` — verificar orden descendente, limite 10, sin datos, soft-deleted excluidos
- [x] 5.4 Crear test para `GET /admin/metricas/pedidos-por-estado` — verificar porcentajes suman ~100%, sin pedidos, un solo estado
- [x] 5.5 Verificar que `soft_deleted_at` filtra correctamente en todas las metricas

## 6. Verification

- [x] 6.1 Ejecutar tests con `pytest` y verificar que todos pasan (SQLite)
- [x] 6.2 Verificar que los endpoints aparecen en Swagger UI (`/docs`)
- [x] 6.3 Verificar que los endpoints responden correctamente con `curl` o cliente HTTP
- [x] 6.4 Revisar que no haya regresiones en endpoints admin existentes
