## Context

Food Store necesita endpoints de agregación para el dashboard administrativo. Los datos existen en las tablas `pedido`, `detalle_pedido`, `user` y `estado_pedido`, pero no hay queries de agregación en el codebase. Este es el primer uso de `sqlalchemy.func` (SUM, COUNT, COALESCE) y `group_by()` en el proyecto.

El backend usa PostgreSQL en producción pero SQLite en tests. Las funciones de fecha deben ser dialect-aware o manejarse en Python para evitar incompatibilidades (SQLite usa `strftime`, PostgreSQL usa `date_trunc`).

## Goals / Non-Goals

**Goals:**

- Proveer 4 endpoints GET de solo lectura para el dashboard administrativo
- Usar el patrón existente Router → Service → Repository → Model
- Reutilizar `AdminService` y el router `admin` existente
- Mantener compatibilidad con SQLite (tests) y PostgreSQL (producción)
- Filtrar registros soft-deleted en todas las queries de métricas

**Non-Goals:**

- No crear un router separado para métricas (se mantiene en el admin router)
- No implementar cacheo ni materialización de métricas (se puede agregar después)
- No implementar frontend del dashboard (será un change separado)
- No modificar modelos ni crear migraciones

## Decisions

### 1. Nuevo `AdminMetricsRepository` en `admin/repository.py`

**Rationale**: Los repositorios existentes (`AdminUserRepository`, `AdminOrderRepository`, etc.) manejan queries de listado con filtros. Las queries de agregación son conceptualmente distintas — devuelven datos agregados, no entidades. Un repositorio separado mantiene la cohesión y sigue el Single Responsibility Principle.

**Trade-off**: Agrega una clase más al archivo `repository.py`, pero evita mezclar concerns de listado y agregación en los repositorios existentes.

### 2. Date bucketing en Python, no en SQL

**Rationale**: PostgreSQL usa `date_trunc('day', created_at)` y SQLite usa `strftime('%Y-%m-%d', created_at)`. Son incompatibles. Hacer el bucketing en Python evita SQL dialect-specific y mantiene los tests funcionando con SQLite sin configuración adicional.

**Implementación**: La query SQL agrupa por `DATE(created_at)` (funciona en ambos dialects para truncado a día). Para granularidad `week` y `month`, se hace post-procesamiento en Python agrupando por `isocalendar()` o `strftime('%Y-%m')`.

**Trade-off**: Transfiere más datos del motor de BD a la aplicación para granularidades mayores a día. Para un dashboard con volúmenes moderados esto es aceptable. Si el volumen crece significativamente, se puede migrar a `date_trunc` con detección de dialect.

### 3. Cálculo de porcentajes en Python

**Rationale**: Los porcentajes en `pedidos-por-estado` se calculan como `cantidad / total_pedidos * 100`. Hacerlo en Python es más simple y legible que con window functions SQL. Además, el total de pedidos se obtiene en la misma query.

**Trade-off**: Dos queries en lugar de una (una para conteos por estado, otra para el total). Pero son queries ligeras y el overhead es mínimo.

### 4. Endpoints bajo el router admin existente con prefijo `/metricas`

**Rationale**: El router `admin` ya está montado en `/api/v1/admin`. Agregar las rutas `/metricas/*` bajo el mismo router mantiene la consistencia con los endpoints existentes (`/admin/usuarios`, `/admin/pedidos`, `/admin/productos`, etc.). No se necesita un router separado.

**URLs resultantes**:

- `GET /api/v1/admin/metricas/resumen`
- `GET /api/v1/admin/metricas/ventas`
- `GET /api/v1/admin/metricas/productos-top`
- `GET /api/v1/admin/metricas/pedidos-por-estado`

### 5. `Pedido.total` como fuente de revenue, no sumar detalles

**Rationale**: La columna `Pedido.total` ya almacena el monto total del pedido (subtotal + costo_envio). Sumar `DetallePedido.subtotal` sería incorrecto porque no incluye el costo de envío y podría diverger de `Pedido.total` si hay descuentos o ajustes. Para revenue total y revenue por fecha, se usa `SUM(Pedido.total)`.

**Trade-off**: Si en el futuro se necesita revenue por producto individual, se debe usar `DetallePedido.subtotal`. Para revenue agregado, `Pedido.total` es la fuente canónica.

### 6. Endpoints solo para rol ADMIN

**Rationale**: Las métricas del dashboard son información sensible del negocio. Solo los administradores deben acceder. Los roles STOCK y PEDIDOS tienen acceso a endpoints operativos pero no a KPIs financieros agregados.

