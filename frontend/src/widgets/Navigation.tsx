/**
 * Navigation - Main navigation component with role-based menu items
 * Following FSD: widgets/ directory
 */
import { useAuthStore } from '../stores/authStore';
import { useNavigate } from 'react-router-dom';

export function Navigation() {
  const user = useAuthStore((state) => state.user);
  const logout = useAuthStore((state) => state.logout);
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const getMenuItems = () => {
    const roles = user?.roles || [];

    if (roles.includes('ADMIN')) {
      return [
        { label: 'Dashboard', path: '/admin', icon: '📊' },
        { label: 'Usuarios', path: '/admin/users', icon: '👥' },
        { label: 'Catálogo', path: '/admin/products', icon: '🏪' },
        { label: 'Stock', path: '/admin/stock', icon: '📦' },
        { label: 'Pedidos', path: '/admin/orders', icon: '📋' },
        { label: 'Reportes', path: '/admin/reports', icon: '📈' },
      ];
    }

    if (roles.includes('STOCK')) {
      return [
        { label: 'Productos', path: '/stock/products', icon: '🏪' },
        { label: 'Categorías', path: '/stock/categories', icon: '🏷️' },
        { label: 'Gestionar Stock', path: '/stock/manage', icon: '📦' },
      ];
    }

    if (roles.includes('PEDIDOS')) {
      return [
        { label: 'Panel de Pedidos', path: '/orders', icon: '📋' },
        { label: 'Reportes', path: '/orders/reports', icon: '📈' },
      ];
    }

    // CLIENT
    return [
      { label: 'Catálogo', path: '/catalog', icon: '🏪' },
      { label: 'Mi Carrito', path: '/cart', icon: '🛒' },
      { label: 'Mis Pedidos', path: '/orders', icon: '📦' },
      { label: 'Perfil', path: '/profile', icon: '👤' },
    ];
  };

  return (
    <nav className="main-navigation">
      <div className="nav-brand">
        <span>🍔</span> Food Store
      </div>
      <div className="nav-menu">
        {getMenuItems().map((item) => (
          <a key={item.path} href={item.path} className="nav-item">
            {item.icon} {item.label}
          </a>
        ))}
      </div>
      <div className="nav-user">
        <span>{user?.email}</span>
        <button onClick={handleLogout}>Cerrar Sesión</button>
      </div>
    </nav>
  );
}

export default Navigation;