import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { getProfile, updateProfile, changePassword } from '../../shared/api/usuariosApi';
import type {
  UserProfileResponse,
  ProfileUpdateRequest,
  PasswordChangeRequest,
} from '../../shared/api/usuariosApi';
import type { UserProfile } from './types';

function mapProfile(data: UserProfileResponse): UserProfile {
  return {
    id: data.id,
    email: data.email,
    full_name: data.full_name,
    telefono: data.telefono,
    roles: data.roles,
    created_at: data.created_at,
  };
}

export function useProfile() {
  return useQuery<UserProfile>({
    queryKey: ['profile'],
    queryFn: async () => {
      const data = await getProfile();
      return mapProfile(data);
    },
  });
}

export function useUpdateProfile() {
  const queryClient = useQueryClient();
  return useMutation<UserProfile, Error, ProfileUpdateRequest>({
    mutationFn: async (payload) => {
      const data = await updateProfile(payload);
      return mapProfile(data);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['profile'] });
      toast.success('Perfil actualizado correctamente');
    },
    onError: (error) => {
      toast.error(error.message || 'Error al actualizar perfil');
    },
  });
}

export function useChangePassword() {
  return useMutation<{ mensaje: string }, Error, PasswordChangeRequest>({
    mutationFn: changePassword,
    onSuccess: () => {
      toast.success('Contraseña actualizada correctamente');
    },
    onError: (error) => {
      toast.error(error.message || 'Error al cambiar contraseña');
    },
  });
}
