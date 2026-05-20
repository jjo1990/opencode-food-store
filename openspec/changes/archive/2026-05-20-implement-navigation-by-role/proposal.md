## Why

El frontend ya tiene componentes de navegación (Header, Navigation, Sidebar) y protección de rutas (ProtectedRoute), pero están incompletos y con código legacy:

- `Navigation.tsx` y `Sidebar.tsx` usan clases CSS que no existen (no Tailwind)
- El `Header.tsx` solo muestra "Catálogo" sin importar el rol del usuario
- El router no tiene rutas protegidas por rol ni lazy loading
- No existen las páginas para ADMIN, STOCK, PEDIDOS

Sin este change, los usuarios no pueden navegar según su rol, y las rutas administrativas no tienen protección frontend.

## What Changes

1. **Header.tsx**: Agregar navegación por roles (CLIENT ve Catálogo/Carrito/Pedidos/Perfil, ADMIN ve links de admin, etc.)
2. **Navigation.tsx**: Reescribir con Tailwind + `<Link>` de React Router (reemplazar `<a>` + CSS legacy)
3. **Sidebar.tsx**: Reescribir con Tailwind + `<Link>` + menú completo por rol
4. **Router**: Agregar rutas protegidas con `ProtectedRoute` + `allowedRoles` para ADMIN, STOCK, PEDIDOS
5. **Lazy loading**: Las páginas de cada rol se cargan con `React.lazy()` para no inflar el bundle inicial
6. **Páginas placeholder**: Crear páginas stub para admin (Dashboard, Users, Products, Stock, Orders), stock (Products, Categories, Manage), pedidos (Panel, Reports)

## Capabilities

### New Capabilities

- `navigation-by-role`: Sistema de navegación que renderiza opciones según los roles del usuario autenticado, con lazy loading de módulos y guards de rutas

### Modified Capabilities

- `frontend-core-setup`: El router se actualiza para incluir rutas protegidas por rol, lazy loading de módulos, y organización por secciones (admin, stock, pedidos)

## Impact

- **Archivos a modificar**: `widgets/Header.tsx`, `widgets/Navigation.tsx`, `widgets/Sidebar.tsx`, `app/router.tsx`
- **Archivos nuevos**: `pages/admin/` (Dashboard, Users, Products, Stock, Orders pages), `pages/stock/` (Products, Categories, Manage pages), `pages/pedidos/` (Panel, Reports pages)
- **Sin cambios en backend**: es puramente frontend
