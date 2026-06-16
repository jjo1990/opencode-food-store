import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import {
  fetchConfig,
  updateConfig,
  SystemConfigUpdateRequest,
} from '../../../shared/api/adminConfigApi';

export function useAdminConfig() {
  return useQuery({
    queryKey: ['admin', 'configuracion'],
    queryFn: fetchConfig,
  });
}

export function useUpdateConfig() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: SystemConfigUpdateRequest) => updateConfig(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin', 'configuracion'] });
      toast.success('Configuración guardada correctamente');
    },
    onError: () => {
      toast.error('Error al guardar la configuración');
    },
  });
}
