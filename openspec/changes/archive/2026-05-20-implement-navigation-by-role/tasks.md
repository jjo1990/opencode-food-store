# Tasks: implement-navigation-by-role

## 1. Navigation Config & Infrastructure

- [x] 1.1 Create `shared/config/navigation.ts` with centralized menu items: all routes grouped by section (main, admin, stock, pedidos) with label, path, icon, allowedRoles, and a `getMenuItemsByRole(roles)` function
- [x] 1.2 Create `pages/admin/` page stubs: `AdminDashboardPage.tsx`, `AdminUsersPage.tsx`, `AdminProductsPage.tsx`, `AdminStockPage.tsx`, `AdminOrdersPage.tsx`, `AdminReportsPage.tsx` — each with title and placeholder content
- [x] 1.3 Create `pages/stock/` page stubs: `StockProductsPage.tsx`, `StockCategoriesPage.tsx`, `StockManagePage.tsx`
- [x] 1.4 Create `pages/pedidos/` page stubs: `PedidosPanelPage.tsx`, `PedidosReportsPage.tsx`

## 2. Header with Role-Based Navigation

- [x] 2.1 Update `widgets/Header.tsx` to use centralized navigation config — render different nav links based on user roles (CLIENT, ADMIN, STOCK, PEDIDOS), keep auth status (login/register or email+logout), use Tailwind classes, use `<Link>` from react-router-dom

## 3. Navigation Component with Tailwind

- [x] 3.1 Rewrite `widgets/Navigation.tsx` — replace `<a>` with `<Link>`, replace CSS classes with Tailwind, use centralized navigation config via `getMenuItemsByRole()`, responsive (horizontal desktop, hamburger mobile)

## 4. Sidebar with Tailwind + Full Role Menu

- [x] 4.1 Rewrite `widgets/Sidebar.tsx` — use Tailwind, `<Link>` instead of `<a>`, collapsible state, show all nav items based on roles from centralized config, show user info (email + roles), logout button, responsive behavior

## 5. Router with Role-Based Routes + Lazy Loading

- [x] 5.1 Update `app/router.tsx` — add routes for admin (Dashboard, Users, Products, Stock, Orders, Reports), stock (Products, Categories, Manage), pedidos (Panel, Reports), each wrapped in ProtectedRoute with allowedRoles
- [x] 5.2 Implement lazy loading: wrap all admin/stock/pedidos page imports with `React.lazy()` and add `Suspense` with skeleton fallback in the router
- [x] 5.3 Add `<Suspense>` wrapper in Layout for lazy-loaded routes
