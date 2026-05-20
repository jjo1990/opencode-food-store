# catalog-frontend Specification

## Purpose

TBD - created by archiving change implement-catalog-frontend-ui. Update Purpose after archive.

## Requirements

### Requirement: ProductGrid muestra productos en grilla responsive

El sistema SHALL mostrar una grilla de productos que se adapte a 1 columna en mobile, 2 en tablet, y 3-4 en desktop.

#### Scenario: Usuario ve grilla con productos disponibles

- **WHEN** el usuario navega a `/catalog`
- **THEN** se muestran los productos en una grilla responsive
- **AND** cada card muestra: imagen placeholder, nombre, precio formateado, badge "Disponible"/"Agotado"

#### Scenario: No hay productos disponibles

- **WHEN** no hay productos que coincidan con los filtros actuales
- **THEN** se muestra un mensaje "No se encontraron productos" con icono
- **AND** se muestra un botón "Limpiar filtros" si hay filtros activos

#### Scenario: Error al cargar productos

- **WHEN** la API responde con error (500, timeout, red caída)
- **THEN** se muestra un mensaje de error con descripción
- **AND** se muestra un botón "Reintentar" que refetch la query

### Requirement: CategoryNav navega jerarquía de categorías

El sistema SHALL mostrar un árbol de categorías jerárquico (sidebar o panel lateral) que permite filtrar productos por categoría.

#### Scenario: Usuario navega árbol de categorías

- **WHEN** el usuario carga el catálogo
- **THEN** se muestra el árbol de categorías colapsado en el primer nivel
- **AND** al clickear una categoría padre, se expanden/colapsan sus hijas

#### Scenario: Usuario filtra por categoría

- **WHEN** el usuario clickea una categoría hoja (sin hijas)
- **THEN** la grilla se actualiza mostrando solo productos de esa categoría
- **AND** la categoría seleccionada se marca visualmente como activa

#### Scenario: Usuario limpia filtro de categoría

- **WHEN** el usuario clickea "Todas las categorías" o deselecciona la categoría activa
- **THEN** la grilla muestra todos los productos sin filtro de categoría

### Requirement: Filtros combinados afectan la grilla

El sistema SHALL permitir filtrar productos por: búsqueda textual (nombre), rango de precio (mínimo y máximo), y categoría. Los filtros SHALL combinarse (AND).

#### Scenario: Usuario busca por nombre

- **WHEN** el usuario escribe en el campo de búsqueda
- **THEN** después de 300ms de inactividad (debounce), la grilla se actualiza con productos cuyo nombre contenga el texto
- **AND** el query param `search` se agrega a la URL

#### Scenario: Usuario filtra por rango de precio

- **WHEN** el usuario ajusta los sliders de precio mínimo y/o máximo
- **THEN** la grilla se actualiza mostrando solo productos dentro del rango
- **AND** los query params `precio_min` y `precio_max` se agregan a la URL

#### Scenario: Filtros combinados

- **WHEN** el usuario tiene búsqueda "pizza", categoría "Pizzas", y precio entre 500-2000
- **THEN** la API recibe `?search=pizza&categoria_id=X&precio_min=500&precio_max=2000`
- **AND** la grilla muestra solo productos que cumplen TODAS las condiciones

#### Scenario: Usuario limpia todos los filtros

- **WHEN** el usuario clickea "Limpiar filtros"
- **THEN** todos los filtros vuelven a su valor por defecto
- **AND** la grilla recarga sin filtros
- **AND** los query params se limpian de la URL

### Requirement: Paginación server-side con controles

El sistema SHALL paginar los resultados del lado del servidor, con controles de navegación en el frontend.

#### Scenario: Usuario navega entre páginas

- **WHEN** hay más productos que los que entran en una página (page_size=12)
- **THEN** se muestran controles de paginación (anterior, siguiente, números de página)
- **AND** al clickear "Siguiente" o un número de página, la grilla carga esa página

#### Scenario: Paginación se sincroniza con URL

- **WHEN** el usuario cambia de página
- **THEN** el query param `page` se actualiza en la URL
- **AND** al compartir la URL, al abrirla se carga la página correcta

#### Scenario: Primera y última página

- **WHEN** el usuario está en la página 1
- **THEN** el botón "Anterior" está deshabilitado
- **WHEN** el usuario está en la última página
- **THEN** el botón "Siguiente" está deshabilitado

### Requirement: Skeleton loaders durante carga

El sistema SHALL mostrar skeleton loaders mientras se fetchan los datos del catálogo.

#### Scenario: Carga inicial de productos

- **WHEN** el usuario navega a `/catalog` y los datos aún no se cargaron
- **THEN** se muestran skeleton cards (misma estructura que las cards reales) con animación de pulse
- **AND** el número de skeletons es igual a `page_size` (12)

#### Scenario: Refetch por cambio de filtros

- **WHEN** el usuario cambia un filtro y la query se refetch
- **THEN** la grilla muestra los skeletons mientras se cargan los nuevos resultados
- **AND** los skeletons reemplazan el contenido anterior

### Requirement: ProductDetail muestra información completa del producto

El sistema SHALL mostrar una página de detalle de producto en `/catalog/:slug` con toda la información.

#### Scenario: Usuario ve detalle de producto

- **WHEN** el usuario clickea un producto en la grilla o navega a `/catalog/:slug`
- **THEN** se muestra: imagen grande, nombre, precio, descripción, lista de ingredientes
- **AND** los ingredientes marcados como alérgenos se muestran resaltados (color de advertencia)
- **AND** se muestra badge "Disponible"/"Agotado"

#### Scenario: Producto no encontrado

- **WHEN** el usuario navega a `/catalog/:slug` con un slug inexistente
- **THEN** se muestra mensaje "Producto no encontrado"
- **AND** un botón para volver al catálogo

#### Scenario: Detalle en estado de carga

- **WHEN** el usuario navega al detalle de un producto y los datos aún se cargan
- **THEN** se muestra un skeleton específico para la página de detalle
