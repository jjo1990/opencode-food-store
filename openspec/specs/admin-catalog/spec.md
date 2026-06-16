# admin-catalog Specification

## Purpose

TBD - created by archiving change implement-admin-catalog-access. Update Purpose after archive.

## Requirements

### Requirement: Admin puede listar todos los productos incluyendo eliminados

El sistema SHALL proveer un endpoint `GET /api/v1/admin/productos` que retorne todos los productos registrados, incluyendo aquellos con `soft_deleted_at` no nulo y aquellos con `disponible=false`. Solo accesible para usuarios con rol ADMIN o STOCK.

#### Scenario: Admin lista todos los productos con paginación

- **WHEN** un usuario ADMIN hace `GET /api/v1/admin/productos?page=1&size=20`
- **THEN** el sistema retorna una lista paginada con TODOS los productos (activos, inactivos, soft-deleted)
- **AND** cada item incluye: id, nombre, precio_base, stock_cantidad, disponible, eliminado, soft_deleted_at, created_at
- **AND** la respuesta incluye metadata de paginación (total, page, size, pages)

#### Scenario: Admin filtra productos por disponibilidad

- **WHEN** un usuario ADMIN hace `GET /api/v1/admin/productos?disponible=false`
- **THEN** el sistema retorna solo productos con `disponible=false`, incluyendo soft-deleted si los hay

#### Scenario: Admin filtra productos por estado de eliminación

- **WHEN** un usuario ADMIN hace `GET /api/v1/admin/productos?eliminado=true`
- **THEN** el sistema retorna solo productos con `soft_deleted_at IS NOT NULL`

#### Scenario: Admin busca productos por nombre

- **WHEN** un usuario ADMIN hace `GET /api/v1/admin/productos?search=pizza`
- **THEN** el sistema retorna productos cuyo nombre contenga "pizza" (ILIKE), incluyendo soft-deleted

#### Scenario: Usuario sin rol adecuado recibe 403

- **WHEN** un usuario CLIENT hace `GET /api/v1/admin/productos`
- **THEN** el sistema retorna HTTP 403 Forbidden

### Requirement: Admin puede listar todas las categorías incluyendo eliminadas

El sistema SHALL proveer un endpoint `GET /api/v1/admin/categorias` que retorne todas las categorías registradas, incluyendo aquellas con `soft_deleted_at` no nulo. Solo accesible para usuarios con rol ADMIN o STOCK.

#### Scenario: Admin lista todas las categorías

- **WHEN** un usuario ADMIN hace `GET /api/v1/admin/categorias`
- **THEN** el sistema retorna una lista plana de TODAS las categorías (activas y soft-deleted)
- **AND** cada item incluye: id, nombre, parent_id, eliminado, soft_deleted_at, created_at

#### Scenario: Admin filtra categorías por estado de eliminación

- **WHEN** un usuario ADMIN hace `GET /api/v1/admin/categorias?eliminado=true`
- **THEN** el sistema retorna solo categorías con `soft_deleted_at IS NOT NULL`

#### Scenario: Usuario sin rol adecuado recibe 403

- **WHEN** un usuario CLIENT hace `GET /api/v1/admin/categorias`
- **THEN** el sistema retorna HTTP 403 Forbidden

### Requirement: Admin puede listar todos los ingredientes incluyendo eliminados

El sistema SHALL proveer un endpoint `GET /api/v1/admin/ingredientes` que retorne todos los ingredientes registrados, incluyendo aquellos con `soft_deleted_at` no nulo. Solo accesible para usuarios con rol ADMIN o STOCK.

#### Scenario: Admin lista todos los ingredientes

- **WHEN** un usuario ADMIN hace `GET /api/v1/admin/ingredientes?page=1&size=20`
- **THEN** el sistema retorna una lista paginada de TODOS los ingredientes (activos y soft-deleted)
- **AND** cada item incluye: id, nombre, es_alergeno, eliminado, soft_deleted_at, created_at

#### Scenario: Admin filtra ingredientes por alérgeno

- **WHEN** un usuario ADMIN hace `GET /api/v1/admin/ingredientes?es_alergeno=true`
- **THEN** el sistema retorna solo ingredientes con `es_alergeno=true`, incluyendo soft-deleted

#### Scenario: Admin filtra ingredientes por estado de eliminación

- **WHEN** un usuario ADMIN hace `GET /api/v1/admin/ingredientes?eliminado=true`
- **THEN** el sistema retorna solo ingredientes con `soft_deleted_at IS NOT NULL`

### Requirement: Endpoint público de productos acepta query param incluir_eliminados

El sistema SHALL aceptar un query param opcional `incluir_eliminados` en `GET /api/v1/productos` que, cuando es `true` y el usuario autenticado tiene rol ADMIN o STOCK, incluya productos con `soft_deleted_at IS NOT NULL` en los resultados. Si el usuario no es ADMIN/STOCK, el parámetro es ignorado.

#### Scenario: Admin solicita productos incluyendo eliminados

