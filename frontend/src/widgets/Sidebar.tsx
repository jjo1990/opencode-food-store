import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../stores/authStore';
import { useUIStore } from '../stores/uiStore';
import { getMenuItemsBySection, getSectionLabel } from '../shared/config/navigation';

interface SidebarProps {
  className?: string;
}

export function Sidebar({ className = '' }: SidebarProps) {
  const [collapsed, setCollapsed] = useState(false);
  const { user, logout } = useAuthStore();
  const { setMobileMenuOpen } = useUIStore();
  const navigate = useNavigate();
  const roles = user?.roles || [];
  const sections = getMenuItemsBySection(roles);

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const handleNavClick = () => {
    setMobileMenuOpen(false);
  };

  return (
    <aside
      className={`fixed left-0 top-16 z-30 flex h-[calc(100vh-4rem)] flex-col border-r border-gray-200 bg-white transition-all duration-300 dark:border-gray-700 dark:bg-gray-900 ${
        collapsed ? 'w-16' : 'w-64'
      } ${className}`}
    >
      <button
        onClick={() => setCollapsed(!collapsed)}
        className="flex min-h-[44px] min-w-[44px] items-center justify-end border-b border-gray-100 p-3 text-gray-500 transition-colors hover:text-gray-600 dark:border-gray-800 dark:text-gray-400 dark:hover:text-gray-200"
        aria-label={collapsed ? 'Expandir menú' : 'Colapsar menú'}
      >
        {collapsed ? '→' : '←'}
      </button>

      {!collapsed && (
        <div className="border-b border-gray-100 p-4 dark:border-gray-800">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary-100 text-lg dark:bg-primary-900/30">
              👤
            </div>
            <div className="min-w-0 flex-1">
              <p className="truncate text-sm font-medium text-gray-900 dark:text-gray-100">{user?.email}</p>
              <p className="text-xs text-gray-500 dark:text-gray-400">{roles.join(', ')}</p>
            </div>
          </div>
        </div>
      )}

      <nav className="flex-1 overflow-y-auto p-2">
        {Object.entries(sections).map(([section, items]) => {
          if (section === 'main') return null;
          return (
            <div key={section} className="mb-4">
              {!collapsed && (
                <p className="mb-1 px-3 text-xs font-semibold uppercase tracking-wider text-gray-400 dark:text-gray-500">
                  {getSectionLabel(section)}
                </p>
              )}
              {items.map((item) => (
                <Link
                  key={item.path}
                  to={item.path}
                  onClick={handleNavClick}
                  className="flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-gray-700 transition-colors hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700"
                >
                  <span className="text-lg">{item.icon}</span>
                  {!collapsed && <span>{item.label}</span>}
                </Link>
              ))}
            </div>
          );
        })}
      </nav>

      <div className="border-t border-gray-200 p-2 dark:border-gray-700">
        <button
          onClick={handleLogout}
          className="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-red-600 transition-colors hover:bg-red-50 dark:text-red-400 dark:hover:bg-red-900/20"
        >
          <span className="text-lg">🚪</span>
          {!collapsed && <span>Cerrar Sesión</span>}
        </button>
      </div>
    </aside>
  );
}

export default Sidebar;
