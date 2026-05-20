# Design: implement-products-crud

## Context

The catalog module currently has `Categoria` and `Ingrediente` models with full CRUD. Products are the central entity that ties them together via M:M relationships. The existing patterns (SQLAlchemy models with UUID PKs, feature-first module structure, service-layer validation, soft delete, role-based access via `require_role()`) must be followed consistently.

**Current state:**

- `backend/app/models/categoria.py` — Categoria model with self-referential FK
- `backend/app/models/ingrediente.py` — Ingrediente model with unique name
- `backend/app/categorias/` — Full CRUD module
- `backend/app/ingredientes/` — Full CRUD module with pagination
- Alembic has migrations for categoria, ingrediente, user, refresh_token

**Constraints:**

- Producto.precio_base must be `DECIMAL(10,2)` (never float) — stored as SQLAlchemy `Numeric(10, 2)`
- Producto.stock_cantidad must be `INTEGER CHECK >= 0`
- Junction tables: ProductoCategoria (M:M), ProductoIngrediente (M:M with es_removible)
- All queries must filter `soft_deleted_at IS NULL` by default
- Role access: ADMIN + STOCK for mutations, public for GET available products

## Goals / Non-Goals

**Goals:**

- Implement Producto model with all fields per ERD v5
- Implement ProductoCategoria and ProductoIngrediente junction models
- Full CRUD endpoints with proper validation and error handling
- Alembic migration for all 3 new tables
- Role-based access consistent with existing modules

**Non-Goals:**

- Public catalog API with advanced filtering (Change 20)
- Inventory decrement on order confirmation (Phase 5/6)
- Frontend UI (Change 21)
- Image upload handling

## Decisions

### 1. Numeric type for precio_base

**Decision:** Use SQLAlchemy `Numeric(10, 2)` instead of `Float`.
**Rationale:** Floats cause precision errors in financial calculations. ERD v5 explicitly requires `DECIMAL(10,2)`. This matches the `precio_snapshot` field in DetallePedido.
**Alternative considered:** `Float` — rejected due to rounding errors.

### 2. Junction tables as separate SQLAlchemy models

**Decision:** Model `ProductoCategoria` and `ProductoIngrediente` as explicit SQLAlchemy models (not just `association_table`).
**Rationale:** `ProductoIngrediente` has `es_removible` attribute that needs to be queryable. Explicit models allow direct repository access for advanced queries (e.g., "find products by ingredient category").
**Alternative considered:** SQLAlchemy `Table()` with `association_proxy` — rejected because it doesn't support extra columns well and makes queries harder.

### 3. Stock validation at service layer

**Decision:** Service layer validates `stock_cantidad >= 0` and `precio_base > 0` on create/update.
**Rationale:** Consistent with existing pattern (CategoriaService and IngredienteService both validate in service). DB-level CHECK constraint serves as defense-in-depth.
**Alternative considered:** DB-only validation — rejected because it gives worse error messages to API consumers.

### 4. No UoW in this CRUD

**Decision:** Use direct `Session` management (commit/refresh in repository).
**Rationale:** The existing categories and ingredients CRUD modules use this simpler pattern. UoW will be introduced in Phase 5 for transactional order creation where atomic commits across multiple entities are required.
**Migration path:** When UoW is introduced, service methods can be refactored to accept a UoW instance instead of `db: Session`.

### 5. Soft delete cascading

