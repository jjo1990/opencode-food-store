# Change 38: Admin Order Management — Design Document

## Executive Summary

Extend the admin module with 3 specialized endpoints for order lifecycle management. The design leverages the existing FSM (Finite State Machine) for order state transitions and reuses audit trail infrastructure. All endpoints require ADMIN or PEDIDOS role.

---

## Context

### What Exists Today

1. **FSM Implementation** — `backend/app/pedidos/service.py` (lines 24–43)
   - `TRANSITIONS` dict: defines valid state changes per role
   - `TERMINAL_STATES` set: {ENTREGADO, CANCELADO}
   - 6 order states: PENDIENTE → CONFIRMADO → EN_PREPARACION → EN_CAMINO → ENTREGADO or CANCELADO

2. **Order Models**
   - `Pedido`: order aggregate (id, usuario_id, estado_codigo, total, created_at, etc.)
   - `DetallePedido`: line items (producto_id, cantidad, precio_snapshot, etc.)
   - `HistorialEstadoPedido`: audit trail (estado_desde, estado_nuevo, actor_id, motivo, created_at)

3. **Admin Module Patterns**
   - Router: `require_role("ADMIN")` dependency for authorization
   - Service: stateless business logic with validation
   - Repository: query building + pagination
   - Schemas: Pydantic models with `from_attributes = True` for ORM mapping

4. **Pagination Standard** — Admin usuarios endpoint uses page/size pattern (default size=20, max=100)

---

## Goals

### Primary Goals

1. **List Orders** → Enable admins to query all orders with:
   - Pagination (page, size with sensible defaults)
   - Filtering: estado_codigo, fecha_inicio/fin, usuario_id, monto_min/max
   - Join usuario table to show client names
   - Sorted by created_at descending

2. **Change Order State** → Transition orders through FSM with:
   - Validation via existing TRANSITIONS dict
   - Motivo (reason) as optional audit trail entry
   - Returns updated order snapshot

3. **Get Order Detail** → Full order context:
   - All line items
   - Complete state history with actor names (joined from User table)
   - Timeline of who did what and when

### Secondary Goals

- Maintain consistency with existing admin/usuarios patterns
- Follow RBAC: both ADMIN and PEDIDOS roles authorized
- Minimal code duplication (reuse FSM, repo patterns)
- Transparent audit trail for compliance

---

## Non-Goals

- Order creation by admin (clients only)
- Bulk operations (batch state changes)
- Email/SMS notifications
- Payment refunds (pagos module responsibility)
- Soft-delete orders
- Frontend implementation
- Webhooks or external event publishing

---

## Decisions

### Decision 1: Reuse Existing FSM for State Transitions

**Context**: Order FSM is fully implemented in `pedidos/service.py::TRANSITIONS` dict.

**Decision**: Do NOT create separate validation logic in admin module. Call existing FSM via service layer.

**Rationale**:
- Centralized state machine = single source of truth
- Prevents divergence between client and admin transitions
- Reduces maintenance burden

**Consequence**: Admin transitions obey the same rules as client transitions (role + destination validation).

---

### Decision 2: Join Usuario Table for Client Names in List

**Context**: The list endpoint must show who owns each order.

**Decision**: LEFT OUTER JOIN usuario table in repository query. Include `cliente_nombre` in response.

**Rationale**:
- Avoids N+1 queries (one multi-table query vs. loop + individual queries)
- Admins want readable client names, not UUIDs
- Follows existing pattern in pedidos service (lines 376–382)

**Implementation**:
```python
# In admin/repository.py::list_orders_admin
query = self.db.query(Pedido, User.full_name).outerjoin(
    User, Pedido.usuario_id == User.id
).filter(...)  # filters applied
```

---

### Decision 3: Pagination Defaults

**Context**: Admin usuarios uses page/size with defaults.

**Decision**: Adopt same pattern for orders:
- page: int ≥ 1, default 1
- size: int ≥ 1, max 100, default 20

**Rationale**:
- Consistency across admin module
- 20 items = ~1 screen on web/mobile
- Max 100 prevents memory/DB abuse

---

### Decision 4: Date Filters are Optional

**Context**: Admins may want orders from a date range (e.g., last 7 days, last month).

**Decision**: fecha_inicio and fecha_fin are optional query params. If provided, filter orders WHERE created_at BETWEEN fecha_inicio AND fecha_fin.

**Rationale**:
- Flexibility: admins can view all orders (no date filter) or specific range
- Separate from state/user/amount filters (compose multiple)
- Matches user expectations from reporting systems

**Implementation**:
```python
if fecha_inicio:
    query = query.filter(Pedido.created_at >= fecha_inicio)
if fecha_fin:
    query = query.filter(Pedido.created_at <= fecha_fin)
```

---

### Decision 5: Use Motivo Field for Audit Trail

**Context**: State changes should be auditable — why did an admin cancel an order?

**Decision**: Accept optional `motivo` string (max 500 chars) in PATCH request. Store in HistorialEstadoPedido.

**Rationale**:
- HistorialEstadoPedido model already has motivo field
- Complies with audit requirements
- Matches existing schema (AvanzarEstadoRequest in pedidos/schemas.py)

---

### Decision 6: Response Types

**Context**: Multiple endpoint responses needed.

**Decision**:
1. **GET /admin/pedidos** → `AdminOrderListResponse` (paginated list with summary items)
2. **PATCH /admin/pedidos/{id}/estado** → `PedidoRead` (simple order snapshot)
3. **GET /admin/pedidos/{id}** → `PedidoDetail` (full order with items + history)

**Rationale**:
- Reuse existing `PedidoRead` and `PedidoDetail` schemas (no duplication)
- Create new `AdminOrderListResponse` with `AdminOrderListItem` for list endpoint
- Minimizes schema bloat

