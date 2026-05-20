# Proposal: implement-catalog-public-api

## What

Create the **public-facing catalog API** for Food Store. This change enhances the existing productos endpoints with:

- **Public product listing** with advanced filters: `categoria_id`, `nombre` (ILIKE search), `precio_min`, `precio_max`, pagination
- **Public product detail** with full relations (categorías, ingredientes, es_alergeno) — WITHOUT exposing exact stock
- **Role-aware behavior**: public users only see `disponible=true` products; ADMIN/STOCK can see all
- **Public categories tree endpoint** (already exists — verify alignment)
- **Dedicated public schemas** that don't leak internal fields (stock_cantidad)

## Why

- The current `GET /productos` mixes admin and public concerns — it exposes `stock_cantidad` and has no `precio_min`/`precio_max` filters
- US-018 requires the catalog to only show `disponible=true` AND `soft_deleted_at IS NULL` for the public
- US-019 requires search by name and category
- US-023 requires price range filtering
- This is the **backdoor for all frontend catalog features** (Change 21)

## Dependencies

- ✅ `implement-products-crud` (Change 19) — Producto CRUD with repository filters
- ✅ `implement-categories-crud` (Change 17) — Categoria tree endpoint (already public)
- ✅ `implement-route-protection` (Change 13) — `get_current_user` optional dependency

## Scope

### In Scope

- `PublicProductoResponse` and `PublicPaginatedProductos` schemas (no stock)
- `PublicProductoDetail` schema for detail view
- `precio_min` and `precio_max` filters in repository/service
- Role-aware list endpoint: public defaults to `disponible=true`, admin passes `?disponible=`
- Ensure GET /categorias tree is public (already is — just verify)

### Out of Scope

- Category tree modifications (already exists in Change 17)
- Frontend catalog UI (Change 21)
- Stock management endpoints

## Effort

~3 hours (enhancement of existing code, not greenfield)
