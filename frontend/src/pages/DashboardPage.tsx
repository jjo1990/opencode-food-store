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
    <main className="px-4 py-8 sm:px-6 lg:px-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900 lg:text-3xl dark:text-gray-100">
          Bienvenido{user?.email ? `, ${user.email.split('@')[0]}` : ''}
        </h1>
        <p className="mt-1 text-gray-500 dark:text-gray-400">Has iniciado sesion exitosamente</p>
      </div>

      <section aria-labelledby="account-info" className="mb-8">
        <h2 id="account-info" className="sr-only">Informacion de cuenta</h2>
        <div className="rounded-xl bg-white p-6 shadow-md dark:bg-gray-800 dark:shadow-gray-900/30">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">Informacion de tu cuenta</h3>
          <div className="mt-4 space-y-2 text-sm text-gray-600 dark:text-gray-300">
            <p>
              <strong>Email:</strong> {user?.email}
            </p>
            <p>
              <strong>Roles:</strong> {user?.roles?.map(getRoleLabel).join(', ')}
            </p>
          </div>
        </div>
      </section>

      <section aria-labelledby="quick-actions-heading">
        <h2 id="quick-actions-heading" className="text-lg font-semibold text-gray-900 dark:text-gray-100">Acciones rapidas</h2>
        <div className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {user?.roles?.includes('CLIENT') && (
            <>
              <button className="rounded-xl bg-white p-6 text-left shadow-md transition-shadow hover:shadow-lg dark:bg-gray-800 dark:shadow-gray-900/30">
                <span className="text-2xl">🛒</span>
                <p className="mt-2 font-medium text-gray-900 dark:text-gray-100">Ver Catalogo</p>
              </button>
              <button className="rounded-xl bg-white p-6 text-left shadow-md transition-shadow hover:shadow-lg dark:bg-gray-800 dark:shadow-gray-900/30">
                <span className="text-2xl">📦</span>
                <p className="mt-2 font-medium text-gray-900 dark:text-gray-100">Mis Pedidos</p>
              </button>
              <button className="rounded-xl bg-white p-6 text-left shadow-md transition-shadow hover:shadow-lg dark:bg-gray-800 dark:shadow-gray-900/30">
                <span className="text-2xl">👤</span>
                <p className="mt-2 font-medium text-gray-900 dark:text-gray-100">Mi Perfil</p>
              </button>
            </>
          )}
          {user?.roles?.includes('ADMIN') && (
            <>
              <button className="rounded-xl bg-white p-6 text-left shadow-md transition-shadow hover:shadow-lg dark:bg-gray-800 dark:shadow-gray-900/30">
                <span className="text-2xl">⚙️</span>
                <p className="mt-2 font-medium text-gray-900 dark:text-gray-100">Panel de Admin</p>
              </button>
              <button className="rounded-xl bg-white p-6 text-left shadow-md transition-shadow hover:shadow-lg dark:bg-gray-800 dark:shadow-gray-900/30">
                <span className="text-2xl">👥</span>
                <p className="mt-2 font-medium text-gray-900 dark:text-gray-100">Gestionar Usuarios</p>
              </button>
            </>
          )}
          {user?.roles?.includes('STOCK') && (
            <>
              <button className="rounded-xl bg-white p-6 text-left shadow-md transition-shadow hover:shadow-lg dark:bg-gray-800 dark:shadow-gray-900/30">
                <span className="text-2xl">📦</span>
                <p className="mt-2 font-medium text-gray-900 dark:text-gray-100">Gestionar Stock</p>
              </button>
              <button className="rounded-xl bg-white p-6 text-left shadow-md transition-shadow hover:shadow-lg dark:bg-gray-800 dark:shadow-gray-900/30">
                <span className="text-2xl">🏷️</span>
                <p className="mt-2 font-medium text-gray-900 dark:text-gray-100">Categorias</p>
              </button>
            </>
          )}
          {user?.roles?.includes('PEDIDOS') && (
            <>
              <button className="rounded-xl bg-white p-6 text-left shadow-md transition-shadow hover:shadow-lg dark:bg-gray-800 dark:shadow-gray-900/30">
                <span className="text-2xl">📋</span>
                <p className="mt-2 font-medium text-gray-900 dark:text-gray-100">Panel de Pedidos</p>
              </button>
              <button className="rounded-xl bg-white p-6 text-left shadow-md transition-shadow hover:shadow-lg dark:bg-gray-800 dark:shadow-gray-900/30">
                <span className="text-2xl">📊</span>
                <p className="mt-2 font-medium text-gray-900 dark:text-gray-100">Reportes</p>
              </button>
            </>
          )}
        </div>
      </section>
    </main>
  );
}

export default DashboardPage;