---

## New Structures

### Schema 1: AdminOrderListItem

```python
# backend/app/admin/schemas.py

class AdminOrderListItem(BaseModel):
    """Single order in admin list view"""
    id: UUID
    cliente_nombre: str | None  # Joined from user.full_name; None if user deleted
    usuario_id: UUID
    estado_codigo: str
    total: Decimal
    created_at: datetime
    direccion_calle: str | None  # From direccion_snapshot JSON or null
    
    class Config:
        from_attributes = True
```

### Schema 2: AdminOrderListResponse

```python
# backend/app/admin/schemas.py

class AdminOrderListResponse(BaseModel):
    """Paginated list of orders for admin"""
    items: list[AdminOrderListItem]
    total: int
    page: int
    size: int
    pages: int
```

### Schema 3: AdminChangeStateRequest

```python
# backend/app/admin/schemas.py

class AdminChangeStateRequest(BaseModel):
    """Request to change order state"""
    nuevo_estado: str = Field(..., min_length=1, max_length=20)
    motivo: str | None = Field(None, max_length=500)
```

---

## Endpoint Flow (ASCII Diagram)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     ADMIN ORDER MANAGEMENT FLOW                          │
└─────────────────────────────────────────────────────────────────────────┘

1. LIST ORDERS
   ┌──────────────────────────────────────────────────────┐
   │ GET /api/v1/admin/pedidos?page=1&size=20&estado=EN  │
   │ + Requires: ADMIN or PEDIDOS role                    │
   └──────────────────────────────────────────────────────┘
                            ↓
   ┌──────────────────────────────────────────────────────┐
   │ AdminService.list_orders_admin()                      │
   │  → AdminRepository.list_orders_admin()               │
   │     • Join User table for client names               │
   │     • Apply filters: estado, fecha, usuario, monto   │
   │     • Pagination: offset=(page-1)*size              │
   └──────────────────────────────────────────────────────┘
                            ↓
   ┌──────────────────────────────────────────────────────┐
   │ Response: AdminOrderListResponse                      │
   │ {                                                      │
   │   items: [                                            │
   │     {id, cliente_nombre, total, estado_codigo, ...}  │
   │   ],                                                  │
   │   total: 347,  page: 1,  size: 20,  pages: 18       │
   │ }                                                      │
   └──────────────────────────────────────────────────────┘


2. CHANGE ORDER STATE
   ┌──────────────────────────────────────────────────────┐
   │ PATCH /api/v1/admin/pedidos/{id}/estado              │
   │ Body: { nuevo_estado: "EN_PREPARACION", motivo: "..." }
   │ + Requires: ADMIN or PEDIDOS role                    │
   └──────────────────────────────────────────────────────┘
                            ↓
   ┌──────────────────────────────────────────────────────┐
   │ AdminService.change_order_state_admin()              │
   │  → Fetch pedido by id                                │
   │  → Validate transition via FSM (TRANSITIONS)         │
   │  → Check actor role against allowed_roles            │
   │  → Update pedido.estado_codigo                       │
   │  → Create HistorialEstadoPedido (audit entry)        │
   │  → Commit transaction                                │
   └──────────────────────────────────────────────────────┘
                            ↓
   ┌──────────────────────────────────────────────────────┐
   │ Response: PedidoRead                                  │
   │ {id, estado_codigo, total, created_at, ...}          │
   └──────────────────────────────────────────────────────┘


3. GET ORDER DETAIL
   ┌──────────────────────────────────────────────────────┐
   │ GET /api/v1/admin/pedidos/{id}                        │
   │ + Requires: ADMIN or PEDIDOS role                    │
   └──────────────────────────────────────────────────────┘
                            ↓
   ┌──────────────────────────────────────────────────────┐
   │ AdminService.get_order_detail_admin()                │
   │  → Fetch pedido with detalles + historial           │
   │  → Join User table to historial for actor names      │
   │  → Build PedidoDetail response                       │
   └──────────────────────────────────────────────────────┘
                            ↓
   ┌──────────────────────────────────────────────────────┐
   │ Response: PedidoDetail                                │
   │ {                                                      │
   │   id, estado_codigo, total, created_at,              │
   │   items: [{...}, ...],                               │
   │   historial: [{estado_desde, estado_nuevo,           │
   │               actor_nombre, motivo, created_at}]     │
   │ }                                                      │
   └──────────────────────────────────────────────────────┘
```

---

## Dependencies

### External (No New Requirements)
- FastAPI ✓ (already in use)
- SQLAlchemy ORM ✓ (already in use)
- Pydantic ✓ (already in use)

### Internal
- `app.models.pedido.Pedido`
- `app.models.detalle_pedido.DetallePedido`
- `app.models.historial_estado_pedido.HistorialEstadoPedido`
- `app.models.user.User`
- `app.pedidos.service.PedidoService` (FSM: TRANSITIONS, TERMINAL_STATES)
- `app.core.dependencies.require_role()`
- `app.core.database.get_db()`

### Files to Modify
1. `backend/app/admin/schemas.py` — Add 3 schemas
2. `backend/app/admin/repository.py` — Add list_orders_admin + count_orders_admin methods
3. `backend/app/admin/service.py` — Add list_orders_admin + change_order_state_admin methods
4. `backend/app/admin/router.py` — Add 3 endpoints

---

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| Invalid state transitions | Reuse existing FSM validation; no new logic |
| Unauthorized access | `require_role(["ADMIN", "PEDIDOS"])` on all 3 endpoints |
| Performance on large datasets | Pagination with size limit (max 100); indexed queries on estado_codigo, created_at |
| Audit trail corruption | Create HistorialEstadoPedido in transaction; rollback on error |
| N+1 queries | Use JOINs in repository; selectinload for nested relations |
