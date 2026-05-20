# Spec: Catalog Public API

## Public Schemas

### PublicProductoResponse

```
id: UUID
nombre: str
descripcion: str | None
precio_base: Decimal
disponible: bool
imagen_url: str | None
created_at: datetime
```

NOTE: Does NOT include `stock_cantidad` (exact stock is internal).

### PublicProductoDetail

Inherits PublicProductoResponse plus:

```
categorias: list[CategoriaEnProducto]  # { id, nombre }
ingredientes: list[IngredienteEnProducto]  # { id, nombre, es_alergeno, es_removible }
```

### PublicPaginatedProductos

```
items: list[PublicProductoResponse]
total: int
skip: int
limit: int
```

## Endpoints

### GET /api/v1/productos

- **Auth:** Optional (if token present AND ADMIN/STOCK → shows all; otherwise → public)
- **Query params:**
  - `skip`: int, default 0, ge 0
  - `limit`: int, default 20, ge 1, le 100
  - `categoria_id`: UUID, optional
  - `nombre`: str, optional — ILIKE search
  - `precio_min`: Decimal, optional, ge 0
  - `precio_max`: Decimal, optional, ge 0
  - `disponible`: bool, optional — ADMIN/STOCK only (public ignores this, always true)
- **Response:** 200 PublicPaginatedProductos
- **Behavior:**
  - **Public:** `disponible=true` AND `soft_deleted_at IS NULL` (hard filter)
  - **ADMIN/STOCK:** respect `?disponible=` param; excludes soft-deleted

### GET /api/v1/productos/{id}

- **Auth:** Optional (same role-aware logic)
- **Response:** 200 PublicProductoDetail
- **Behavior:**
  - **Public:** product must be `disponible=true` AND not soft-deleted
  - **ADMIN/STOCK:** can see available and unavailable (not soft-deleted)
  - **404:** if not found, soft-deleted, or (public) not available

### GET /api/v1/categorias

- **Auth:** None (already public)
- **Response:** 200 list[CategoriaTreeNode]
- **No changes needed** — already returns active-only tree

## Error Responses

- **404:** "Producto no encontrado" (same message for missing/not-available to avoid info leakage)
- **400:** Invalid precio_min/precio_max values
