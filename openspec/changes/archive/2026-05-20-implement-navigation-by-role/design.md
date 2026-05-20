## Context

El frontend tiene componentes de navegación creados en el setup inicial (Phase 0) que no se migraron a Tailwind cuando se configuró en el Change 21. El Header actual (con Tailwind) solo muestra un link fijo a "Catálogo" sin importar el rol. El router no tiene rutas administrativas ni protección por rol.

El ProtectedRoute ya existe y soporta `allowedRoles`. El authStore expone `user.roles` como `string[]`.

## Goals / Non-Goals

**Goals:**

- Header con navegación contextual según el rol del usuario
- Navigation + Sidebar reescritos con Tailwind usando `<Link>` de React Router
- Router con rutas protegidas por rol usando ProtectedRoute
- Lazy loading de páginas por módulo de rol
- Páginas stub para módulos admin, stock, pedidos (contenido mínimo, funcionalidad real se implementa en changes posteriores)
- Usuario no autenticado: solo ve Catálogo + Login/Registrarse

**Non-Goals:**

- Implementar la funcionalidad real de admin/stock/pedidos (son changes separados: Phase 7, etc.)
- Tests unitarios (se agregan en change de testing)
- Breadcrumbs o migas de pan

## Decisions

### 1. Tres componentes de navegación con responsabilidades distintas

**Decisión**: Mantener Header (barra superior), Navigation (nav horizontal principal) y Sidebar (panel lateral colapsable) como componentes separados.

- **Header**: Logo, nav links principales (según rol), auth status (login/register o email+logout). Siempre visible.
- **Navigation**: Nav links horizontales detallados según rol. Visible en desktop, hamburguesa en mobile.
- **Sidebar**: Panel lateral colapsable con navegación completa. Útil para secciones admin con muchas subrutas.

### 2. Lazy loading por módulo de rol con React.lazy

**Decisión**: Las páginas de admin, stock y pedidos se cargan con `React.lazy()` y `Suspense`.
**Por qué**: La app arranca con ~50KB de JS inicial. Si cargamos todas las páginas de admin upfront, el bundle crece innecesariamente para usuarios CLIENT. Con lazy loading, cada módulo se carga solo cuando se navega a él.

### 3. Rutas organizadas por sección en el router

**Decisión**: Las rutas admin van bajo un layout propio con sidebar, igual que stock y pedidos.

```
/catalog          → público
/admin            → ProtectedRoute(roles: ['ADMIN']) + Layout con Sidebar
/admin/users      → ProtectedRoute(roles: ['ADMIN'])
/admin/products   → ProtectedRoute(roles: ['ADMIN', 'STOCK'])
/stock            → ProtectedRoute(roles: ['STOCK']) + Layout propio
/pedidos          → ProtectedRoute(roles: ['PEDIDOS']) + Layout propio
```

### 4. Menú items centralizados en un hook o archivo de config

**Decisión**: Los menú items se definen en un archivo `shared/config/navigation.ts` con la estructura:

```ts
{ label, path, icon, allowedRoles?: string[], section: 'main'|'admin'|'stock'|'pedidos' }
```

**Por qué**: Evita duplicar la definición de items en Header, Navigation y Sidebar. Un solo source of truth.

## Risks / Trade-offs

| Riesgo                                                                                          | Mitigación                                                                                                                            |
| ----------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| **Páginas stub sin funcionalidad real** — el usuario podría pensar que la feature está completa | Dejar claro en el diseño que son placeholders con título + "Próximamente"                                                             |
| **Sidebar duplica funcionalidad del Header/Navigation** — puede confundir al usuario            | Sidebar es colapsable y se usa principalmente en secciones admin para navegación detallada. Header muestra solo los links principales |
| **Lazy loading puede causar flash de loading** si la red es lenta                               | Usar Suspense con skeleton placeholder consistente                                                                                    |
