# Change 38: Implement Admin Order Management

## What

Add 3 new admin-exclusive endpoints to enable comprehensive order management: list all orders with advanced filtering & pagination, change order state through the FSM, and retrieve detailed order information with full audit trail.

## Why

Admins and order managers (rol PEDIDOS) need visibility and control over all customer orders. Currently, they can only see their own orders. This change provides:
- **Visibility**: List all orders across the platform with filters (state, date, customer, amount)
- **Control**: Transition orders through valid FSM states with optional notes and audit trail
- **Accountability**: Full audit trail showing who changed what and when

## Scope

### New Endpoints

1. **`GET /api/v1/admin/pedidos`** — List all orders with pagination + filtering
   - Query parameters: page, size, estado_codigo, fecha_inicio, fecha_fin, usuario_id, monto_min, monto_max
   - Response: Paginated list with client name, total, state, timestamps
   - RBAC: ADMIN or PEDIDOS role required

2. **`PATCH /api/v1/admin/pedidos/{id}/estado`** — Change order state
   - Request body: nuevo_estado, motivo (optional)
   - Validates transition via existing FSM (TRANSITIONS map)
   - Creates audit trail entry (HistorialEstadoPedido)
   - RBAC: ADMIN or PEDIDOS role required

3. **`GET /api/v1/admin/pedidos/{id}`** — Get order detail with audit trail
   - Returns: Full order data + all line items + complete state change history with actor names
   - RBAC: ADMIN or PEDIDOS role required

### Modified Modules

- **backend/app/admin/schemas.py** — Add 3 new Pydantic schemas
- **backend/app/admin/repository.py** — Add list_orders_admin with joins & filters
- **backend/app/admin/service.py** — Add list_orders_admin & change_order_state_admin methods
- **backend/app/admin/router.py** — Add 3 new endpoints

### Reused Components

- FSM (TRANSITIONS, TERMINAL_STATES) from `backend/app/pedidos/service.py`
- Order models (Pedido, DetallePedido, HistorialEstadoPedido) — no changes needed
- Audit trail creation — already exists in PedidoRepository

## Non-Goals

- **Email/SMS notifications** — No state change notifications (future feature)
- **Frontend UI** — Only backend endpoints; frontend team implements separately
- **Webhooks** — No external event triggers
- **Order cancellation refunds** — State transitions only; payment refunds handled by pagos module
- **Bulk state changes** — Single-order transitions only (no batch operations)
- **Order creation** — Admin cannot create orders (clients only); admin can manage existing
- **Soft-delete orders** — Order deletion logic out of scope; currently no delete endpoint
