## 1. Backend — Admin Repository Layer

- [x] 1.1 Agregar `AdminProductoRepository` en `backend/app/admin/repository.py` con método `list_all_admin(skip, limit, search, disponible, eliminado, categoria_id)` que no filtra `soft_deleted_at IS NULL` por defecto
- [x] 1.2 Agregar `AdminCategoriaRepository` en `backend/app/admin/repository.py` con método `list_all_admin(eliminado)` que no filtra `soft_deleted_at IS NULL`
- [x] 1.3 Agregar `AdminIngredienteRepository` en `backend/app/admin/repository.py` con método `list_all_admin(skip, limit, es_alergeno, eliminado)` que no filtra `soft_deleted_at IS NULL`

## 2. Backend — Admin Schemas

- [x] 2.1 Crear `AdminProductoListItem`, `AdminProductoListResponse` en `backend/app/admin/schemas.py` con campos: id, nombre, precio_base, stock_cantidad, disponible, eliminado (bool), soft_deleted_at, created_at, categorias
- [x] 2.2 Crear `AdminCategoriaListItem`, `AdminCategoriaListResponse` en `backend/app/admin/schemas.py` con campos: id, nombre, parent_id, eliminado (bool), soft_deleted_at, created_at
- [x] 2.3 Crear `AdminIngredienteListItem`, `AdminIngredienteListResponse` en `backend/app/admin/schemas.py` con campos: id, nombre, es_alergeno, eliminado (bool), soft_deleted_at, created_at

## 3. Backend — Admin Service

- [x] 3.1 Agregar método `list_productos_admin(page, size, search, disponible, eliminado, categoria_id)` en `AdminService` que use `AdminProductoRepository` y retorne `AdminProductoListResponse`
- [x] 3.2 Agregar método `list_categorias_admin(eliminado)` en `AdminService` que use `AdminCategoriaRepository` y retorne `AdminCategoriaListResponse`
- [x] 3.3 Agregar método `list_ingredientes_admin(page, size, es_alergeno, eliminado)` en `AdminService` que use `AdminIngredienteRepository` y retorne `AdminIngredienteListResponse`

## 4. Backend — Admin Router

- [x] 4.1 Agregar `GET /api/v1/admin/productos` con RBAC `require_role("ADMIN", "STOCK")`, query params: page, size, search, disponible, eliminado, categoria_id
- [x] 4.2 Agregar `GET /api/v1/admin/categorias` con RBAC `require_role("ADMIN", "STOCK")`, query param: eliminado
- [x] 4.3 Agregar `GET /api/v1/admin/ingredientes` con RBAC `require_role("ADMIN", "STOCK")`, query params: page, size, es_alergeno, eliminado

## 5. Backend — Enhance Existing Productos Endpoint

- [x] 5.1 Agregar query param `incluir_eliminados: bool = False` a `GET /api/v1/productos` en `productos/router.py`
- [x] 5.2 Modificar `ProductoRepository.get_all()` para aceptar flag `include_deleted` que omita el filtro `soft_deleted_at IS NULL`
- [x] 5.3 Modificar `ProductoService.list_productos()` para pasar `include_deleted` al repo cuando `incluir_eliminados=True` y usuario es ADMIN/STOCK, ignorar en otro caso

## 6. Frontend — API Client

- [x] 6.1 Crear `shared/api/adminCatalogApi.ts` con funciones `fetchAdminProductos()`, `fetchAdminCategorias()`, `fetchAdminIngredientes()` usando el cliente Axios existente

## 7. Frontend — Entity Hooks (TanStack Query)

- [x] 7.1 Crear `features/admin-catalog/hooks/useAdminProductos.ts` con `useQuery` para listar productos admin + `useMutation` para crear/editar/eliminar usando endpoints existentes
- [x] 7.2 Crear `features/admin-catalog/hooks/useAdminCategorias.ts` con `useQuery` para listar categorías admin + `useMutation` para crear/editar/eliminar
- [x] 7.3 Crear `features/admin-catalog/hooks/useAdminIngredientes.ts` con `useQuery` para listar ingredientes admin + `useMutation` para crear/editar/eliminar

## 8. Frontend — Admin Pages

- [x] 8.1 Crear `pages/admin/AdminProductosPage.tsx` con tabla de productos (columnas: nombre, precio, stock, disponible badge, eliminado badge), filtros (búsqueda, disponibilidad, eliminados), modales de crear/editar, confirmación de eliminación
- [x] 8.2 Crear `pages/admin/AdminCategoriasPage.tsx` con vista jerárquica de categorías, indicador de eliminadas, modales de crear/editar (con selector de padre), confirmación de eliminación
- [x] 8.3 Crear `pages/admin/AdminIngredientesPage.tsx` con tabla (nombre, alérgeno badge, eliminado badge), filtros, modales de crear/editar, confirmación de eliminación

## 9. Frontend — Router & Navigation

- [x] 9.1 Agregar rutas `/admin/productos`, `/admin/categorias`, `/admin/ingredientes` con `ProtectedRoute` y `allowedRoles={["ADMIN", "STOCK"]}` usando `React.lazy()`
- [x] 9.2 Actualizar `shared/config/navigation.ts` agregando ítem "Catálogo" con sub-ítems Productos/Categorías/Ingredientes, visible solo para ADMIN y STOCK
- [x] 9.3 Verificar que el sidebar renderiza el nuevo ítem y la navegación funciona correctamente

## 10. Verification

- [x] 10.1 Verificar que `GET /api/v1/admin/productos` retorna productos soft-deleted y response 403 para CLIENT
- [x] 10.2 Verificar que `GET /api/v1/admin/categorias` retorna categorías soft-deleted y response 403 para CLIENT
- [x] 10.3 Verificar que `GET /api/v1/admin/ingredientes` retorna ingredientes soft-deleted y response 403 para CLIENT
- [x] 10.4 Verificar que `GET /api/v1/productos?incluir_eliminados=true` funciona para ADMIN y es ignorado para CLIENT
- [x] 10.5 Verificar build frontend sin errores de TypeScript
