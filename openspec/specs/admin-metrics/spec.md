# admin-metrics Specification

## Purpose

TBD - created by archiving change implement-metrics-endpoints. Update Purpose after archive.

## Requirements

### Requirement: Resumen de KPIs generales

El sistema SHALL proveer un endpoint `GET /api/v1/admin/metricas/resumen` que retorne un resumen de indicadores clave del negocio. Solo accesible para usuarios con rol ADMIN.

**Response schema:**

```json
{
  "total_ventas": 150000.5,
  "cantidad_pedidos": 342,
  "pedidos_por_estado": {
    "PENDIENTE": 45,
    "CONFIRMADO": 120,
    "EN_PREPARACION": 80,
    "EN_CAMINO": 50,
    "ENTREGADO": 30,
    "CANCELADO": 17
  },
  "usuarios_registrados": 89
}
```

- `total_ventas`: `SUM(Pedido.total)` para todos los pedidos con `soft_deleted_at IS NULL`. `0.0` si no hay pedidos.
- `cantidad_pedidos`: `COUNT(Pedido.id)` con `soft_deleted_at IS NULL`.
- `pedidos_por_estado`: objeto con clave = `estado_codigo` y valor = conteo. Incluye todos los códigos de estado que tengan al menos un pedido.
- `usuarios_registrados`: `COUNT(User.id)` con `soft_deleted_at IS NULL`.

#### Scenario: Admin obtiene resumen con datos

- **WHEN** un usuario ADMIN hace `GET /api/v1/admin/metricas/resumen`
- **THEN** el sistema retorna 200 con total_ventas, cantidad_pedidos, pedidos_por_estado y usuarios_registrados
- **AND** todos los campos contienen valores calculados desde la BD

#### Scenario: Admin obtiene resumen con BD vacía

- **WHEN** un usuario ADMIN hace `GET /api/v1/admin/metricas/resumen` y no hay pedidos ni usuarios
- **THEN** el sistema retorna 200 con `total_ventas: 0.0`, `cantidad_pedidos: 0`, `pedidos_por_estado: {}`, `usuarios_registrados: 0`

#### Scenario: Usuario sin rol ADMIN recibe 403

- **WHEN** un usuario con rol CLIENT, STOCK o PEDIDOS hace `GET /api/v1/admin/metricas/resumen`
- **THEN** el sistema retorna HTTP 403 Forbidden

#### Scenario: Usuario no autenticado recibe 401

- **WHEN** un usuario sin token hace `GET /api/v1/admin/metricas/resumen`
- **THEN** el sistema retorna HTTP 401 Unauthorized

---

### Requirement: Ventas por período con granularidad configurable

El sistema SHALL proveer un endpoint `GET /api/v1/admin/metricas/ventas` que retorne ventas agregadas por período. El período se define mediante `fecha_inicio`, `fecha_fin` y `granularidad`. Solo accesible para usuarios con rol ADMIN.

**Query parameters:**

- `fecha_inicio` (required, ISO date): fecha de inicio del rango (inclusive)
- `fecha_fin` (required, ISO date): fecha de fin del rango (inclusive)
- `granularidad` (required, enum): `"day"`, `"week"` o `"month"`

**Validaciones:**

- `fecha_inicio` debe ser anterior a `fecha_fin`
- El rango entre `fecha_inicio` y `fecha_fin` no puede exceder 365 días
- `granularidad` debe ser uno de: `"day"`, `"week"`, `"month"`

**Response schema:**

```json
{
  "items": [
    {
      "fecha": "2026-06-01",
      "monto_total": 12500.0,
      "cantidad_pedidos": 15
    }
  ]
}
```

- `fecha`: string en formato ISO date (`YYYY-MM-DD`) para day, `YYYY-Www` para week, `YYYY-MM` para month.
- `monto_total`: `SUM(Pedido.total)` para el período.
- `cantidad_pedidos`: `COUNT(Pedido.id)` para el período.
- Solo se incluyen pedidos con `soft_deleted_at IS NULL`.
- Los períodos sin pedidos NO se incluyen en la respuesta (no se rellenan ceros).
- Ordenado por fecha ascendente.

#### Scenario: Admin consulta ventas diarias de una semana

- **WHEN** un usuario ADMIN hace `GET /api/v1/admin/metricas/ventas?fecha_inicio=2026-06-01&fecha_fin=2026-06-07&granularidad=day`
- **THEN** el sistema retorna 200 con array de items, uno por cada día con pedidos
- **AND** cada item tiene fecha en formato `YYYY-MM-DD`, monto_total y cantidad_pedidos

#### Scenario: Admin consulta ventas semanales de un trimestre

- **WHEN** un usuario ADMIN hace `GET /api/v1/admin/metricas/ventas?fecha_inicio=2026-01-01&fecha_fin=2026-03-31&granularidad=week`
- **THEN** el sistema retorna 200 con array de items agrupados por semana ISO
- **AND** cada item tiene fecha en formato `YYYY-Www`

#### Scenario: Admin consulta ventas mensuales de un año

- **WHEN** un usuario ADMIN hace `GET /api/v1/admin/metricas/ventas?fecha_inicio=2026-01-01&fecha_fin=2026-12-31&granularidad=month`
- **THEN** el sistema retorna 200 con array de items agrupados por mes
- **AND** cada item tiene fecha en formato `YYYY-MM`

