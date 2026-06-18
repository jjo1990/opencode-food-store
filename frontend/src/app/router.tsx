import { lazy } from 'react';
import { createBrowserRouter, Outlet } from 'react-router-dom';
import { Header } from '../widgets/Header';
import { Footer } from '../widgets/Footer';
import { Sidebar } from '../widgets/Sidebar';
import { MobileDrawer } from '../shared/components/MobileDrawer';
import { PageTransition } from '../shared/components/PageTransition';
import { ProtectedRoute } from '../features/auth/ProtectedRoute';
import { useUIStore } from '../stores/uiStore';
import { CatalogPage } from '../pages/CatalogPage';
import { ProductDetailPage } from '../pages/ProductDetailPage';
import { ProfilePage } from '../pages/ProfilePage';
import { AddressesPage } from '../pages/AddressesPage';
import { NotFoundPage } from '../pages/NotFoundPage';
import LoginPage from '../pages/LoginPage';
import RegisterPage from '../pages/RegisterPage';
import { DashboardPage } from '../pages/DashboardPage';

const AdminDashboardPage = lazy(() => import('../pages/admin/AdminDashboardPage'));
const AdminUsersPage = lazy(() => import('../pages/admin/AdminUsersPage'));
const AdminProductsPage = lazy(() => import('../pages/admin/AdminProductsPage'));
const AdminStockPage = lazy(() => import('../pages/admin/AdminStockPage'));
const AdminOrdersPage = lazy(() => import('../pages/admin/AdminOrdersPage'));
const AdminReportsPage = lazy(() => import('../pages/admin/AdminReportsPage'));
const AdminProductosPage = lazy(() => import('../pages/admin/AdminProductosPage'));
const AdminCategoriasPage = lazy(() => import('../pages/admin/AdminCategoriasPage'));
const AdminIngredientesPage = lazy(() => import('../pages/admin/AdminIngredientesPage'));
const AdminConfigPage = lazy(() => import('../pages/admin/AdminConfigPage'));

const StockProductsPage = lazy(() => import('../pages/stock/StockProductsPage'));
const StockCategoriesPage = lazy(() => import('../pages/stock/StockCategoriesPage'));
const StockManagePage = lazy(() => import('../pages/stock/StockManagePage'));

const OrdersPage = lazy(() => import('../pages/OrdersPage'));
const CheckoutPage = lazy(() => import('../pages/CheckoutPage'));
const PedidosPanelPage = lazy(() => import('../pages/pedidos/PedidosPanelPage'));
const PedidosReportsPage = lazy(() => import('../pages/pedidos/PedidosReportsPage'));

function Layout() {
  const { mobileMenuOpen, setMobileMenuOpen } = useUIStore();

  return (
    <div className="flex min-h-screen flex-col">
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:fixed focus:left-4 focus:top-4 focus:z-[100] focus:rounded-lg focus:bg-primary focus:px-4 focus:py-2 focus:text-white focus:shadow-lg"
      >
        Saltar al contenido
      </a>
      <Header />
      <div className="flex flex-1">
        <Sidebar className="hidden lg:block" />
        <MobileDrawer isOpen={mobileMenuOpen} onClose={() => setMobileMenuOpen(false)}>
          <Sidebar className="w-64" />
        </MobileDrawer>
        <main id="main-content" className="flex-1 overflow-auto" tabIndex={-1}>
          <PageTransition>
            <Outlet />
          </PageTransition>
        </main>
      </div>
      <Footer />
    </div>
  );
}

