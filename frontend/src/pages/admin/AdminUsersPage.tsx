import { useState, useEffect, useRef } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import {
  useAdminUsers,
  useDeleteAdminUser,
  useReactivateAdminUser,
} from '../../features/admin-users/hooks/useAdminUsers';
import { UserEditModal } from '../../features/admin-users/components/UserEditModal';
import { Modal } from '../../shared/components/Modal';
import { ErrorDisplay } from '../../shared/components/ErrorDisplay';
import { EmptyState } from '../../shared/components/EmptyState';
import { Skeleton } from '../../shared/components/Skeleton';
import type { AdminUserResponse } from '../../shared/api/adminUsersApi';

const ROLE_BADGE: Record<string, string> = {
  ADMIN: 'bg-red-100 text-red-800',
  STOCK: 'bg-blue-100 text-blue-800',
  PEDIDOS: 'bg-orange-100 text-orange-800',
  CLIENT: 'bg-green-100 text-green-800',
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
          <span
            key={role}
            className={`inline-flex rounded-full px-2 py-0.5 text-xs font-medium ${ROLE_BADGE[role] || 'bg-gray-100 text-gray-800'}`}
          >
            {role}
          </span>
        ))}
      </div>
    );
  };

  const renderStatusBadge = (user: AdminUserResponse) => {
    if (user.soft_deleted_at) {
      return (
        <span className="inline-flex rounded-full bg-gray-100 px-2 py-0.5 text-xs font-medium text-gray-600">
          Eliminado
        </span>
      );
    }
    if (user.activo) {
      return (
        <span className="inline-flex rounded-full bg-green-100 px-2 py-0.5 text-xs font-medium text-green-800">
          Activo
        </span>
      );
    }
    return (
      <span className="inline-flex rounded-full bg-red-100 px-2 py-0.5 text-xs font-medium text-red-800">
        Inactivo
      </span>
    );
  };

  const renderContent = () => {
    if (isLoading) {
      return (
        <div className="overflow-x-auto rounded-lg border border-gray-200">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium uppercase text-gray-500">
                  ID
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium uppercase text-gray-500">
                  Nombre
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium uppercase text-gray-500">
                  Email
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium uppercase text-gray-500">
                  Roles
                </th>
                <th className="px-4 py-3 text-center text-xs font-medium uppercase text-gray-500">
                  Estado
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium uppercase text-gray-500">
                  Fecha
                </th>
                <th className="px-4 py-3 text-center text-xs font-medium uppercase text-gray-500">
                  Acciones
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 bg-white">
              {Array.from({ length: 8 }).map((_, i) => (
                <tr key={i}>
                  <td className="px-4 py-3">
                    <Skeleton width="80px" height="16px" />
                  </td>
                  <td className="px-4 py-3">
                    <Skeleton width="140px" height="16px" />
                  </td>
                  <td className="px-4 py-3">
                    <Skeleton width="180px" height="16px" />
                  </td>
                  <td className="px-4 py-3">
                    <Skeleton width="120px" height="16px" />
                  </td>
                  <td className="px-4 py-3">
                    <Skeleton width="60px" height="16px" />
                  </td>
                  <td className="px-4 py-3">
                    <Skeleton width="100px" height="16px" />
                  </td>
                  <td className="px-4 py-3">
                    <Skeleton width="60px" height="16px" />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      );
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
        <div className="overflow-x-auto rounded-lg border border-gray-200">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium uppercase text-gray-500">
                  ID
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium uppercase text-gray-500">
                  Nombre
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium uppercase text-gray-500">
                  Email
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium uppercase text-gray-500">
                  Roles
                </th>
                <th className="px-4 py-3 text-center text-xs font-medium uppercase text-gray-500">
                  Estado
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium uppercase text-gray-500">
                  Fecha
                </th>
                <th className="px-4 py-3 text-center text-xs font-medium uppercase text-gray-500">
                  Acciones
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 bg-white">
              {data.items.map((user) => (
                <tr
                  key={user.id}
                  onClick={() => handleRowClick(user)}
                  className={
                    user.soft_deleted_at
                      ? 'bg-gray-50 text-gray-400 cursor-pointer'
                      : 'cursor-pointer hover:bg-gray-50 transition-colors'
                  }
                >
                  <td className="px-4 py-3 text-sm font-mono">{truncateUUID(user.id)}</td>
                  <td className="px-4 py-3 text-sm">
                    <span
                      className={
                        user.soft_deleted_at ? 'line-through' : 'font-medium text-gray-900'
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
                          className="rounded-lg p-1.5 text-gray-500 hover:bg-gray-100 hover:text-gray-700 transition-colors"
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
          <p className="text-sm text-gray-500">
            Mostrando {(page - 1) * PAGE_SIZE + 1}–{Math.min(page * PAGE_SIZE, data.total)} de{' '}
            {data.total}
          </p>
          <div className="flex gap-2">
            <button
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page <= 1}
              className="rounded-lg border border-gray-300 px-3 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-50"
            >
              Anterior
            </button>
            <button
              onClick={() => setPage((p) => p + 1)}
              disabled={page >= data.pages}
              className="rounded-lg border border-gray-300 px-3 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-50"
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
        <h1 className="text-3xl font-bold text-gray-900">Gestión de Usuarios</h1>
        <p className="mt-2 text-sm text-gray-500">Administración de usuarios, roles y permisos.</p>
      </div>

      <div className="mb-6 flex flex-wrap gap-3">
        <input
          type="text"
          placeholder="Buscar por nombre o email..."
          value={localSearch}
          onChange={(e) => setLocalSearch(e.target.value)}
          className="rounded-lg border border-gray-300 px-4 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
        />
        <select
          value={rol}
          onChange={(e) => handleFilterChange(setRol, e.target.value)}
          className="rounded-lg border border-gray-300 px-4 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
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
          className="rounded-lg border border-gray-300 px-4 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
        >
          <option value="activo">Activos</option>
          <option value="inactivo">Inactivos</option>
          <option value="todos">Todos</option>
        </select>
      </div>

      {renderContent()}

      <UserEditModal userId={selectedUserId} isOpen={showEditModal} onClose={handleEditClose} />

      <Modal
        isOpen={!!deactivateUser}
        onClose={() => setDeactivateUser(null)}
        title="Desactivar usuario"
        footer={
          <>
            <button
              type="button"
              onClick={() => setDeactivateUser(null)}
              className="rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
            >
              Cancelar
            </button>
            <button
              type="button"
              onClick={handleDeactivateConfirm}
              disabled={deleteMutation.isPending}
              className="rounded-lg bg-red-600 px-4 py-2 text-sm font-medium text-white hover:bg-red-700 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {deleteMutation.isPending ? 'Desactivando...' : 'Confirmar'}
            </button>
          </>
        }
      >
        <p className="text-sm text-gray-600">
          ¿Desactivar a <strong>{deactivateUser?.full_name || deactivateUser?.email}</strong>? El
          usuario no podrá acceder al sistema pero sus datos se conservarán.
        </p>
      </Modal>

      <Modal
        isOpen={!!reactivateUser}
        onClose={() => setReactivateUser(null)}
        title="Reactivar usuario"
        footer={
          <>
            <button
              type="button"
              onClick={() => setReactivateUser(null)}
              className="rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
            >
              Cancelar
            </button>
            <button
              type="button"
              onClick={handleReactivateConfirm}
              disabled={reactivateMutation.isPending}
              className="rounded-lg bg-green-600 px-4 py-2 text-sm font-medium text-white hover:bg-green-700 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {reactivateMutation.isPending ? 'Reactivando...' : 'Confirmar'}
            </button>
          </>
        }
      >
        <p className="text-sm text-gray-600">
          ¿Reactivar a <strong>{reactivateUser?.full_name || reactivateUser?.email}</strong>? El
          usuario recuperará el acceso al sistema.
        </p>
      </Modal>
    </div>
  );
}

export default AdminUsersPage;
