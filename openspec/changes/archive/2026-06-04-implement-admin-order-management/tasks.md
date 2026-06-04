## 1. Create New Schemas

**File**: `backend/app/admin/schemas.py`

**Description**: Add 3 new Pydantic models for admin order operations.

**Details**:
- [ ] Create `AdminOrderListItem` schema with fields: id, cliente_nombre, usuario_id, estado_codigo, total, created_at, direccion_calle
- [ ] Create `AdminOrderListResponse` schema with pagination: items, total, page, size, pages
- [ ] Create `AdminChangeStateRequest` schema with: nuevo_estado (required), motivo (optional)
- [ ] Ensure all use `from_attributes = True` for ORM compatibility
- [ ] Add proper validation: nuevo_estado (1–20 chars), motivo (max 500 chars)

**Acceptance Criteria**:
- All 3 schemas are importable from `app.admin.schemas`
- Pydantic validation works (test with invalid motivo length, missing nuevo_estado)
- Schemas can be serialized/deserialized to/from JSON

---

## 2. Extend Admin Repository

**File**: `backend/app/admin/repository.py`

**Description**: Add repository methods to query orders with filtering, pagination, and client name joins.

**Details**:
- [ ] Add `list_orders_admin()` method:
  - Parameters: page, size, estado_codigo, fecha_inicio, fecha_fin, usuario_id, monto_min, monto_max
  - Joins User table on usuario_id for `cliente_nombre`
  - Applies all filters (estado, date range, user, amount)
  - Filters out soft-deleted orders (`soft_deleted_at IS NULL`)
  - Orders by `created_at DESC`
  - Handles pagination: offset, limit
  - Returns: tuple of (list[Pedido + cliente_name], total_count)

- [ ] Add `count_orders_admin()` method (optional, for consistency):
  - Same filters as list_orders_admin
  - Returns: int (total matching count)

**Acceptance Criteria**:
- Method returns tuples of (Pedido, cliente_name)
- Filters are applied correctly (test each filter: estado, date, user, amount)
- Pagination works (offset/limit produce correct ranges)
- Soft-deleted orders are excluded
- No N+1 queries (single multi-table query)

---

## 3. Extend Admin Service

**File**: `backend/app/admin/service.py`

**Description**: Add service methods for order listing and state transitions with FSM validation.

**Details**:
- [ ] Add `list_orders_admin()` method:
  - Calls `AdminRepository.list_orders_admin()` with all filter parameters
  - Builds `AdminOrderListResponse` with:
    - items: list of `AdminOrderListItem` (map Pedido + cliente_name)
    - total, page, size, pages (pagination metadata)
  - Handles error cases (invalid page/size)

- [ ] Add `change_order_state_admin()` method:
  - Parameters: order_id, new_estado, motivo, current_user
  - Fetch order: `PedidoRepository.get_by_id(order_id)`
  - Validate order exists and not soft-deleted (raise 404 if missing)
  - Import FSM from `pedidos.service`: TRANSITIONS, TERMINAL_STATES
  - Validate transition:
    - Check order not in TERMINAL_STATES (raise 422 if terminal)
    - Check nuevo_estado in TRANSITIONS[current_estado] (raise 422 if invalid)
    - Check user role in transition["roles"] (raise 403 if unauthorized)
  - Update `pedido.estado_codigo = nuevo_estado`
  - If `transition["stock_action"] == "restore"`: restore stock for all items
    - Query each Producto with row-level lock `.with_for_update()`
    - Increment stock: `producto.stock_cantidad += detalle.cantidad`
  - Create audit entry via `PedidoRepository.create_historial()`
  - Commit transaction; rollback on exception
  - Return updated order as `PedidoRead`

**Acceptance Criteria**:
- Invalid transitions are rejected (422)
- Unauthorized users get 403
- Non-existent orders return 404
- Audit trail is created correctly
- Stock is restored when needed
- Transaction rolls back on error

---

## 4. Extend Admin Router

**File**: `backend/app/admin/router.py`

**Description**: Add 3 new endpoints with RBAC and proper HTTP semantics.

**Details**:
- [ ] Add `GET /admin/pedidos` endpoint:
  - Query params: page (default 1), size (default 20, max 100), estado_codigo, fecha_inicio, fecha_fin, usuario_id, monto_min, monto_max
  - Dependency: `require_role(["ADMIN", "PEDIDOS"])`
  - Calls `AdminService.list_orders_admin()`
  - Returns: `AdminOrderListResponse`
  - HTTP 200 on success, 403 on unauthorized, 422 on invalid params