export const router = createBrowserRouter([
  {
    path: '/login',
    element: <LoginPage />,
  },
  {
    path: '/register',
    element: <RegisterPage />,
  },
  {
    element: <Layout />,
    children: [
      { path: '/', element: <CatalogPage /> },
      { path: '/dashboard', element: <DashboardPage /> },
      { path: '/catalog', element: <CatalogPage /> },
      { path: '/catalog/:id', element: <ProductDetailPage /> },

      {
        path: '/admin',
        element: (
          <ProtectedRoute allowedRoles={['ADMIN']}>
            <AdminDashboardPage />
          </ProtectedRoute>
        ),
      },
      {
        path: '/admin/users',
        element: (
          <ProtectedRoute allowedRoles={['ADMIN']}>
            <AdminUsersPage />
          </ProtectedRoute>
        ),
      },
      {
        path: '/admin/products',
        element: (
          <ProtectedRoute allowedRoles={['ADMIN', 'STOCK']}>
            <AdminProductsPage />
          </ProtectedRoute>
        ),
      },
      {
        path: '/admin/stock',
        element: (
          <ProtectedRoute allowedRoles={['ADMIN']}>
            <AdminStockPage />
          </ProtectedRoute>
        ),
      },
      {
        path: '/admin/orders',
        element: (
          <ProtectedRoute allowedRoles={['ADMIN', 'PEDIDOS']}>
            <AdminOrdersPage />
          </ProtectedRoute>
        ),
      },
      {
        path: '/admin/reports',
        element: (
          <ProtectedRoute allowedRoles={['ADMIN']}>
            <AdminReportsPage />
          </ProtectedRoute>
        ),
      },
      {
        path: '/admin/productos',
        element: (
          <ProtectedRoute allowedRoles={['ADMIN', 'STOCK']}>
            <AdminProductosPage />
          </ProtectedRoute>
        ),
      },
      {
        path: '/admin/categorias',
        element: (
          <ProtectedRoute allowedRoles={['ADMIN', 'STOCK']}>
            <AdminCategoriasPage />
          </ProtectedRoute>
        ),
      },
      {
        path: '/admin/ingredientes',
        element: (
          <ProtectedRoute allowedRoles={['ADMIN', 'STOCK']}>
            <AdminIngredientesPage />
          </ProtectedRoute>
        ),
      },
      {
        path: '/admin/configuracion',
        element: (
          <ProtectedRoute allowedRoles={['ADMIN']}>
            <AdminConfigPage />
          </ProtectedRoute>
        ),
      },

      {
        path: '/stock/products',
        element: (
          <ProtectedRoute allowedRoles={['STOCK']}>
            <StockProductsPage />
          </ProtectedRoute>
        ),
      },
      {
        path: '/stock/categories',
        element: (
          <ProtectedRoute allowedRoles={['STOCK']}>
            <StockCategoriesPage />
          </ProtectedRoute>
        ),
      },
      {
        path: '/stock/manage',
        element: (
          <ProtectedRoute allowedRoles={['STOCK']}>
            <StockManagePage />
          </ProtectedRoute>
        ),
      },

      {
        path: '/pedidos',
        element: (
          <ProtectedRoute allowedRoles={['PEDIDOS']}>
            <PedidosPanelPage />
          </ProtectedRoute>
        ),
      },
      {
        path: '/pedidos/reports',
        element: (
          <ProtectedRoute allowedRoles={['PEDIDOS']}>
            <PedidosReportsPage />
          </ProtectedRoute>
        ),
      },

      {
        path: '/checkout',
        element: (
          <ProtectedRoute allowedRoles={['CLIENT']}>
            <CheckoutPage />
          </ProtectedRoute>
        ),
      },
      {
        path: '/orders',
        element: (
          <ProtectedRoute allowedRoles={['CLIENT']}>
            <OrdersPage />
          </ProtectedRoute>
        ),
      },
      {
        path: '/profile',
        element: (
          <ProtectedRoute allowedRoles={['CLIENT']}>
            <ProfilePage />
          </ProtectedRoute>
        ),
      },
      {
        path: '/addresses',
        element: (
          <ProtectedRoute allowedRoles={['CLIENT']}>
            <AddressesPage />
          </ProtectedRoute>
        ),
      },

      { path: '*', element: <NotFoundPage /> },
    ],
  },
]);
