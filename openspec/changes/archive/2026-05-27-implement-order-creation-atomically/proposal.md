## Why

Sin la creación de pedidos, el sistema es solo un catálogo con carrito. El cliente puede explorar productos y agregarlos al carrito, pero no puede concretar una compra. Este change implementa el primer endpoint transaccional del sistema — `POST /api/v1/pedidos` — que convierte el carrito en un pedido real con snapshots inmutables, cálculos de totales y registro de trazabilidad inicial. Es el habilitador de todo lo que sigue: pagos, FSM, dashboard.

## What Changes

- **Nuevas tablas en BD**: `estado_pedido` (catálogo), `forma_pago` (catálogo), `pedido`, `detalle_pedido`, `historial_estado_pedido`
- **Nuevo módulo backend `pedidos/`**: model, schemas, repository, service, router
- **Nuevo endpoint**: `POST /api/v1/pedidos` — creación atómica de pedidos con Unit of Work (transaccional)
- **Seed data**: registro de 6 estados (`PENDIENTE`, `CONFIRMADO`, `EN_PREPARACIÓN`, `EN_CAMINO`, `ENTREGADO`, `CANCELADO`) y 3 formas de pago (`MERCADOPAGO`, `EFECTIVO`, `TRANSFERENCIA`)
- **Migración Alembic**: nueva revisión con todas las tablas del Dominio 3 (Ventas, Pagos y Trazabilidad)

## Capabilities

### New Capabilities

- `order-creation`: Creación atómica de pedidos con validación de stock, snapshots de precio/nombre/dirección, cálculo de totales y registro de historial inicial. Transacción vía Unit of Work con commit/rollback.

### Modified Capabilities

- _(ninguna — primera vez que se toca el dominio de pedidos)_

## Impact

- **Backend**: nuevo módulo `backend/app/pedidos/` con 6 archivos (model, schemas, repository, service, router, **init**)
- **Base de datos**: 5 nuevas tablas + migración Alembic + seed data
- **Modelos**: nuevos modelos SQLAlchemy en `backend/app/models/` (pedido, detalle_pedido, historial_estado_pedido, estado_pedido, forma_pago)
- **main.py**: registro del nuevo router `pedidos_router` con prefijo `/api/v1`
- **Dependencias**: requiere módulos `productos` (validación stock), `direcciones` (snapshot dirección), y `core/` (UoW, dependencias auth)
