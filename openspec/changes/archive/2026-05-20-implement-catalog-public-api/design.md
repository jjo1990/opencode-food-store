# Design: implement-catalog-public-api

## Context

The current products module has CRUD endpoints but doesn't distinguish between public and admin access for the list endpoint. The `GET /productos` returns `stock_cantidad` in its response, doesn't support `precio_min`/`precio_max` filters, and defaults to showing all products regardless of `disponible` status.

The categories tree endpoint (`GET /categorias`) is already public with no auth — this is correct and needs no changes.

**Current state:**

- `ProductoResponse` includes `stock_cantidad` (exposed to all)
- `GET /productos` has `disponible` filter defaulting to None (shows all)
- No `precio_min`/`precio_max` filter support
- Repository `get_all()` already supports `categoria_id`, `nombre` ILIKE
- No optional auth on public endpoints

## Goals / Non-Goals

**Goals:**

- Public product list: `disponible=true` by default, filtered to active products only
- Admin product list: can filter by `disponible` param
- Add `precio_min` and `precio_max` filters to repository + service
- Public response schemas without `stock_cantidad`
- Admin response schemas keep `stock_cantidad` (admin needs it)
- Detail view for public with relations but no stock quantity

**Non-Goals:**

- Category tree changes (already public)
- Product CRUD mutations (already in Change 19)
- Frontend UI (Change 21)

## Decisions

### 1. Two-tier response schemas

**Decision:** Create `PublicProductoResponse` (without stock) and `ProductoResponse` (with stock).
**Rationale:** The public should not see exact stock quantities (business risk). Admin/STOCK need it for inventory management.
**Alternative considered:** Single schema with nullable `stock_cantidad=null` for public — rejected because it pollutes the API contract with fields that have no meaning for certain consumers.

### 2. Optional auth dependency for role-aware filtering

**Decision:** Use `Optional[User] = Depends(get_optional_current_user)` pattern. If user is present and has ADMIN/STOCK role, show all. Otherwise, filter to `disponible=true`.
**Rationale:** A single endpoint that behaves differently based on auth is cleaner than two separate endpoints.
**Implementation:**

```python
async def get_optional_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(http_bearer_optional),
    db: Session = Depends(get_db)
) -> User | None:
    if not credentials:
        return None
    try:
        return await get_current_user(credentials, db)
    except Exception:
        return None
```

**Alternative considered:** Two separate endpoints (`/public/productos` and `/admin/productos`) — rejected because it doubles the API surface and complicates frontend logic.

### 3. Price range as query params

**Decision:** `precio_min` and `precio_max` are optional `Decimal` query params on `GET /productos`.
**Rationale:** Consistent with existing filter pattern (categoria_id, nombre). Simple to implement in repository with `>=` and `<=` on the `precio_base` Numeric column.
**Alternative considered:** Single `precio_rango` param with comma-separated values — rejected for being non-standard and harder to document in Swagger.

### 4. Categories tree stays untouched

**Decision:** No changes to `GET /categorias` endpoint or CategoriaService.
**Rationale:** It's already public, returns the tree correctly, and filters out soft-deleted. Verified.

## Components

### Schema Changes (backend/app/productos/schemas.py)

| New Schema                 | Fields                                                                   | Used By             |
| -------------------------- | ------------------------------------------------------------------------ | ------------------- |
| `PublicProductoResponse`   | id, nombre, descripcion, precio_base, disponible, imagen_url, created_at | Public list         |
| `PublicProductoDetail`     | PublicProductoResponse + categorias, ingredientes                        | Public detail       |
| `PublicPaginatedProductos` | items (list[PublicProductoResponse]), total, skip, limit                 | Public list wrapper |

### Repository Changes (backend/app/productos/repository.py)

| Method      | Change                                                                     |
| ----------- | -------------------------------------------------------------------------- |
| `get_all()` | Add `precio_min: Decimal \| None` and `precio_max: Decimal \| None` params |
| `count()`   | Add same params                                                            |

### Service Changes (backend/app/productos/service.py)

| Method             | Change                                                                                 |
| ------------------ | -------------------------------------------------------------------------------------- |
| `list_productos()` | Add `precio_min`, `precio_max`. Accept `is_public: bool` flag for role-aware filtering |
| `get_producto()`   | Return `PublicProductoDetail` for public                                               |
| New method         | `list_productos_public()` — delegates to repo with `disponible=true` default           |

### Router Changes (backend/app/productos/router.py)

| Endpoint              | Change                                                                                                                                             |
| --------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| `GET /productos`      | Add optional auth. Public: `disponible=true` default. Admin: `disponible` param. Add `precio_min`, `precio_max`. Return `PublicPaginatedProductos` |
| `GET /productos/{id}` | Return `PublicProductoDetail` instead of `ProductoDetail`                                                                                          |

### New Dependency (backend/app/core/dependencies.py)

| Function                      | Purpose                                                          |
| ----------------------------- | ---------------------------------------------------------------- |
| `get_optional_current_user()` | Returns `User \| None` without throwing on missing/invalid token |

## Implementation Notes

1. **Backward compatibility:** The existing `ProductoResponse` and `ProductoDetail` remain for admin endpoints (POST, PUT, PATCH). Only GET endpoints switch to public schemas.

2. **Price filter in repository:**

   ```python
   if precio_min is not None:
       query = query.filter(Producto.precio_base >= precio_min)
   if precio_max is not None:
       query = query.filter(Producto.precio_base <= precio_max)
   ```

3. **Ordering:** List always returns ordered by `nombre` ASC, consistent with existing categorias/ingredientes conventions.

4. **Public detail:** Even for public, we verify the product exists AND is `disponible=true`. Admin detail can see unavailable products.

## Risks / Trade-offs

| Risk                                                  | Mitigation                                                                                                                             |
| ----------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| Adding optional auth adds latency to public endpoints | The auth check is a lightweight JWT decode + user lookup — negligible cost. `http_bearer_optional` doesn't require the header to exist |
| Two response schemas increase maintenance             | They're thin wrappers — `PublicProductoResponse` is `ProductoResponse` minus one field. Easy to keep in sync                           |
| Public endpoint exposing too much via error messages  | Service returns "Producto no encontrado" for both not-found and not-available cases to avoid leaking info                              |
