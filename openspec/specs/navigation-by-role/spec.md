# navigation-by-role Specification

## Purpose

TBD - created by archiving change implement-navigation-by-role. Update Purpose after archive.

## Requirements

### Requirement: Header muestra navegación contextual por rol

El sistema SHALL mostrar en el Header links de navegación que cambian según el rol del usuario autenticado.

#### Scenario: Usuario no autenticado ve links públicos

- **WHEN** el usuario no está autenticado
- **THEN** el Header muestra: logo, link a Catálogo, botón "Iniciar Sesión" y "Registrarse"

#### Scenario: Cliente autenticado ve links de cliente

- **WHEN** el usuario tiene el rol CLIENT
- **THEN** el Header muestra: logo, links a Catálogo, Carrito, Mis Pedidos, Perfil, email del usuario + botón "Cerrar Sesión"

#### Scenario: Admin ve links administrativos

- **WHEN** el usuario tiene el rol ADMIN
- **THEN** el Header muestra: logo, links a Dashboard, Usuarios, Productos, Stock, Pedidos, Reportes, email + "Cerrar Sesión"

#### Scenario: Stock ve links de stock

- **WHEN** el usuario tiene el rol STOCK
- **THEN** el Header muestra: logo, links a Productos, Categorías, Gestionar Stock, email + "Cerrar Sesión"

#### Scenario: Pedidos ve links de pedidos

- **WHEN** el usuario tiene el rol PEDIDOS
- **THEN** el Header muestra: logo, links a Panel de Pedidos, Reportes, email + "Cerrar Sesión"

### Requirement: Menú items centralizados en configuración

El sistema SHALL definir los items de navegación en un único archivo de configuración compartido por Header, Navigation y Sidebar.

#### Scenario: Unica fuente de verdad

- **WHEN** se agrega un nuevo item de navegación
- **THEN** se modifica solo el archivo de configuración
- **AND** Header, Navigation y Sidebar reflejan el nuevo item automáticamente

### Requirement: Sidebar con navegación completa y colapsable

El sistema SHALL proveer un Sidebar colapsable con navegación completa, adaptada al rol del usuario.

#### Scenario: Sidebar expandido

- **WHEN** el sidebar está expandido
- **THEN** muestra: logo, info del usuario (email + roles), navegación completa con íconos, botón "Cerrar Sesión"

#### Scenario: Sidebar colapsado

- **WHEN** el usuario clickea el botón de colapsar
- **THEN** el sidebar se reduce a solo íconos (o se oculta completamente en mobile)
- **AND** el contenido principal ocupa el espacio liberado

### Requirement: Lazy loading de módulos por rol

El sistema SHALL cargar bajo demanda (lazy loading) las páginas de cada módulo de rol usando `React.lazy()` y `Suspense`.

#### Scenario: Usuario CLIENT no carga páginas admin

- **WHEN** un usuario con rol CLIENT navega al catálogo
- **THEN** solo se cargan los chunks de páginas públicas y de cliente
- **AND** el chunk de páginas admin NO está en el bundle inicial

#### Scenario: Admin navega a sección admin por primera vez

- **WHEN** un usuario con rol ADMIN navega a `/admin`
- **THEN** se carga dinámicamente el chunk de páginas admin
- **AND** se muestra un skeleton loader durante la carga

### Requirement: Guards de rutas por rol

El sistema SHALL proteger las rutas del frontend usando `ProtectedRoute` con `allowedRoles` para prevenir navegación directa a URLs no permitidas.

#### Scenario: Usuario sin permiso es redirigido

- **WHEN** un usuario sin rol ADMIN intenta navegar a `/admin`
- **THEN** es redirigido a `/dashboard` (o `/catalog` si no es CLIENT)
- **AND** no ve el contenido de la ruta

#### Scenario: Usuario no autenticado es redirigido al login

- **WHEN** un usuario no autenticado intenta navegar a `/admin`
- **THEN** es redirigido a `/login`
- **AND** después del login exitoso, es redirigido a la URL original

### Requirement: Páginas stub para módulos de rol

El sistema SHALL crear páginas placeholder para los módulos de ADMIN, STOCK y PEDIDOS con título y contenido "Próximamente" hasta que se implemente su funcionalidad real.

#### Scenario: Admin ve página Dashboard

- **WHEN** un ADMIN navega a `/admin`
- **THEN** se muestra la página Dashboard con título y cards placeholder de métricas

#### Scenario: Stock ve página de productos

- **WHEN** un usuario STOCK navega a `/stock/products`
- **THEN** se muestra la página con título "Gestión de Productos" y contenido "Próximamente"

#### Scenario: Pedidos ve panel de pedidos

- **WHEN** un usuario PEDIDOS navega a `/orders`
- **THEN** se muestra el panel con título "Panel de Pedidos" y contenido "Próximamente"