#### Scenario: Rango de fechas inválido (inicio > fin)

- **WHEN** un usuario ADMIN hace `GET /api/v1/admin/metricas/ventas?fecha_inicio=2026-06-15&fecha_fin=2026-06-01&granularidad=day`
- **THEN** el sistema retorna HTTP 422 Unprocessable Entity con mensaje descriptivo

#### Scenario: Rango excede 365 días

- **WHEN** un usuario ADMIN hace `GET /api/v1/admin/metricas/ventas?fecha_inicio=2025-01-01&fecha_fin=2026-12-31&granularidad=month`
- **THEN** el sistema retorna HTTP 422 Unprocessable Entity con mensaje descriptivo

#### Scenario: Granularidad inválida

- **WHEN** un usuario ADMIN hace `GET /api/v1/admin/metricas/ventas?fecha_inicio=2026-06-01&fecha_fin=2026-06-07&granularidad=hour`
- **THEN** el sistema retorna HTTP 422 Unprocessable Entity con mensaje descriptivo

#### Scenario: Período sin pedidos

- **WHEN** un usuario ADMIN consulta un rango de fechas sin pedidos
- **THEN** el sistema retorna 200 con `items: []`

---

### Requirement: Top 10 productos más vendidos

El sistema SHALL proveer un endpoint `GET /api/v1/admin/metricas/productos-top` que retorne los 10 productos más vendidos, ordenados por cantidad total vendida descendente. Solo accesible para usuarios con rol ADMIN.

**Response schema:**

```json
{
  "items": [
    {
      "producto_id": "550e8400-e29b-41d4-a716-446655440000",
      "nombre": "Pizza Margherita",
      "cantidad_vendida": 85,
      "monto_total": 42500.0
    }
  ]
}
```

- `producto_id`: UUID del producto.
- `nombre`: `nombre_snapshot` de `DetallePedido` (el nombre al momento del pedido).
- `cantidad_vendida`: `SUM(DetallePedido.cantidad)`.
- `monto_total`: `SUM(DetallePedido.subtotal)`.
- Se joinea con `Pedido` para filtrar `pedido.soft_deleted_at IS NULL`.
- Máximo 10 resultados.

#### Scenario: Admin obtiene top 10 productos

- **WHEN** un usuario ADMIN hace `GET /api/v1/admin/metricas/productos-top`
- **THEN** el sistema retorna 200 con hasta 10 items ordenados por cantidad_vendida descendente
- **AND** cada item contiene producto_id, nombre, cantidad_vendida, monto_total

#### Scenario: Menos de 10 productos en el sistema

- **WHEN** hay solo 3 productos con ventas registradas
- **THEN** el sistema retorna 3 items

#### Scenario: Sin ventas registradas

- **WHEN** no hay ningún detalle de pedido
- **THEN** el sistema retorna 200 con `items: []`

---

### Requirement: Distribución de pedidos por estado con porcentajes

El sistema SHALL proveer un endpoint `GET /api/v1/admin/metricas/pedidos-por-estado` que retorne la distribución actual de pedidos por estado, incluyendo conteo y porcentaje. Solo accesible para usuarios con rol ADMIN.

**Response schema:**

```json
{
  "items": [
    {
      "estado": "PENDIENTE",
      "cantidad": 45,
      "porcentaje": 13.16
    }
  ]
}
```

- `estado`: `estado_codigo` del pedido.
- `cantidad`: `COUNT(Pedido.id)` para ese estado.
- `porcentaje`: `(cantidad / total_pedidos) * 100`, redondeado a 2 decimales.
- Solo se incluyen pedidos con `soft_deleted_at IS NULL`.
- Se incluyen todos los estados que tengan al menos un pedido.
- La suma de todos los porcentajes debe ser 100% (o cercano por redondeo).

#### Scenario: Admin obtiene distribución de pedidos

- **WHEN** un usuario ADMIN hace `GET /api/v1/admin/metricas/pedidos-por-estado`
- **THEN** el sistema retorna 200 con array de items, cada uno con estado, cantidad y porcentaje
- **AND** los porcentajes suman aproximadamente 100%

#### Scenario: Sin pedidos

- **WHEN** no hay pedidos en la BD
- **THEN** el sistema retorna 200 con `items: []`

#### Scenario: Todos los pedidos en un mismo estado

- **WHEN** todos los pedidos están en estado PENDIENTE
- **THEN** el sistema retorna 1 item con `porcentaje: 100.0`

---

### Requirement: Filtrado de registros soft-deleted en métricas

El sistema SHALL excluir de todas las métricas los pedidos con `soft_deleted_at IS NOT NULL` y los usuarios con `soft_deleted_at IS NOT NULL`. Los pedidos administrativamente eliminados no deben contaminar los KPIs.

#### Scenario: Pedido soft-deleted no afecta métricas

- **WHEN** existe un pedido con `soft_deleted_at` no nulo
- **THEN** ese pedido no se cuenta en `cantidad_pedidos`, `total_ventas`, `pedidos_por_estado`, `ventas` ni `productos-top`

#### Scenario: Usuario soft-deleted no se cuenta

- **WHEN** existe un usuario con `soft_deleted_at` no nulo
- **THEN** ese usuario no se cuenta en `usuarios_registrados`
