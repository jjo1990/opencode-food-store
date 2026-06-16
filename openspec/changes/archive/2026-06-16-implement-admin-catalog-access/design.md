## Context

El módulo `backend/app/admin/` ya contiene gestión de usuarios (Change 37) y gestión de pedidos (Change 38) siguiendo el patrón Router → Service → Repository → Schemas. Los módulos de catálogo (`productos/`, `categorias/`, `ingredientes/`) tienen CRUD completo con RBAC ADMIN/STOCK en escritura, pero los endpoints GET filtran `soft_deleted_at IS NULL` y los públicos ocultan `disponible=false`. No existe una vista administrativa unificada.

**Constraints:**

- No modificar los módulos de catálogo existentes (productos, categorias, ingredientes) más allá de agregar un query param opcional
- Seguir el patrón exacto del admin module existente (AdminService, Admin*Repository, Admin*Schemas)
- Reutilizar modelos y repositorios existentes donde sea posible
- Sin migraciones nuevas: todos los modelos ya existen

## Goals / Non-Goals

**Goals:**

- Proveer endpoints admin de listado que muestren el catálogo completo (incluyendo soft-deleted y no disponibles)
- Agregar página frontend de gestión de catálogo en el panel admin (productos, categorías, ingredientes)
- Agregar ítem "Catálogo" en el sidebar admin visible solo para ADMIN/STOCK

**Non-Goals:**

- Reimplementar CRUD de escritura (POST/PUT/DELETE) — ya existen y funcionan con RBAC correcto
- Modificar el comportamiento de endpoints públicos de catálogo
- Agregar migraciones de base de datos
- Crear sistema de notificaciones o métricas relacionadas al catálogo

## Decisions

### D1: Nuevos repositorios admin en lugar de modificar los existentes

Se crean `AdminProductoRepository`, `AdminCategoriaRepository`, `AdminIngredienteRepository` en `backend/app/admin/repository.py`. Estos extienden las queries base de los repositorios de catálogo pero **sin** filtrar `soft_deleted_at IS NULL`.

**Alternativa considerada:** Agregar flag `include_deleted` a los repos existentes. Rechazada porque ensucia la interfaz pública con responsabilidades administrativas.

**Rationale:** Separación clara de responsabilidades. Los repos de catálogo sirven al público; los admin repos sirven al panel. El AdminOrderRepository ya existe con este mismo pattern.

### D2: Endpoints admin bajo `/api/v1/admin/` — no modificar rutas de catálogo existentes

Nuevos endpoints:

- `GET /api/v1/admin/productos` → `AdminService.list_productos_admin()`
- `GET /api/v1/admin/categorias` → `AdminService.list_categorias_admin()`
- `GET /api/v1/admin/ingredientes` → `AdminService.list_ingredientes_admin()`

Los endpoints públicos `/api/v1/productos`, `/api/v1/categorias`, `/api/v1/ingredientes` permanecen sin cambios.

**Alternativa considerada:** Modificar endpoints públicos para que devuelvan datos distintos según el rol. Rechazada porque acopla responsabilidades y complica el versionado de API.

**Rationale:** Principio de separación de concerns. El prefijo `/admin` delimita claramente el contexto administrativo, igual que los endpoints de usuarios y pedidos admin.

### D3: Query param `incluir_eliminados` en GET /api/v1/productos existente

Se agrega `incluir_eliminados: bool = Query(False)` al endpoint `GET /api/v1/productos`. Cuando es `True` y el usuario es ADMIN/STOCK, el repositorio omite el filtro `soft_deleted_at IS NULL`. Si el usuario no es ADMIN/STOCK, se ignora el parámetro.

**Rationale:** El endpoint público ya tiene lógica role-aware (devuelve `ProductoResponse` vs `PublicProductoResponse`). Agregar este flag mantiene la API consistente y evita duplicar el endpoint de listado con filtros.

### D4: Schemas admin reutilizan schemas de catálogo con composición

En lugar de duplicar campos, los schemas admin extienden los existentes:

- `AdminProductoListItem` → incluye `stock_cantidad`, `disponible`, `soft_deleted_at`, `eliminado`
- `AdminCategoriaListItem` → incluye `soft_deleted_at`, `eliminado`, `parent_id`
- `AdminIngredienteListItem` → incluye `soft_deleted_at`, `eliminado`

### D5: Frontend: Feature-Sliced Design estricto

Páginas admin de catálogo en `pages/admin/`:

- `AdminProductosPage.tsx` — listado con filtros + modales crear/editar/eliminar
- `AdminCategoriasPage.tsx` — árbol jerárquico + modales
- `AdminIngredientesPage.tsx` — tabla + modales

Hooks TanStack Query en `features/admin-catalog/`:

- `useAdminProductos()`, `useAdminCategorias()`, `useAdminIngredientes()`

API client en `shared/api/adminCatalogApi.ts`

**Rationale:** Sigue el patrón FSD establecido por `implement-catalog-frontend-ui` y `implement-admin-orders-management-ui`. Los hooks de TanStack Query se separan de las páginas para reutilización.

## Risks / Trade-offs

| Risk                                                        | Mitigation                                                                                                               |
| ----------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| Duplicación de queries entre repos catálogo y admin         | Los admin repos son queries simples sin joins complejos. Si crecen, se puede refactorizar a un query builder compartido. |
| Frontend admin depende de endpoints de escritura existentes | Los endpoints POST/PUT/DELETE de catálogo ya están implementados y probados. Solo se agregan hooks para consumirlos.     |
| Sidebar navigation debe respetar lazy loading               | Se agregan rutas con `React.lazy()` siguiendo el pattern de `navigation-by-role`.                                        |
