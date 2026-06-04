# Change 38: Admin Order Management — Technical Specifications

## Endpoint 1: List All Orders (Admin)

### Route
```
GET /api/v1/admin/pedidos
```

### Authentication & Authorization
- **Required**: JWT token in Authorization header
- **Role**: ADMIN or PEDIDOS

### Query Parameters

| Name | Type | Default | Max | Description |
|------|------|---------|-----|-------------|
| page | int | 1 | — | Page number (1-indexed); ≥ 1 |
| size | int | 20 | 100 | Items per page; 1–100 |
| estado_codigo | str | (none) | — | Filter by order state (e.g., "PENDIENTE", "EN_PREPARACION") |
| fecha_inicio | datetime | (none) | — | Filter: orders created >= this timestamp (ISO 8601) |
| fecha_fin | datetime | (none) | — | Filter: orders created <= this timestamp (ISO 8601) |
| usuario_id | UUID | (none) | — | Filter by customer UUID |
| monto_min | Decimal | (none) | — | Filter: total >= monto_min |
| monto_max | Decimal | (none) | — | Filter: total <= monto_max |

### Example Request
```http
GET /api/v1/admin/pedidos?page=2&size=20&estado_codigo=PENDIENTE&fecha_inicio=2026-01-01T00:00:00Z&monto_min=100.00
Authorization: Bearer <jwt_token>
```

### Response Schema

```python
class AdminOrderListItem(BaseModel):
    id: UUID  # Order ID
    cliente_nombre: str | None  # Customer full_name (NULL if user soft-deleted)
    usuario_id: UUID  # Customer ID
    estado_codigo: str  # e.g., "PENDIENTE", "CONFIRMADO"
    total: Decimal  # Order total (subtotal + envío)
    created_at: datetime  # Order creation timestamp
    direccion_calle: str | None  # Street from direccion_snapshot JSON (optional)

class AdminOrderListResponse(BaseModel):
    items: list[AdminOrderListItem]
    total: int  # Total matching orders (across all pages)
    page: int  # Current page
    size: int  # Items per page
    pages: int  # Total pages = ceil(total / size)
```

### Response Example (200 OK)
```json
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "cliente_nombre": "Juan Pérez",
      "usuario_id": "550e8400-e29b-41d4-a716-446655440001",
      "estado_codigo": "PENDIENTE",
      "total": "320.50",
      "created_at": "2026-06-03T14:30:00Z",
      "direccion_calle": "Av. 9 de Julio"
    }
  ],
  "total": 347,
  "page": 2,
  "size": 20,
  "pages": 18
}
```

### Error Responses

| Status | Condition |
|--------|-----------|
| 401 Unauthorized | Missing or invalid JWT token |
| 403 Forbidden | User does not have ADMIN or PEDIDOS role |
| 422 Unprocessable Entity | Invalid query params (e.g., page < 1, size > 100, invalid date format) |

---

## Endpoint 2: Change Order State (Admin)

### Route
```
PATCH /api/v1/admin/pedidos/{id}/estado
```

### Parameters

| Name | Location | Type | Required |
|------|----------|------|----------|
| id | Path | UUID | Yes |
| Body | Body | AdminChangeStateRequest | Yes |

### Authentication & Authorization
- **Required**: JWT token in Authorization header
- **Role**: ADMIN or PEDIDOS

### Request Schema

```python
class AdminChangeStateRequest(BaseModel):
    nuevo_estado: str = Field(..., min_length=1, max_length=20)
    motivo: str | None = Field(None, max_length=500)

    # Example: {"nuevo_estado": "EN_PREPARACION", "motivo": "Cliente confirmó recepción"}
```

### Request Validation
- `nuevo_estado`: Required, 1–20 characters, alphanumeric + underscore
- `motivo`: Optional, max 500 characters

### State Transition Validation

Transitions are defined by the existing FSM in `backend/app/pedidos/service.py::TRANSITIONS`.

### Validation Rules
1. **Order exists & not soft-deleted**: Return 404 if not found
2. **Not in terminal state**: Reject if current state is ENTREGADO or CANCELADO
3. **Valid transition**: nuevo_estado must be in TRANSITIONS[estado_actual]
4. **Role authorized**: Current user role must be in transition["roles"]
5. **Stock action**: If "restore", increment stock for all order items

### Example Request
```http
PATCH /api/v1/admin/pedidos/550e8400-e29b-41d4-a716-446655440000/estado
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "nuevo_estado": "EN_PREPARACION",
  "motivo": "Confirmada disponibilidad de ingredientes"
}
```

### Response Schema

Returns the updated order in `PedidoRead` format:

