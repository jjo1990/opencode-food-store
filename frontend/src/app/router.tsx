import { lazy } from 'react';
import { createBrowserRouter, Outlet } from 'react-router-dom';
import { Header } from '../widgets/Header';
import { Footer } from '../widgets/Footer';
import { ProtectedRoute } from '../features/auth/ProtectedRoute';
import { CatalogPage } from '../pages/CatalogPage';
import { ProductDetailPage } from '../pages/ProductDetailPage';
import { ProfilePage } from '../pages/ProfilePage';
import { AddressesPage } from '../pages/AddressesPage';
import { NotFoundPage } from '../pages/NotFoundPage';

const AdminDashboardPage = lazy(() => import('../pages/admin/AdminDashboardPage'));
const AdminUsersPage = lazy(() => import('../pages/admin/AdminUsersPage'));
const AdminProductsPage = lazy(() => import('../pages/admin/AdminProductsPage'));
const AdminStockPage = lazy(() => import('../pages/admin/AdminStockPage'));
const AdminOrdersPage = lazy(() => import('../pages/admin/AdminOrdersPage'));
const AdminReportsPage = lazy(() => import('../pages/admin/AdminReportsPage'));

const StockProductsPage = lazy(() => import('../pages/stock/StockProductsPage'));
const StockCategoriesPage = lazy(() => import('../pages/stock/StockCategoriesPage'));
const StockManagePage = lazy(() => import('../pages/stock/StockManagePage'));

const OrdersPage = lazy(() => import('../pages/OrdersPage'));
const CheckoutPage = lazy(() => import('../pages/CheckoutPage'));
const PedidosPanelPage = lazy(() => import('../pages/pedidos/PedidosPanelPage'));
const PedidosReportsPage = lazy(() => import('../pages/pedidos/PedidosReportsPage'));

function Layout() {
  return (
    <div className="flex min-h-screen flex-col">
      <Header />
      <main className="flex-1">
        <Outlet />
      </main>
      <Footer />
    </div>
  );
}

export const router = createBrowserRouter([
  {
    element: <Layout />,
    children: [
      { path: '/', element: <CatalogPage /> },
      { path: '/catalog', element: <CatalogPage /> },
      { path: '/catalog/:slug', element: <ProductDetailPage /> },

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
