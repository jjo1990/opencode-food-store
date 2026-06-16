import { useState, useEffect, useCallback } from 'react';
import { Modal } from '../../../shared/components/Modal';
import { Spinner } from '../../../shared/components/Spinner';
import { ErrorDisplay } from '../../../shared/components/ErrorDisplay';
import { type AdminUserUpdateRequest } from '../../../shared/api/adminUsersApi';
import { useAdminUser, useUpdateAdminUser, useDeleteAdminUser } from '../hooks/useAdminUsers';

const ROLES = ['CLIENT', 'STOCK', 'PEDIDOS', 'ADMIN'] as const;

const ROLE_LABELS: Record<string, string> = {
  CLIENT: 'Cliente',
  STOCK: 'Gestor de Stock',
  PEDIDOS: 'Gestor de Pedidos',
  ADMIN: 'Administrador',
};

interface UserEditModalProps {
  userId: string | null;
  isOpen: boolean;
  onClose: () => void;
}

export function UserEditModal({ userId, isOpen, onClose }: UserEditModalProps) {
  const { data: user, isLoading, isError, refetch } = useAdminUser(isOpen ? userId : null);

  const updateMutation = useUpdateAdminUser();
  const deleteMutation = useDeleteAdminUser();

  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [telefono, setTelefono] = useState('');
  const [roles, setRoles] = useState<string[]>([]);
  const [activo, setActivo] = useState(true);
  const [adminRemoveWarning, setAdminRemoveWarning] = useState(false);
  const [adminRemoveConfirmed, setAdminRemoveConfirmed] = useState(false);
  const [showDeactivateConfirm, setShowDeactivateConfirm] = useState(false);

  useEffect(() => {
    if (user) {
      setFullName(user.full_name || '');
      setEmail(user.email);
      setTelefono(user.telefono || '');
      setRoles([...user.roles]);
      setActivo(user.activo);
      setAdminRemoveWarning(false);
      setAdminRemoveConfirmed(false);
      setShowDeactivateConfirm(false);
    }
  }, [user]);

  const hasChanges = useCallback((): boolean => {
    if (!user) return false;
    if (fullName !== (user.full_name || '')) return true;
    if (email !== user.email) return true;
    if (telefono !== (user.telefono || '')) return true;
    if (roles.length !== user.roles.length) return true;
    if (!roles.every((r) => user.roles.includes(r))) return true;
    return false;
  }, [user, fullName, email, telefono, roles]);

  const handleRoleToggle = (role: string) => {
    const hadAdmin = user?.roles.includes('ADMIN');
    const currentlyChecked = roles.includes(role);

    if (role === 'ADMIN' && hadAdmin && currentlyChecked && !adminRemoveConfirmed) {
      setAdminRemoveWarning(true);
      return;
    }

    setRoles((prev) => (prev.includes(role) ? prev.filter((r) => r !== role) : [...prev, role]));
  };

  const handleAdminRemoveConfirm = () => {
    setAdminRemoveConfirmed(true);
    setAdminRemoveWarning(false);
    setRoles((prev) => prev.filter((r) => r !== 'ADMIN'));
  };

  const handleAdminRemoveCancel = () => {
    setAdminRemoveWarning(false);
  };

  const handleSave = async () => {
    if (!userId) return;

    const body: AdminUserUpdateRequest = {};

    if (user && fullName !== (user.full_name || '')) {
      body.full_name = fullName || null;
    }
    if (user && email !== user.email) {
      body.email = email;
    }
    if (user && telefono !== (user.telefono || '')) {
      body.telefono = telefono || null;
    }
    if (user) {
      const originalRoles = [...user.roles].sort().join(',');
      const currentRoles = [...roles].sort().join(',');
      if (originalRoles !== currentRoles) {
        body.roles = roles;
      }
    }

    try {
      await updateMutation.mutateAsync({ id: userId, body });
      onClose();
    } catch {
      // error handled by mutation onError toast
    }
  };

  const handleDeactivate = async () => {
    if (!userId) return;
    try {
      await deleteMutation.mutateAsync(userId);
      setShowDeactivateConfirm(false);
      onClose();
    } catch {
      // error handled by mutation onError toast
    }
  };

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('es-AR', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  const modalTitle = user?.soft_deleted_at ? 'Usuario Eliminado' : 'Editar Usuario';
  const isSoftDeleted = !!user?.soft_deleted_at;

  const renderContent = () => {
    if (isLoading) {
      return (
        <div className="flex justify-center py-12">
          <Spinner size="lg" />
        </div>
      );
    }

    if (isError) {
      return (
        <ErrorDisplay message="Error al cargar los datos del usuario" onRetry={() => refetch()} />
      );
    }

    if (!user) return null;

    if (isSoftDeleted) {
      return (
        <div className="space-y-4">
          <div className="rounded-lg bg-gray-50 p-4 text-center">
            <p className="text-sm text-gray-600">
              Este usuario fue eliminado el {formatDate(user.soft_deleted_at!)}.
            </p>
            <p className="mt-1 text-sm text-gray-500">
              Podés reactivarlo desde la tabla principal.
            </p>
          </div>
        </div>
      );
    }

    return (
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700">Nombre completo</label>
          <input
            type="text"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">Email</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">Teléfono</label>
          <input
            type="text"
            value={telefono}
            onChange={(e) => setTelefono(e.target.value)}
            className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Roles</label>
          <div className="space-y-2">
            {ROLES.map((role) => (
              <label
                key={role}
                className="flex items-center gap-2 rounded-lg border border-gray-200 px-3 py-2 hover:bg-gray-50 cursor-pointer"
              >
                <input
                  type="checkbox"
                  checked={roles.includes(role)}
                  onChange={() => handleRoleToggle(role)}
                  className="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                />
                <span className="text-sm text-gray-700">{ROLE_LABELS[role]}</span>
                <span
                  className={`ml-auto inline-flex rounded-full px-2 py-0.5 text-xs font-medium ${
                    role === 'ADMIN'
                      ? 'bg-red-100 text-red-800'
                      : role === 'STOCK'
                        ? 'bg-blue-100 text-blue-800'
                        : role === 'PEDIDOS'
                          ? 'bg-orange-100 text-orange-800'
                          : 'bg-green-100 text-green-800'
                  }`}
                >
                  {role}
                </span>
              </label>
            ))}
          </div>
        </div>

        {adminRemoveWarning && (
          <div className="rounded-lg border border-amber-300 bg-amber-50 p-4">
            <div className="flex items-start gap-3">
              <svg
                className="h-5 w-5 text-amber-500 mt-0.5 shrink-0"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                />
              </svg>
              <div>
                <p className="text-sm font-medium text-amber-800">
                  ¿Estás seguro? Si quitás el rol ADMIN, este usuario perderá acceso al panel de
                  administración.
                </p>
                <div className="mt-3 flex gap-2">
                  <button
                    type="button"
                    onClick={handleAdminRemoveConfirm}
                    className="rounded-lg bg-amber-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-amber-700"
                  >
                    Confirmar
                  </button>
                  <button
                    type="button"
                    onClick={handleAdminRemoveCancel}
                    className="rounded-lg border border-gray-300 px-3 py-1.5 text-xs font-medium text-gray-700 hover:bg-gray-50"
                  >
                    Cancelar
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        <div className="flex items-center justify-between rounded-lg border border-gray-200 px-3 py-2">
          <span className="text-sm font-medium text-gray-700">Usuario activo</span>
          <button
            type="button"
            onClick={() => setActivo(!activo)}
            className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
              activo ? 'bg-green-500' : 'bg-gray-300'
            }`}
          >
            <span
              className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                activo ? 'translate-x-6' : 'translate-x-1'
              }`}
            />
          </button>
        </div>

        <div className="text-xs text-gray-400">
          <p>ID: {user.id}</p>
          <p>Registrado: {formatDate(user.created_at)}</p>
        </div>
      </div>
    );
  };

  const renderFooter = () => {
    if (isLoading || isError || !user) return null;

    if (isSoftDeleted) {
      return (
        <button
          type="button"
          onClick={onClose}
          className="rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
        >
          Cerrar
        </button>
      );
    }

    return (
      <>
        <button
          type="button"
          onClick={() => setShowDeactivateConfirm(true)}
          className="rounded-lg border border-red-300 px-4 py-2 text-sm font-medium text-red-600 hover:bg-red-50"
        >
          Desactivar usuario
        </button>
        <div className="flex-1" />
        <button
          type="button"
          onClick={onClose}
          className="rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
        >
          Cancelar
        </button>
        <button
          type="button"
          onClick={handleSave}
          disabled={!hasChanges() || updateMutation.isPending || adminRemoveWarning}
          className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {updateMutation.isPending ? 'Guardando...' : 'Guardar cambios'}
        </button>
      </>
    );
  };

  return (
    <>
      <Modal isOpen={isOpen} onClose={onClose} title={modalTitle} footer={renderFooter()}>
        {renderContent()}
      </Modal>

      <Modal
        isOpen={showDeactivateConfirm}
        onClose={() => setShowDeactivateConfirm(false)}
        title="Desactivar usuario"
        footer={
          <>
            <button
              type="button"
              onClick={() => setShowDeactivateConfirm(false)}
              className="rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
            >
              Cancelar
            </button>
            <button
              type="button"
              onClick={handleDeactivate}
              disabled={deleteMutation.isPending}
              className="rounded-lg bg-red-600 px-4 py-2 text-sm font-medium text-white hover:bg-red-700 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {deleteMutation.isPending ? 'Desactivando...' : 'Confirmar'}
            </button>
          </>
        }
      >
        <p className="text-sm text-gray-600">
          ¿Desactivar a <strong>{user?.full_name || user?.email}</strong>? El usuario no podrá
          acceder al sistema pero sus datos se conservarán.
        </p>
      </Modal>
    </>
  );
}

export default UserEditModal;