```python
class PedidoRead(BaseModel):
    id: UUID
    estado_codigo: str
    subtotal: Decimal
    costo_envio: Decimal
    total: Decimal
    created_at: datetime

    class Config:
        from_attributes = True
```

### Response Example (200 OK)
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "estado_codigo": "EN_PREPARACION",
  "subtotal": "270.50",
  "costo_envio": "50.00",
  "total": "320.50",
  "created_at": "2026-06-03T14:30:00Z"
}
```

### Error Responses

| Status | Condition |
|--------|-----------|
| 400 Bad Request | Invalid JSON body (e.g., missing nuevo_estado) |
| 401 Unauthorized | Missing or invalid JWT token |
| 403 Forbidden | User role not in transition["roles"] or not ADMIN/PEDIDOS |
| 404 Not Found | Order ID not found or soft-deleted |
| 422 Unprocessable Entity | Invalid transition (e.g., ENTREGADO→PENDIENTE) or order in terminal state |
| 500 Internal Server Error | Transaction failure; all changes rolled back |

### Side Effects

1. **HistorialEstadoPedido Entry**: Creates audit record with:
   - pedido_id = id
   - estado_desde = current estado_codigo
   - estado_nuevo = nuevo_estado
   - actor_id = current_user.id
   - motivo = request.motivo
   - created_at = now()

2. **Stock Restoration** (if applicable): If transition["stock_action"] == "restore":
   - For each DetallePedido in the order:
     - Increment Producto.stock_cantidad by item.cantidad

3. **Database Transaction**: Wrapped in transaction; rolls back all changes on any error.

---

## Endpoint 3: Get Order Detail (Admin)

### Route
```
GET /api/v1/admin/pedidos/{id}
```

### Parameters

| Name | Location | Type |
|------|----------|------|
| id | Path | UUID |

### Authentication & Authorization
- **Required**: JWT token in Authorization header
- **Role**: ADMIN or PEDIDOS

### Example Request
```http
GET /api/v1/admin/pedidos/550e8400-e29b-41d4-a716-446655440000
Authorization: Bearer <jwt_token>
```

### Response Schema

Returns the order in `PedidoDetail` format (extends `PedidoRead`):

```python
class DetallePedidoRead(BaseModel):
    id: UUID
    producto_id: UUID
    nombre_snapshot: str
    precio_snapshot: Decimal
    cantidad: int
    subtotal: Decimal
    personalizacion: list[UUID] | None

class HistorialRead(BaseModel):
    estado_desde: str | None
    estado_nuevo: str
    actor_id: UUID | None
    motivo: str | None
    created_at: datetime

class PedidoDetail(BaseModel):
    id: UUID
    estado_codigo: str
    subtotal: Decimal
    costo_envio: Decimal
    total: Decimal
    created_at: datetime
    items: list[DetallePedidoRead] = []
    historial: list[HistorialRead] = []
```

### Response Example (200 OK)
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "estado_codigo": "EN_PREPARACION",
  "subtotal": "270.50",
  "costo_envio": "50.00",
  "total": "320.50",
  "created_at": "2026-06-03T14:30:00Z",
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440100",
      "producto_id": "550e8400-e29b-41d4-a716-446655440200",
      "nombre_snapshot": "Milanesa de Pollo",
      "precio_snapshot": "85.50",
      "cantidad": 2,
      "subtotal": "171.00",
      "personalizacion": []
    }
  ],
  "historial": [
    {
      "estado_desde": null,
      "estado_nuevo": "PENDIENTE",
      "actor_id": "550e8400-e29b-41d4-a716-446655440001",
      "motivo": null,
      "created_at": "2026-06-03T14:30:00Z"
    }
  ]
}
```

### Error Responses

| Status | Condition |
|--------|-----------|
| 401 Unauthorized | Missing or invalid JWT token |
| 403 Forbidden | User does not have ADMIN or PEDIDOS role |
| 404 Not Found | Order ID not found or soft-deleted |

---

## Implementation Notes

### Query Optimization

**Endpoint 1 (List Orders)**:
- Use `LEFT OUTER JOIN user` on `usuario_id` for `cliente_nombre`
- Apply all filters with `WHERE` clauses (estado, dates, user, amounts)
- Order by `created_at DESC` for most recent first
- Soft-delete check: `WHERE soft_deleted_at IS NULL`

**Endpoint 3 (Get Detail)**:
- Eager load `items` (DetallePedido) and `historial` (HistorialEstadoPedido)
- Left join `user` table on `historial.actor_id` for actor names
- Single query with JOINs, not N+1

### Transaction Handling

**Endpoint 2 (Change State)**:
- Wrap all operations in database transaction
- Use `SELECT ... FOR UPDATE` on Producto rows when restoring stock (prevents concurrent modifications)
- Rollback entire transaction on any error
- Commit only if all steps succeed

