import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import {
  fetchAdminUsers,
  fetchAdminUser,
  updateAdminUser,
  deleteAdminUser,
  reactivateAdminUser,
  type AdminUsersParams,
  type AdminUserListResponse,
  type AdminUserResponse,
  type AdminUserUpdateRequest,
} from '../../../shared/api/adminUsersApi';

export function useAdminUsers(params: AdminUsersParams) {
  return useQuery<AdminUserListResponse>({
    queryKey: ['admin-users', params],
    queryFn: () => fetchAdminUsers(params),
    placeholderData: (prev) => prev,
  });
}

export function useAdminUser(userId: string | null) {
  return useQuery<AdminUserResponse>({
    queryKey: ['admin-user', userId],
    queryFn: () => fetchAdminUser(userId!),
    enabled: !!userId,
  });
}

export function useUpdateAdminUser() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, body }: { id: string; body: AdminUserUpdateRequest }) =>
      updateAdminUser(id, body),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: ['admin-users'] });
      queryClient.invalidateQueries({ queryKey: ['admin-user', variables.id] });
      toast.success('Usuario actualizado correctamente');
    },
    onError: () => {
      toast.error('Error al actualizar usuario');
    },
  });
}

export function useDeleteAdminUser() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => deleteAdminUser(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-users'] });
      toast.success('Usuario desactivado correctamente');
    },
    onError: () => {
      toast.error('Error al desactivar usuario');
    },
  });
}

export function useReactivateAdminUser() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => reactivateAdminUser(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-users'] });
      toast.success('Usuario reactivado correctamente');
    },
    onError: () => {
      toast.error('Error al reactivar usuario');
    },
  });
}
