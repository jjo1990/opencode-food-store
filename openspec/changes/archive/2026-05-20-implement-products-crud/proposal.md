# Proposal: implement-products-crud

## What

Implement the **Producto** CRUD module for the Food Store catalog. This includes:

- **Producto model** with fields: id (UUID), nombre, descripcion, precio_base (DECIMAL), stock_cantidad (INTEGER), disponible (BOOLEAN), imagen_url, timestamps, soft delete
- **Junction tables**: `ProductoCategoria` (M:M between Producto and Categoria) and `ProductoIngrediente` (M:M between Producto and Ingrediente with `es_removible` flag)
- **Full CRUD endpoints** with pagination, filtering, role-based access
- **Alembic migration** for all product-related tables

## Why

Products are the core entity of the catalog. Without products, the e-commerce platform cannot operate. This change is:

- **Dependency** for Changes 20 (Catalog Public API), 21 (Catalog Frontend UI), 27 (Checkout Validation), 28 (Order Creation), and all downstream features
- **Required** by US-015 through US-023 (product browsing, searching, and management)
- The final piece of Phase 2 catalog backend infrastructure

## Dependencies

- ✅ `implement-categories-crud` (Change 17) — Categoria model exists
- ✅ `implement-ingredients-crud` (Change 18) — Ingrediente model exists
- ✅ `implement-route-protection` (Change 13) — `require_role()` dependency available
- ✅ `implement-base-patterns` (Change 6) — BaseRepository, UoW, DB session available

## Scope

### In Scope

- Producto SQLAlchemy model with all fields and relationships
- ProductoCategoria and ProductoIngrediente junction models
- Full CRUD: schemas, repository, service, router
- Role-based access: ADMIN + STOCK can modify, public read for available products
- Alembic migration for 3 new tables
- Router registration in `main.py`

### Out of Scope

- Public catalog API with advanced filtering (Change 20)
- Catalog frontend UI (Change 21)
- Stock decrement on order confirmation (Change 32)
- Product image upload (static URL only)

## Effort

~6 hours (medium complexity due to M:M relationships)