- **WHEN** un usuario ADMIN hace `GET /api/v1/productos?incluir_eliminados=true`
- **THEN** el sistema retorna todos los productos (activos y soft-deleted) en formato `ProductoResponse` (con stock_cantidad)

#### Scenario: Cliente intenta usar incluir_eliminados

- **WHEN** un usuario CLIENT hace `GET /api/v1/productos?incluir_eliminados=true`
- **THEN** el sistema ignora el parámetro y retorna solo productos activos no eliminados en formato `PublicProductoResponse`

#### Scenario: Usuario no autenticado usa incluir_eliminados

- **WHEN** un usuario no autenticado hace `GET /api/v1/productos?incluir_eliminados=true`
- **THEN** el sistema ignora el parámetro y retorna solo productos disponibles no eliminados

### Requirement: Sidebar admin muestra ítem Catálogo para ADMIN y STOCK

El sistema SHALL mostrar un ítem de navegación "Catálogo" en el sidebar del panel admin, con sub-ítems "Productos", "Categorías" e "Ingredientes", únicamente para usuarios con rol ADMIN o STOCK.

#### Scenario: Admin ve menú Catálogo en sidebar

- **WHEN** un usuario ADMIN accede al panel de administración
- **THEN** el sidebar muestra el ítem "Catálogo" expandible con sub-ítems Productos, Categorías, Ingredientes

#### Scenario: Stock ve menú Catálogo en sidebar

- **WHEN** un usuario STOCK accede al panel de administración
- **THEN** el sidebar muestra el ítem "Catálogo" expandible con sub-ítems Productos, Categorías, Ingredientes

#### Scenario: Cliente NO ve menú Catálogo

- **WHEN** un usuario CLIENT accede a cualquier página
- **THEN** el sidebar NO muestra el ítem "Catálogo"

### Requirement: Página admin de productos permite gestionar el catálogo

El sistema SHALL proveer una página `AdminProductosPage` accesible en `/admin/productos` que muestre una tabla de productos con filtros, y permita crear, editar y eliminar productos usando los endpoints existentes.

#### Scenario: Admin ve tabla de productos con columnas completas

- **WHEN** un usuario ADMIN navega a `/admin/productos`
- **THEN** el sistema muestra una tabla con columnas: ID, Nombre, Precio, Stock, Disponible, Eliminado, Acciones
- **AND** los productos eliminados se muestran con estilo atenuado (texto gris, tachado)

#### Scenario: Admin crea un nuevo producto

- **WHEN** un usuario ADMIN completa el formulario de creación y hace submit
- **THEN** el sistema llama a `POST /api/v1/productos` con los datos del formulario
- **AND** la tabla se actualiza mostrando el nuevo producto

#### Scenario: Admin edita un producto existente

- **WHEN** un usuario ADMIN modifica campos en el modal de edición y guarda
- **THEN** el sistema llama a `PUT /api/v1/productos/{id}` con los datos modificados
- **AND** la tabla refleja los cambios

#### Scenario: Admin elimina un producto

- **WHEN** un usuario ADMIN confirma la eliminación de un producto
- **THEN** el sistema llama a `DELETE /api/v1/productos/{id}`
- **AND** el producto aparece como eliminado (soft_deleted_at no nulo) en la tabla

### Requirement: Página admin de categorías permite gestionar categorías

El sistema SHALL proveer una página `AdminCategoriasPage` accesible en `/admin/categorias` que muestre las categorías en estructura jerárquica y permita crear, editar y eliminar categorías.

#### Scenario: Admin ve categorías en estructura jerárquica

- **WHEN** un usuario ADMIN navega a `/admin/categorias`
- **THEN** el sistema muestra las categorías organizadas jerárquicamente (padre → hijas)
- **AND** las categorías eliminadas se muestran con estilo atenuado

#### Scenario: Admin crea una nueva categoría

- **WHEN** un usuario ADMIN completa el formulario de creación con nombre y padre opcional
- **THEN** el sistema llama a `POST /api/v1/categorias` y actualiza la vista

#### Scenario: Admin elimina una categoría sin productos activos

- **WHEN** un usuario ADMIN elimina una categoría sin productos ni hijos activos
- **THEN** el sistema llama a `DELETE /api/v1/categorias/{id}` y la categoría aparece como eliminada

### Requirement: Página admin de ingredientes permite gestionar ingredientes

El sistema SHALL proveer una página `AdminIngredientesPage` accesible en `/admin/ingredientes` que muestre una tabla de ingredientes y permita crear, editar y eliminar ingredientes.

#### Scenario: Admin ve tabla de ingredientes

- **WHEN** un usuario ADMIN navega a `/admin/ingredientes`
- **THEN** el sistema muestra una tabla con columnas: Nombre, Alérgeno, Eliminado, Acciones

#### Scenario: Admin crea un ingrediente con flag de alérgeno

- **WHEN** un usuario ADMIN crea un ingrediente con `es_alergeno=true`
- **THEN** el sistema llama a `POST /api/v1/ingredientes` y el ingrediente aparece con badge de alérgeno
