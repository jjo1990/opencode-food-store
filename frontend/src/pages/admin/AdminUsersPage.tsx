import { useState, useEffect, useRef } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import {
  useAdminUsers,
  useDeleteAdminUser,
  useReactivateAdminUser,
} from '../../features/admin-users/hooks/useAdminUsers';
import { UserEditModal } from '../../features/admin-users/components/UserEditModal';
import { Badge } from '../../shared/components/Badge';
import { ConfirmationModal } from '../../shared/components/ConfirmationModal';
import { ErrorDisplay } from '../../shared/components/ErrorDisplay';
import { EmptyState } from '../../shared/components/EmptyState';
import { SkeletonTable } from '../../shared/components/SkeletonTable';
import type { AdminUserResponse } from '../../shared/api/adminUsersApi';

const ROLE_VARIANT: Record<string, 'error' | 'info' | 'warning' | 'success'> = {
  ADMIN: 'error',
  STOCK: 'info',
  PEDIDOS: 'warning',
  CLIENT: 'success',
};

const PAGE_SIZE = 20;

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString('es-AR', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
}

function truncateUUID(id: string) {
  return id.slice(0, 8) + '...';
}

export function AdminUsersPage() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [localSearch, setLocalSearch] = useState('');
  const [rol, setRol] = useState('');
  const [estado, setEstado] = useState('activo');
  const [selectedUserId, setSelectedUserId] = useState<string | null>(null);
  const [showEditModal, setShowEditModal] = useState(false);
  const [deactivateUser, setDeactivateUser] = useState<AdminUserResponse | null>(null);
  const [reactivateUser, setReactivateUser] = useState<AdminUserResponse | null>(null);

  const queryClient = useQueryClient();
  const deleteMutation = useDeleteAdminUser();
  const reactivateMutation = useReactivateAdminUser();
  const debounceRef = useRef<ReturnType<typeof setTimeout>>();

  useEffect(() => {
    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => {
      setSearch(localSearch);
      setPage(1);
    }, 300);
    return () => {
      if (debounceRef.current) clearTimeout(debounceRef.current);
    };
  }, [localSearch]);

  const params = {
    page,
    size: PAGE_SIZE,
    ...(search && { search }),
    ...(rol && { rol }),
    ...(estado !== 'todos' && { estado }),
  };

  const { data, isLoading, isError, error, refetch } = useAdminUsers(params);

  const handleRowClick = (user: AdminUserResponse) => {
    if (user.soft_deleted_at) {
      setReactivateUser(user);
    } else {
      setSelectedUserId(user.id);
      setShowEditModal(true);
    }
  };

  const handleEditClick = (e: React.MouseEvent, user: AdminUserResponse) => {
    e.stopPropagation();
    setSelectedUserId(user.id);
    setShowEditModal(true);
  };

  const handleDeactivateClick = (e: React.MouseEvent, user: AdminUserResponse) => {
    e.stopPropagation();
    setDeactivateUser(user);
  };

  const handleReactivateClick = (e: React.MouseEvent, user: AdminUserResponse) => {
    e.stopPropagation();
    setReactivateUser(user);
  };

  const handleDeactivateConfirm = async () => {
    if (!deactivateUser) return;
    try {
      await deleteMutation.mutateAsync(deactivateUser.id);
      setDeactivateUser(null);
    } catch {
      // error handled by mutation
    }
  };

  const handleReactivateConfirm = async () => {
    if (!reactivateUser) return;
    try {
      await reactivateMutation.mutateAsync(reactivateUser.id);
      setReactivateUser(null);
    } catch {
      // error handled by mutation
    }
  };

  const handleEditClose = () => {
    setShowEditModal(false);
    setSelectedUserId(null);
    queryClient.invalidateQueries({ queryKey: ['admin-users'] });
  };

  const handleFilterChange = (setter: (v: string) => void, value: string) => {
    setter(value);
    setPage(1);
  };

  const renderRoleBadges = (roles: string[]) => {
    return (
      <div className="flex flex-wrap gap-1">
        {roles.map((role) => (
          <Badge key={role} variant={ROLE_VARIANT[role] || 'neutral'} size="sm">
            {role}
          </Badge>
        ))}
      </div>
    );
  };

  const renderStatusBadge = (user: AdminUserResponse) => {
    if (user.soft_deleted_at) {
      return (
        <Badge variant="neutral" size="sm">
          Eliminado
        </Badge>
      );
    }
    if (user.activo) {
      return (
        <Badge variant="success" size="sm">
          Activo
        </Badge>
      );
    }
    return (
      <Badge variant="error" size="sm">
        Inactivo
      </Badge>
    );
  };

  const renderContent = () => {
    if (isLoading) {
      return <SkeletonTable rows={8} columns={7} />;
    }

    if (isError) {
      return (
        <ErrorDisplay
          message={(error as Error)?.message || 'Error al cargar usuarios'}
          onRetry={() => refetch()}
        />
      );
    }

    if (!data || data.items.length === 0) {
      const hasFilters = search || rol || estado !== 'todos';
      return (
        <EmptyState
          title={hasFilters ? 'Sin resultados' : 'No hay usuarios registrados'}
          description={
            hasFilters
              ? 'No se encontraron usuarios con esos filtros.'
              : 'Aún no hay usuarios en el sistema.'
          }
        />
      );
    }

    return (
      <>
        <div className="overflow-x-auto rounded-lg border border-gray-200 dark:border-gray-700">
          <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead className="bg-gray-50 dark:bg-gray-800">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium uppercase text-gray-500 dark:text-gray-400">
                  ID
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium uppercase text-gray-500 dark:text-gray-400">
                  Nombre
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium uppercase text-gray-500 dark:text-gray-400">
                  Email
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium uppercase text-gray-500 dark:text-gray-400">
                  Roles
                </th>
                <th className="px-4 py-3 text-center text-xs font-medium uppercase text-gray-500 dark:text-gray-400">
                  Estado
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium uppercase text-gray-500 dark:text-gray-400">
                  Fecha
                </th>
                <th className="px-4 py-3 text-center text-xs font-medium uppercase text-gray-500 dark:text-gray-400">
                  Acciones
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 dark:divide-gray-700 bg-white dark:bg-gray-900">
              {data.items.map((user) => (
                <tr
                  key={user.id}
                  onClick={() => handleRowClick(user)}
                  className={
                    user.soft_deleted_at
                      ? 'bg-gray-50 dark:bg-gray-800 text-gray-500 dark:text-gray-400 cursor-pointer'
                      : 'cursor-pointer hover:bg-gray-50 dark:bg-gray-800 transition-colors'
                  }
                >
                  <td className="px-4 py-3 text-sm font-mono">{truncateUUID(user.id)}</td>
                  <td className="px-4 py-3 text-sm">
                    <span
                      className={
                        user.soft_deleted_at ? 'line-through' : 'font-medium text-gray-900 dark:text-gray-100'
                      }
                    >
                      {user.full_name || user.email}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-sm">{user.email}</td>
                  <td className="px-4 py-3">{renderRoleBadges(user.roles)}</td>
                  <td className="px-4 py-3 text-center">{renderStatusBadge(user)}</td>
                  <td className="px-4 py-3 text-sm whitespace-nowrap">
                    {formatDate(user.created_at)}
                  </td>
                  <td className="px-4 py-3 text-center">
                    <div className="flex items-center justify-center gap-1">
                      {!user.soft_deleted_at && (
                        <button
                          onClick={(e) => handleEditClick(e, user)}
                          className="rounded-lg p-1.5 text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:bg-gray-700 hover:text-gray-700 dark:text-gray-300 transition-colors"
                          title="Editar usuario"
                        >
                          <svg
                            className="h-4 w-4"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                          >
                            <path
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              strokeWidth={2}
                              d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
                            />
                          </svg>
                        </button>
                      )}
                      {user.soft_deleted_at ? (
                        <button
                          onClick={(e) => handleReactivateClick(e, user)}
                          className="rounded-lg px-2 py-1 text-xs font-medium text-green-600 hover:bg-green-50 transition-colors"
                        >
                          Reactivar
                        </button>
                      ) : (
                        <button
                          onClick={(e) => handleDeactivateClick(e, user)}
                          className="rounded-lg px-2 py-1 text-xs font-medium text-red-600 hover:bg-red-50 transition-colors"
                        >
                          Desactivar
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="mt-4 flex items-center justify-between">
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Mostrando {(page - 1) * PAGE_SIZE + 1}–{Math.min(page * PAGE_SIZE, data.total)} de{' '}
            {data.total}
          </p>
          <div className="flex gap-2">
            <button
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page <= 1}
              className="rounded-lg border border-gray-300 px-3 py-1.5 text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:bg-gray-800 disabled:cursor-not-allowed disabled:opacity-50"
            >
              Anterior
            </button>
            <button
              onClick={() => setPage((p) => p + 1)}
              disabled={page >= data.pages}
              className="rounded-lg border border-gray-300 px-3 py-1.5 text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:bg-gray-800 disabled:cursor-not-allowed disabled:opacity-50"
            >
              Siguiente
            </button>
          </div>
        </div>
      </>
    );
  };

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100">Gestión de Usuarios</h1>
        <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">Administración de usuarios, roles y permisos.</p>
      </div>

      <div className="mb-6 flex flex-wrap gap-3">
        <input
          type="text"
          placeholder="Buscar por nombre o email..."
          value={localSearch}
          onChange={(e) => setLocalSearch(e.target.value)}
          className="rounded-lg border border-gray-300 px-4 py-2 text-sm focus-visible:border-indigo-500 focus:outline-none focus-visible:ring-1 focus-visible:ring-indigo-500"
        />
        <select
          value={rol}
          onChange={(e) => handleFilterChange(setRol, e.target.value)}
          className="rounded-lg border border-gray-300 px-4 py-2 text-sm focus-visible:border-indigo-500 focus:outline-none focus-visible:ring-1 focus-visible:ring-indigo-500"
        >
          <option value="">Todos los roles</option>
          <option value="ADMIN">ADMIN</option>
          <option value="STOCK">STOCK</option>
          <option value="PEDIDOS">PEDIDOS</option>
          <option value="CLIENT">CLIENT</option>
        </select>
        <select
          value={estado}
          onChange={(e) => handleFilterChange(setEstado, e.target.value)}
          className="rounded-lg border border-gray-300 px-4 py-2 text-sm focus-visible:border-indigo-500 focus:outline-none focus-visible:ring-1 focus-visible:ring-indigo-500"
        >
          <option value="activo">Activos</option>
          <option value="inactivo">Inactivos</option>
          <option value="todos">Todos</option>
        </select>
      </div>

      {renderContent()}

      <UserEditModal userId={selectedUserId} isOpen={showEditModal} onClose={handleEditClose} />

      <ConfirmationModal
        isOpen={!!deactivateUser}
        onClose={() => setDeactivateUser(null)}
        onConfirm={handleDeactivateConfirm}
        title="Desactivar usuario"
        message={`¿Desactivar a ${deactivateUser?.full_name || deactivateUser?.email}? El usuario no podrá acceder al sistema pero sus datos se conservarán.`}
        variant="danger"
        confirmLabel="Desactivar"
        isLoading={deleteMutation.isPending}
      />

      <ConfirmationModal
        isOpen={!!reactivateUser}
        onClose={() => setReactivateUser(null)}
        onConfirm={handleReactivateConfirm}
        title="Reactivar usuario"
        message={`¿Reactivar a ${reactivateUser?.full_name || reactivateUser?.email}? El usuario recuperará el acceso al sistema.`}
        variant="info"
        confirmLabel="Reactivar"
        isLoading={reactivateMutation.isPending}
      />
    </div>
  );
}

export default AdminUsersPage;
