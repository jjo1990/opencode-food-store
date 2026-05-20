# Tasks: implement-products-crud

## T1 — Model Layer: Producto + Junction Tables

- [x] Create `backend/app/models/producto.py` with Producto model (UUID PK, nombre, descripcion, precio_base Numeric(10,2), stock_cantidad Integer, disponible Boolean, imagen_url String, created_at, updated_at, soft_deleted_at)
- [x] Create `backend/app/models/producto_categoria.py` with ProductoCategoria model (producto_id FK, categoria_id FK, composite PK)
- [x] Create `backend/app/models/producto_ingrediente.py` with ProductoIngrediente model (producto_id FK, ingrediente_id FK, es_removible Boolean, composite PK)
- [x] Update `backend/app/models/__init__.py` to import and export new models
- [x] Update `__all__` in models/**init**.py

## T2 — Alembic Migration

- [x] Generate migration: `alembic revision --autogenerate -m "add producto, producto_categoria, producto_ingrediente models"`
- [x] Verify migration creates 3 tables with correct columns, constraints, FKs, and indexes
- [x] Migration must be reversible (downgrade drops all 3 tables)

## T3 — Pydantic Schemas

- [x] Create `backend/app/productos/schemas.py` with:
  - `ProductoCreate`: nombre (1-200), descripcion (optional), precio_base (Decimal >= 0), stock_cantidad (int >= 0, default 0), disponible (bool, default true), imagen_url (optional), categoria_ids (list[uuid]), ingrediente_ids (list[uuid])
  - `ProductoUpdate`: all fields optional
  - `ProductoResponse`: id, nombre, descripcion, precio_base, stock_cantidad, disponible, imagen_url, created_at
  - `ProductoDisponibilidadUpdate`: disponible (bool)
  - `PaginatedProductos`: items (list[ProductoResponse]), total (int), skip (int), limit (int)
  - `ProductoDetail`: ProductoResponse + categorias (list[CategoriaResponse]), ingredientes (list with IngredienteResponse + es_removible)
  - `ProductoIngredienteResponse`: producto_id, ingrediente_id, es_removible

## T4 — Repository Layer

- [x] Create `backend/app/productos/repository.py` with ProductoRepository:
  - `create()`: create producto + bulk insert junction rows
  - `get_by_id(id)`: single producto with eager-loaded categorias, ingredientes
  - `get_all(skip, limit, categoria_id, nombre, disponible)`: filtered list with optional filters
  - `count()`: count with same filters
  - `update()`: update producto fields + sync junction rows (delete+insert)
  - `soft_delete()`: set soft_deleted_at
  - `toggle_disponibilidad()`: update disponible only
  - `get_ingredientes(producto_id)`: list ingredientes for a prodotto
  - All read queries filter `soft_deleted_at IS NULL`

## T5 — Service Layer

- [x] Create `backend/app/productos/service.py` with ProductoService:
  - `create_producto()`: validate categorias/ingredientes exist + active, check precio_base >= 0, check stock >= 0
  - `list_productos()`: delegate to repository with filters
  - `get_producto()`: 404 if not found
  - `update_producto()`: validate new categorias/ingredientes, check nombre non-empty
  - `toggle_disponibilidad()`: update only the disponible field
  - `delete_producto()`: soft delete
  - `get_ingredientes()`: list with ingredient details
  - Custom exceptions: ProductoNotFoundException (404), ProductoValidationException (400)

## T6 — Router Layer

- [x] Create `backend/app/productos/router.py` with APIRouter(prefix="/productos"):
  - `POST /productos` → create_producto (ADMIN, STOCK)
  - `GET /productos` → list_productos (public: only available; admin/stock: all)
  - `GET /productos/{id}` → get_producto (public)
  - `PUT /productos/{id}` → update_producto (ADMIN, STOCK)
  - `PATCH /productos/{id}/disponibilidad` → toggle_disponibilidad (ADMIN, STOCK)
  - `DELETE /productos/{id}` → delete_producto (ADMIN, STOCK)
  - `GET /productos/{id}/ingredientes` → get_ingredientes (public)
- [x] Use `response_model` on all endpoints
- [x] Use `status_code` explicitly (201 for POST, 204 for DELETE)

## T7 — Register Module

- [x] Create `backend/app/productos/__init__.py`
- [x] Register router in `backend/app/main.py`: `app.include_router(productos_router, prefix="/api/v1")`

## T8 — Verify

- [x] Run `python -c "from app.models.producto import Producto; print('OK')"`
- [x] Run `python -c "from app.productos.router import router; print('OK')"`
- [x] Verify all imports resolve correctly
- [x] Verify migration file is generated and valid