- [ ] Add `PATCH /admin/pedidos/{id}/estado` endpoint:
  - Path param: id (UUID)
  - Body: `AdminChangeStateRequest`
  - Dependency: `require_role(["ADMIN", "PEDIDOS"])`
  - Calls `AdminService.change_order_state_admin()`
  - Returns: `PedidoRead`
  - HTTP 200 on success, 400 on bad request, 403 on unauthorized, 404 on not found, 422 on invalid transition

- [ ] Add `GET /admin/pedidos/{id}` endpoint:
  - Path param: id (UUID)
  - Dependency: `require_role(["ADMIN", "PEDIDOS"])`
  - Calls existing `PedidoRepository.get_by_id()` or add `get_order_detail_admin()` in service
  - Returns: `PedidoDetail` with full audit trail and client info
  - HTTP 200 on success, 403 on unauthorized, 404 on not found

**Acceptance Criteria**:
- All 3 endpoints are accessible at correct routes
- RBAC is enforced (401 for no token, 403 for wrong role)
- Query/path params are validated by FastAPI
- Responses match schemas (Pydantic validation)
- Error responses include appropriate status codes and messages

---

## 5. Write Repository Tests

**File**: `backend/tests/test_admin_orders_repository.py` (new file)

**Description**: Unit tests for repository layer — filtering, pagination, joins.

**Test Cases**:
- [ ] `test_list_orders_empty` — No orders in DB, returns empty list
- [ ] `test_list_orders_with_pagination` — Correct offset/limit applied
- [ ] `test_list_orders_filter_by_estado` — Filters by estado_codigo correctly
- [ ] `test_list_orders_filter_by_user` — Filters by usuario_id correctly
- [ ] `test_list_orders_filter_by_date_range` — Filters by fecha_inicio/fin correctly
- [ ] `test_list_orders_filter_by_amount_range` — Filters by monto_min/max correctly
- [ ] `test_list_orders_joins_user_name` — Returns cliente_nombre from joined User table
- [ ] `test_list_orders_excludes_soft_deleted` — Soft-deleted orders are excluded
- [ ] `test_list_orders_combined_filters` — Multiple filters compose correctly (AND logic)
- [ ] `test_count_orders_matches_list` — count matches list length

**Acceptance Criteria**:
- All tests pass
- Each filter behavior is verified
- Soft-delete logic is correct
- Join produces non-null cliente_name for valid users, NULL for deleted users

---

## 6. Write Service Tests

**File**: `backend/tests/test_admin_orders_service.py` (new file)

**Description**: Unit tests for service layer — FSM validation, authorization, audit trail.

**Test Cases**:
- [ ] `test_list_orders_admin_returns_paginated_response` — Response schema is correct
- [ ] `test_change_order_state_admin_valid_transition` — Valid transition succeeds
- [ ] `test_change_order_state_admin_invalid_transition` — Invalid transition raises 422
- [ ] `test_change_order_state_admin_unauthorized_role` — Wrong role raises 403
- [ ] `test_change_order_state_admin_terminal_state_rejected` — Can't transition from ENTREGADO
- [ ] `test_change_order_state_admin_order_not_found` — Missing order raises 404
- [ ] `test_change_order_state_admin_creates_audit_entry` — HistorialEstadoPedido is created
- [ ] `test_change_order_state_admin_restores_stock_on_cancel` — Stock incremented when transition has "restore"
- [ ] `test_change_order_state_admin_transaction_rollback_on_error` — DB rolled back if exception

**Acceptance Criteria**:
- FSM validation works (use TRANSITIONS from pedidos.service)
- Role checks pass/fail correctly
- Audit entries are created with correct fields (actor_id, motivo)
- Stock restoration logic is triggered when needed
- Transactions roll back on error

---

## 7. Write Integration Tests

**File**: `backend/tests/test_admin_orders_endpoints.py` (new file)

**Description**: End-to-end tests for HTTP endpoints — auth, request/response, error codes.

**Test Cases**:
- [ ] `test_get_admin_pedidos_no_auth` — 401 without token
- [ ] `test_get_admin_pedidos_wrong_role` — 403 for CLIENT role
- [ ] `test_get_admin_pedidos_valid` — 200 with ADMIN role, returns AdminOrderListResponse
- [ ] `test_get_admin_pedidos_filters_work` — Query params filter correctly
- [ ] `test_patch_admin_pedidos_estado_no_auth` — 401 without token
- [ ] `test_patch_admin_pedidos_estado_wrong_role` — 403 for CLIENT role
- [ ] `test_patch_admin_pedidos_estado_valid` — 200 with ADMIN role, returns updated PedidoRead
- [ ] `test_patch_admin_pedidos_estado_invalid_transition` — 422 for invalid transition
- [ ] `test_patch_admin_pedidos_estado_not_found` — 404 for missing order
- [ ] `test_get_admin_pedidos_id_no_auth` — 401 without token
- [ ] `test_get_admin_pedidos_id_wrong_role` — 403 for CLIENT role
- [ ] `test_get_admin_pedidos_id_valid` — 200 with ADMIN role, returns PedidoDetail with historial
- [ ] `test_get_admin_pedidos_id_not_found` — 404 for missing order

