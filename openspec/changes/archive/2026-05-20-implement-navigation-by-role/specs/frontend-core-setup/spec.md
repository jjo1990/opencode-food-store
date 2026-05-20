# Spec: frontend-core-setup (Delta)

> Delta spec for navigation-by-role change. Modifies router requirements to include role-based routing and lazy loading.

## MODIFIED Requirements

### Requirement: Router con layout compartido

El sistema SHALL tener un router configurado con React Router v6 con layout compartido (Header/Nav/Footer), rutas definidas por rol, y lazy loading de módulos.

#### Scenario: Router monta layout compartido

- **WHEN** el usuario navega a cualquier ruta
- **THEN** se renderiza el layout compartido con Header (logo, nav links contextuales por rol, auth status) y Footer
- **AND** el contenido de la ruta se renderiza en un `<Outlet />`

#### Scenario: Rutas públicas disponibles sin autenticación

- **WHEN** el usuario navega a `/catalog` o `/catalog/:slug`
- **THEN** se renderiza la página correspondiente
- **AND** no se requiere autenticación

#### Scenario: Rutas admin protegidas por rol ADMIN

- **WHEN** el usuario navega a `/admin`, `/admin/users`, `/admin/products`, `/admin/stock`, `/admin/orders`, `/admin/reports`
- **THEN** el `ProtectedRoute` verifica que el usuario tenga rol ADMIN
- **AND** si no tiene el rol, se redirige a `/catalog`

#### Scenario: Rutas stock protegidas por rol STOCK

- **WHEN** el usuario navega a `/stock/products`, `/stock/categories`, `/stock/manage`
- **THEN** el `ProtectedRoute` verifica que el usuario tenga rol STOCK
- **AND** si no tiene el rol, se redirige a `/catalog`

#### Scenario: Rutas pedidos protegidas por rol PEDIDOS

- **WHEN** el usuario navega a `/orders` o `/orders/reports`
- **THEN** el `ProtectedRoute` verifica que el usuario tenga rol PEDIDOS
- **AND** si no tiene el rol, se redirige a `/catalog`

#### Scenario: Lazy loading de módulos

- **WHEN** el usuario navega a una ruta de admin por primera vez
- **THEN** el chunk de admin se carga dinámicamente con `React.lazy()`
- **AND** se muestra un skeleton loader durante la carga via `Suspense`

#### Scenario: Ruta no encontrada

- **WHEN** el usuario navega a una ruta que no existe
- **THEN** se muestra una página 404 con mensaje y botón para volver al inicio