**Decision:** Soft delete on Producto does NOT cascade to junction tables. Rows in ProductoCategoria/ProductoIngrediente remain (they're referenced by existing orders via snapshots).
**Rationale:** Junction table rows represent historical associations. If a product is soft-deleted, its junction rows still hold valid data for existing orders. The catalog API filters `soft_deleted_at IS NULL` on the product, which effectively hides them from public view.

## Components

### Model Layer

| File                                 | Responsibility                                                                                                                                                                                                                             |
| ------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `app/models/producto.py`             | Producto model (UUID PK, nombre, descripcion, precio_base Numeric, stock_cantidad, disponible, imagen_url, timestamps, soft delete). Relationships: `categorias` (M:M via ProductoCategoria), `ingredientes` (M:M via ProductoIngrediente) |
| `app/models/producto_categoria.py`   | Association model with producto_id (FK), categoria_id (FK), composite PK                                                                                                                                                                   |
| `app/models/producto_ingrediente.py` | Association model with producto_id (FK), ingrediente_id (FK), es_removible (BOOL), composite PK                                                                                                                                            |

### Module Structure (`backend/app/productos/`)

| File            | Responsibility                                                                                                                                               |
| --------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `schemas.py`    | Pydantic request/response schemas: ProductoCreate, ProductoUpdate, ProductoResponse, PaginatedProductos, ProductoDetail (with nested categories/ingredients) |
| `repository.py` | ProductoRepository: CRUD + filtered queries (by categoria, by nombre ILIKE, by disponibilidad)                                                               |
| `service.py`    | ProductoService: validation, business rules, exception handling                                                                                              |
| `router.py`     | 7 endpoints with role guards                                                                                                                                 |

### API Endpoints

| Method | Path                                    | Roles                                       | Description                                  |
| ------ | --------------------------------------- | ------------------------------------------- | -------------------------------------------- |
| POST   | `/api/v1/productos`                     | ADMIN, STOCK                                | Create product with categories & ingredients |
| GET    | `/api/v1/productos`                     | Public (disponible=true), ADMIN/STOCK (all) | List with pagination & filters               |
| GET    | `/api/v1/productos/{id}`                | Public                                      | Detail with categories & ingredients         |
| PUT    | `/api/v1/productos/{id}`                | ADMIN, STOCK                                | Full update                                  |
| PATCH  | `/api/v1/productos/{id}/disponibilidad` | ADMIN, STOCK                                | Toggle disponible                            |
| DELETE | `/api/v1/productos/{id}`                | ADMIN, STOCK                                | Soft delete                                  |
| GET    | `/api/v1/productos/{id}/ingredientes`   | Public                                      | List ingredients for product                 |

## Data Model

```sql
-- Producto
CREATE TABLE producto (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre VARCHAR(200) NOT NULL,
    descripcion TEXT,
    precio_base NUMERIC(10, 2) NOT NULL CHECK (precio_base >= 0),
    stock_cantidad INTEGER NOT NULL DEFAULT 0 CHECK (stock_cantidad >= 0),
    disponible BOOLEAN NOT NULL DEFAULT true,
    imagen_url VARCHAR(500),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    soft_deleted_at TIMESTAMP
);

CREATE INDEX idx_producto_disponible ON producto(disponible) WHERE soft_deleted_at IS NULL;
CREATE INDEX idx_producto_nombre ON producto(nombre) WHERE soft_deleted_at IS NULL;

-- ProductoCategoria (M:M junction)
CREATE TABLE producto_categoria (
    producto_id UUID NOT NULL REFERENCES producto(id) ON DELETE CASCADE,
    categoria_id UUID NOT NULL REFERENCES categoria(id) ON DELETE CASCADE,
    PRIMARY KEY (producto_id, categoria_id)
);

-- ProductoIngrediente (M:M junction with extra field)
CREATE TABLE producto_ingrediente (
    producto_id UUID NOT NULL REFERENCES producto(id) ON DELETE CASCADE,
    ingrediente_id UUID NOT NULL REFERENCES ingrediente(id) ON DELETE CASCADE,
    es_removible BOOLEAN NOT NULL DEFAULT true,
    PRIMARY KEY (producto_id, ingrediente_id)
);
```

## Implementation Notes

1. **Nombre uniqueness:** Unlike Categoria and Ingrediente, Producto.nombre does NOT have a UNIQUE constraint. Products can have duplicate names (e.g., "Pizza" in different categories). Validation is limited to `nombre` being non-empty.

2. **List endpoint behavior:**
   - PUBLIC: `disponible=true` AND `soft_deleted_at IS NULL` (hard filter)
   - ADMIN/STOCK: can pass `?disponible=all` or `?disponible=true` or `?disponible=false` — includes all including non-available but NOT soft-deleted

3. **Category/Ingredient validation on create:** Validate that all referenced categoria_id and ingrediente_id values exist and are not soft-deleted. Return 404 with specific details for each missing reference.

4. **PATCH disponibilidad:** Separate endpoint from PUT. Only toggles `disponible` field. Accepts `{ "disponible": bool }`. Does NOT validate stock (a product can be available with 0 stock — business decision for visibility).

5. **Migrations:** Single migration file for all 3 tables. Migration is reversible (downgrade drops all 3 tables).

## Risks / Trade-offs

| Risk                                                          | Mitigation                                                                              |
| ------------------------------------------------------------- | --------------------------------------------------------------------------------------- |
| M:M relationships add query complexity (N+1 on list endpoint) | Use eager loading (`selectinload`) on repository queries to batch-load relationships    |
| Product name collisions across categories are allowed         | Document explicitly; admin UI should show category context                              |
| Missing migration could block downstream changes              | Migration included in this change; test by running `alembic upgrade head`               |
| Categoria/Ingrediente soft-deleted but referenced in Producto | Repository validates referenced entities are active (not soft-deleted) on create/update |
