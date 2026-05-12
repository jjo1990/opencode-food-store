/**
 * Dashboard Page - Main page after login
 * Following FSD: pages/ directory
 */
import { useAuthStore } from '../stores/authStore';

export function DashboardPage() {
  const user = useAuthStore((state) => state.user);

  const getRoleLabel = (role: string) => {
    const roles: Record<string, string> = {
      CLIENT: 'Cliente',
      ADMIN: 'Administrador',
      STOCK: 'Gestor de Stock',
      PEDIDOS: 'Gestor de Pedidos',
    };
    return roles[role] || role;
  };

  return (
    <div className="dashboard-page">
      <div className="dashboard-header">
        <h1>Bienvenido{a user?.email ? `, ${user.email.split('@')[0]}` : ''}</h1>
        <p>Has iniciado sesión exitosamente</p>
      </div>

      <div className="dashboard-content">
        <div className="user-info-card">
          <h3>Información de tu cuenta</h3>
          <p><strong>Email:</strong> {user?.email}</p>
          <p><strong>Roles:</strong> {user?.roles?.map(getRoleLabel).join(', ')}</p>
        </div>

        <div className="quick-actions">
          <h3>Acciones rápidas</h3>
          <div className="action-buttons">
            {user?.roles?.includes('CLIENT') && (
              <>
                <button className="action-btn">🛒 Ver Catálogo</button>
                <button className="action-btn">📦 Mis Pedidos</button>
                <button className="action-btn">👤 Mi Perfil</button>
              </>
            )}
            {user?.roles?.includes('ADMIN') && (
              <>
                <button className="action-btn">⚙️ Panel de Admin</button>
                <button className="action-btn">👥 Gestionar Usuarios</button>
              </>
            )}
            {user?.roles?.includes('STOCK') && (
              <>
                <button className="action-btn">📦 Gestionar Stock</button>
                <button className="action-btn">🏷️ Categorías</button>
              </>
            )}
            {user?.roles?.includes('PEDIDOS') && (
              <>
                <button className="action-btn">📋 Panel de Pedidos</button>
                <button className="action-btn">📊 Reportes</button>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default DashboardPage;