## Architecture

```
Router (admin/router.py)
  └─ GET /admin/metricas/resumen       → service.get_metrics_resumen()
  └─ GET /admin/metricas/ventas        → service.get_metrics_ventas(fecha_inicio, fecha_fin, granularidad)
  └─ GET /admin/metricas/productos-top → service.get_metrics_productos_top()
  └─ GET /admin/metricas/pedidos-por-estado → service.get_metrics_pedidos_por_estado()

Service (admin/service.py) — AdminService
  └─ self.metrics_repo = AdminMetricsRepository(db)

Repository (admin/repository.py) — AdminMetricsRepository
  └─ get_resumen()           → dict con KPIs
  └─ get_ventas_por_periodo() → list[dict] con ventas por fecha
  └─ get_productos_top()     → list[dict] con top productos
  └─ get_pedidos_por_estado() → list[dict] con distribución

Schemas (admin/schemas.py)
  └─ MetricsResumenResponse
  └─ MetricsVentasRequest / MetricsVentasItem / MetricsVentasResponse
  └─ MetricsProductoTopItem / MetricsProductoTopResponse
  └─ MetricsPedidosEstadoItem / MetricsPedidosEstadoResponse
```

## Data Flow — Resumen Endpoint

```
1. COUNT(User) WHERE soft_deleted_at IS NULL          → usuarios_registrados
2. COUNT(Pedido) WHERE soft_deleted_at IS NULL         → cantidad_pedidos
3. COALESCE(SUM(Pedido.total), 0) WHERE soft_deleted_at IS NULL → total_ventas
4. GROUP BY Pedido.estado_codigo + COUNT               → pedidos_por_estado
```

Los 4 queries se ejecutan secuencialmente dentro de una misma sesión de BD. No requieren transacción porque son lecturas independientes.

## Data Flow — Ventas por Período Endpoint

```
1. SELECT DATE(created_at), SUM(total), COUNT(id)
   FROM pedido
   WHERE soft_deleted_at IS NULL
     AND created_at BETWEEN :fecha_inicio AND :fecha_fin
   GROUP BY DATE(created_at)
   ORDER BY DATE(created_at)
2. Post-procesar en Python:
   - granularidad "day": devolver tal cual
   - granularidad "week": agrupar por ISO week (isocalendar())
   - granularidad "month": agrupar por YYYY-MM (strftime)
```

## Data Flow — Productos Top

```
SELECT dp.producto_id, dp.nombre_snapshot,
       SUM(dp.cantidad) as total_cantidad,
       SUM(dp.subtotal) as total_monto
FROM detalle_pedido dp
JOIN pedido p ON dp.pedido_id = p.id
WHERE p.soft_deleted_at IS NULL
GROUP BY dp.producto_id, dp.nombre_snapshot
ORDER BY total_cantidad DESC
LIMIT 10
```

## Risks / Trade-offs

| Risk                                                         | Mitigation                                                                                                                                                                                                                     |
| ------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Queries sin índices pueden ser lentas con muchos pedidos     | `Pedido.created_at` y `Pedido.estado_codigo` ya tienen índices. `DetallePedido.producto_id` tiene índice. Monitorear performance en producción.                                                                                |
| Date bucketing en Python para week/month consume más memoria | Para granularidad `day` se devuelve directo de SQL. Week/month solo aplican cuando se pide explícitamente. Límite de 365 días en el rango.                                                                                     |
| No hay cacheo — cada request recalcula                       | Aceptable para MVP. Si se necesita, agregar cache con TTL en change futuro.                                                                                                                                                    |
| Métricas no diferencian pedidos cancelados en revenue        | `Pedido.total` se incluye siempre que `soft_deleted_at IS NULL`. Si se necesita excluir cancelados, agregar filtro `estado_codigo != 'CANCELADO'`. Por ahora se incluyen todos los estados para reflejar la realidad completa. |

## Migration Plan

No requiere migración de base de datos. Los endpoints son de solo lectura.

**Rollback**: Eliminar los métodos del router, service, repository y schemas. Cero impacto en datos.

## Open Questions

1. ¿Las métricas deben excluir pedidos en estado CANCELADO del total de ventas? (Por ahora se incluyen todos. El dashboard puede filtrar visualmente.)
2. ¿Se necesita un endpoint de métricas para Gestor de Pedidos (rol PEDIDOS) con datos limitados a sus pedidos? (No en este change. Solo ADMIN.)
3. ¿Límite de rango de fechas para ventas por período? (Se implementa validación: máximo 365 días entre fecha_inicio y fecha_fin.)
