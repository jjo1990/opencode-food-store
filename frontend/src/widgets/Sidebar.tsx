/**
 * Sidebar - Collapsible side panel with navigation
 * Following FSD: widgets/ directory
 */
import { useState } from 'react';
import { useAuthStore } from '../stores/authStore';
import { useNavigate } from 'react-router-dom';

export function Sidebar() {
  const [collapsed, setCollapsed] = useState(false);
  const user = useAuthStore((state) => state.user);
  const logout = useAuthStore((state) => state.logout);
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <aside className={`sidebar ${collapsed ? 'collapsed' : ''}`}>
      <button className="toggle-btn" onClick={() => setCollapsed(!collapsed)}>
        {collapsed ? '→' : '←'}
      </button>

      {!collapsed && (
        <>
          <div className="sidebar-header">
            <span className="sidebar-icon">🍔</span>
            <span className="sidebar-title">Food Store</span>
          </div>

          <div className="sidebar-user">
            <div className="user-avatar">👤</div>
            <div className="user-details">
              <span className="user-email">{user?.email}</span>
              <span className="user-roles">{user?.roles?.join(', ')}</span>
            </div>
          </div>

          <nav className="sidebar-nav">
            <a href="/dashboard" className="sidebar-link">
              📊 Dashboard
            </a>
            <a href="/catalog" className="sidebar-link">
              🏪 Catálogo
            </a>
            <a href="/cart" className="sidebar-link">
              🛒 Carrito
            </a>
            {user?.roles?.includes('ADMIN') && (
              <>
                <hr className="nav-divider" />
                <span className="nav-section">Admin</span>
                <a href="/admin/users" className="sidebar-link">
                  👥 Usuarios
                </a>
                <a href="/admin/products" className="sidebar-link">
                  🏪 Productos
                </a>
                <a href="/admin/orders" className="sidebar-link">
                  📋 Pedidos
                </a>
              </>
            )}
          </nav>

          <div className="sidebar-footer">
            <button onClick={handleLogout} className="logout-btn">
              🚪 Cerrar Sesión
            </button>
          </div>
        </>
      )}
    </aside>
  );
}

export default Sidebar;