# Spec: Products CRUD

## Models

### Producto

```
id: UUID (PK, default gen_random_uuid)
nombre: VARCHAR(200), NOT NULL
descripcion: TEXT, nullable
precio_base: NUMERIC(10, 2), NOT NULL, CHECK >= 0
stock_cantidad: INTEGER, NOT NULL, DEFAULT 0, CHECK >= 0
disponible: BOOLEAN, NOT NULL, DEFAULT true
imagen_url: VARCHAR(500), nullable
created_at: TIMESTAMP, NOT NULL, DEFAULT NOW()
updated_at: TIMESTAMP, NOT NULL, DEFAULT NOW()
soft_deleted_at: TIMESTAMP, nullable
```

### ProductoCategoria (M:M junction)

```
producto_id: UUID, PK, FK → producto.id ON DELETE CASCADE
categoria_id: UUID, PK, FK → categoria.id ON DELETE CASCADE
```

### ProductoIngrediente (M:M junction)

```
producto_id: UUID, PK, FK → producto.id ON DELETE CASCADE
ingrediente_id: UUID, PK, FK → ingrediente.id ON DELETE CASCADE
es_removible: BOOLEAN, NOT NULL, DEFAULT true
```

## API Endpoints

### POST /api/v1/productos

- **Roles:** ADMIN, STOCK
- **Request body:**
  ```json
  {
    "nombre": "string (1-200 chars)",
    "descripcion": "string | null",
    "precio_base": "number (>= 0, 2 decimal places)",
    "stock_cantidad": "integer (>= 0, default 0)",
    "disponible": "boolean (default true)",
    "imagen_url": "string | null (URL)",
    "categoria_ids": ["uuid"],
    "ingrediente_ids": ["uuid"]
  }
  ```
- **Response:** 201 ProductoResponse
- **Validation:**
  - nombre is required, at least 1 char
  - precio_base >= 0
  - stock_cantidad >= 0
  - All categoria_ids must reference existing, active categorias
  - All ingrediente_ids must reference existing, active ingredientes

### GET /api/v1/productos

- **Roles:** Public (filtered), ADMIN/STOCK (all)
- **Query params:** `skip` (int, default 0), `limit` (int, default 20, max 100), `categoria_id` (uuid, optional), `nombre` (string, optional — ILIKE search), `disponible` (bool, optional — ignored for public, which sees only available)
- **Response:** 200 PaginatedProductos
- **Behavior:**
  - Public: only `disponible=true` AND `soft_deleted_at IS NULL`
  - ADMIN/STOCK: all except soft-deleted; can filter by `disponible`

### GET /api/v1/productos/{id}

- **Roles:** Public
- **Response:** 200 ProductoDetail (includes categorias and ingredientes with nested data)
- **Error:** 404 if not found or soft-deleted

### PUT /api/v1/productos/{id}

- **Roles:** ADMIN, STOCK
- **Request body:** Same as POST but all fields optional
- **Response:** 200 ProductoResponse
- **Error:** 404 if not found

### PATCH /api/v1/productos/{id}/disponibilidad

- **Roles:** ADMIN, STOCK
- **Request body:** `{ "disponible": boolean }`
- **Response:** 200 ProductoResponse
- **Error:** 404 if not found

### DELETE /api/v1/productos/{id}

- **Roles:** ADMIN, STOCK
- **Response:** 204 No Content
- **Behavior:** Soft delete (sets soft_deleted_at)

### GET /api/v1/productos/{id}/ingredientes

- **Roles:** Public
- **Response:** 200 list of IngredienteResponse with es_removible
- **Error:** 404 if product not found

## Error Responses

- **404:** "Producto no encontrado"
- **400:** Validation errors (precio_base < 0, stock_cantidad < 0, missing fields)
- **409:** (reserved for future use — stock conflicts)
- **403:** Forbidden if role insufficient via `require_role()`

## Soft Delete Rules

- All read queries filter `soft_deleted_at IS NULL` by default
- Soft-deleted productos are excluded from all public and admin GET endpoints (including GET /productos/{id})
- Junction table rows are NOT modified on product soft delete
- There is NO hard delete endpoint
