# Tasks: implement-catalog-public-api

## T1 — Public Response Schemas

- [x] Add to `backend/app/productos/schemas.py`:
  - `PublicProductoResponse`: id, nombre, descripcion, precio_base, disponible, imagen_url, created_at (NO stock_cantidad), Config from_attributes=True
  - `PublicProductoDetail`: PublicProductoResponse + categorias (list[CategoriaEnProducto]), ingredientes (list[IngredienteEnProducto])
  - `PublicPaginatedProductos`: items (list[PublicProductoResponse]), total (int), skip (int), limit (int)

## T2 — Optional Auth Dependency

- [x] Add `get_optional_current_user()` to `backend/app/core/dependencies.py`:
  - Returns `User | None` — doesn't throw on missing/invalid token
  - Uses `HTTPBearer(auto_error=False)` for optional credential extraction
  - Returns `None` if no credentials or token invalid

## T3 — Repository Price Filters

- [x] Add `precio_min: Decimal | None` and `precio_max: Decimal | None` params to:
  - `ProductoRepository.get_all()`
  - `ProductoRepository.count()`
  - Filter: `Producto.precio_base >= precio_min` and `Producto.precio_base <= precio_max`

## T4 — Service Layer Role-Aware Logic

- [x] Update `ProductoService.list_productos()`:
  - Add `precio_min`, `precio_max` params
  - If `is_public=True`: force `disponible=True` filter (ignore provided value)
- [x] Add `ProductoService.get_producto_public(id)` method:
  - Returns `PublicProductoDetail`
  - Validates product is `disponible=True` AND not soft-deleted
  - Returns 404 for unavailable to public
- [x] Update `ProductoService.list_productos_public()` (or integrate into list_productos with flag)

## T5 — Router Public Endpoints

- [x] Update `GET /productos`:
  - Add optional auth via `get_optional_current_user()`
  - Add `precio_min`, `precio_max` query params
  - If auth user has ADMIN/STOCK role: pass filters through as-is
  - If public (no auth or non-admin): force `disponible=True`, return `PublicPaginatedProductos`
- [x] Update `GET /productos/{id}`:
  - Add optional auth
  - If public: call `get_producto_public()`, return `PublicProductoDetail`
  - If ADMIN/STOCK: call existing `get_producto()`, return `PublicProductoDetail` (or keep ProductoDetail?)

## T6 — Verify

- [x] Run `python -c "from app.productos.schemas import PublicProductoResponse, PublicProductoDetail, PublicPaginatedProductos; print('OK')"`
- [x] Run `python -c "from app.core.dependencies import get_optional_current_user; print('OK')"`
- [x] Verify all 7 product routes still resolve with `python -c "from app.main import app; rs = [r.path for r in app.routes if 'producto' in r.path.lower()]; print(len(rs))"`
- [x] Verify public routes work without auth header