**Acceptance Criteria**:
- All HTTP status codes are correct
- RBAC is enforced on all endpoints
- Request bodies are validated (bad JSON, missing fields)
- Responses match schemas

---

## 8. Update Admin Module Documentation

**File**: `backend/app/admin/README.md` or update comments in router.py

**Description**: Document the 3 new endpoints for other developers.

**Content**:
- [ ] Add section: "Order Management Endpoints" with:
  - Brief description of each endpoint
  - Role requirements
  - Example requests/responses
  - Link to full spec: `../../openspec/changes/implement-admin-order-management/specs/admin-orders-crud.md`

**Acceptance Criteria**:
- Documentation is clear and accurate
- Examples are runnable

---

## 9. Verify FSM Compatibility

**File**: No new files; verification task

**Description**: Ensure new admin transitions respect existing FSM rules and stock logic.

**Checklist**:
- [ ] Review `pedidos/service.py::TRANSITIONS` to confirm all valid transitions are understood
- [ ] Test that ADMIN+PEDIDOS can perform all allowed transitions (e.g., CONFIRMADO→EN_PREPARACION)
- [ ] Test that CLIENT role is NOT in ADMIN transition list (e.g., CONFIRMADO→EN_PREPARACION)
- [ ] Test that stock restoration ("restore" action) works for CANCELADO transitions
- [ ] Test that terminal states (ENTREGADO, CANCELADO) cannot be transitioned from

**Acceptance Criteria**:
- No new FSM logic is introduced (reuse existing)
- All edge cases are tested
- Behavior matches pedidos.service implementation

---

## 10. Manual Testing Checklist

**Description**: Smoke tests before merge.

**Checklist**:
- [ ] Start backend server locally
- [ ] List all orders: `GET /api/v1/admin/pedidos` — returns 200 with AdminOrderListResponse
- [ ] Filter by estado: `GET /api/v1/admin/pedidos?estado_codigo=PENDIENTE` — returns only PENDIENTE orders
- [ ] Paginate: `GET /api/v1/admin/pedidos?page=2&size=10` — returns correct page
- [ ] Change state: `PATCH /api/v1/admin/pedidos/{valid_id}/estado` with valid transition — returns 200, HistorialEstadoPedido created
- [ ] Invalid transition: `PATCH /api/v1/admin/pedidos/{valid_id}/estado` with invalid transition — returns 422
- [ ] Get detail: `GET /api/v1/admin/pedidos/{valid_id}` — returns 200 with PedidoDetail, historial with actor names
- [ ] Missing order: `GET /api/v1/admin/pedidos/{invalid_id}` — returns 404
- [ ] Unauthorized: All 3 endpoints without JWT or with CLIENT role — return 401/403

**Acceptance Criteria**:
- All endpoints work as specified
- Error handling is correct
- Performance is acceptable (no N+1 queries)

---

## 11. Update Spec Compliance Document

**File**: `docs/CHANGES.md` (after all tasks complete)

**Description**: Once this change is archived in OPSX, update the human-readable change log.

**Checklist**:
- [ ] Find this change in `docs/CHANGES.md` under the active section
- [ ] Move row to "Ya realizado (archivado en OPSX)" section
- [ ] Update "Estado" to "✅ Hecho (archivado YYYY-MM-DD)"
- [ ] Update "Evidencia" to point to archived change folder
- [ ] Update "Última actualización" field

**Acceptance Criteria**:
- docs/CHANGES.md is in sync with OPSX archive

---

## Dependencies Between Tasks

```
Task 1 (Schemas)
    ↓
Task 2 (Repository)
    ↓
Task 3 (Service) ← Requires Task 1 & 2
    ↓
Task 4 (Router) ← Requires Task 1, 2, 3
    ↓
Task 5 (Repo Tests)
Task 6 (Service Tests)
Task 7 (Integration Tests) ← Requires Task 4
    ↓
Task 9 (FSM Verification) ← Runs in parallel with Task 8
Task 8 (Documentation)
    ↓
Task 10 (Manual Testing)
    ↓
Task 11 (Update CHANGES.md)
```

---

## Definition of Done

- [ ] All 11 tasks complete
- [ ] All tests passing (unit + integration)
- [ ] Code follows existing patterns (router → service → repo)
- [ ] No breaking changes to existing endpoints
- [ ] FSM logic reused, not duplicated
- [ ] Audit trail created on every state change
- [ ] RBAC enforced (ADMIN or PEDIDOS required)
- [ ] Documentation updated
- [ ] Change archived in OPSX and docs/CHANGES.md synced
