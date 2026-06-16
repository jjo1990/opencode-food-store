## Why

Los administradores (ADMIN/STOCK) necesitan ver y gestionar el catálogo completo desde el panel admin, incluyendo productos no disponibles y elementos eliminados lógicamente que los endpoints públicos ocultan. Actualmente los endpoints de escritura ya aceptan ADMIN/STOCK, pero no existe una vista administrativa unificada con listings completos (incluyendo soft-deleted) ni interfaz frontend para gestionar productos, categorías e ingredientes desde el panel admin.

## What Changes

- **Nuevos endpoints admin de catálogo** bajo `/api/v1/admin/`:
  - `GET /api/v1/admin/productos` — listado de TODOS los productos (incluye soft-deleted y no disponibles) con filtros y paginación
  - `GET /api/v1/admin/categorias` — listado de TODAS las categorías (incluye soft-deleted)
  - `GET /api/v1/admin/ingredientes` — listado de TODOS los ingredientes (incluye soft-deleted)
- **Endpoint existente mejorado**: `GET /api/v1/productos` acepta query param `incluir_eliminados=true` cuando el usuario es ADMIN/STOCK para ver productos soft-deleted
- **Frontend admin**: Páginas de gestión de catálogo accesibles desde el sidebar admin
  - Página CRUD de productos (listado con filtros, crear, editar, eliminar)
  - Página CRUD de categorías (listado jerárquico, crear, editar, eliminar)
  - Página CRUD de ingredientes (listado, crear, editar, eliminar)
- **Sidebar admin**: Nuevo ítem "Catálogo" visible solo para ADMIN/STOCK con sub-ítems Productos, Categorías, Ingredientes

## Capabilities

### New Capabilities

- `admin-catalog`: Endpoints admin de listado de catálogo (productos, categorías, ingredientes) que incluyen elementos soft-deleted y no disponibles, con filtros avanzados y paginación. Acceso exclusivo ADMIN/STOCK.

### Modified Capabilities

_No se modifican specs existentes. Los endpoints públicos de catálogo (`GET /api/v1/productos`, `GET /api/v1/categorias`, `GET /api/v1/ingredientes`) mantienen su comportamiento actual. El nuevo query param `incluir_eliminados` es una adición no-breaking._

## Impact

- **Backend**: Nuevos archivos en `backend/app/admin/` (repository, service, router, schemas) extendiendo el módulo admin existente sin modificar módulos de catálogo
- **Dependencias**: `implement-products-crud`, `implement-categories-crud`, `implement-ingredients-crud`, `implement-rbac-system` (todas ya completadas y archivadas)
- **Frontend**: Nuevas páginas en `frontend/src/pages/admin/` y hooks en `frontend/src/features/admin-catalog/`
- **Sidebar**: Actualización de `shared/config/navigation.ts` para incluir ítem "Catálogo"
- **Sin cambios en BD**: No requiere migraciones nuevas — reutiliza modelos existentes
