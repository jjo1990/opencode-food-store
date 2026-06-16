import { useQuery } from '@tanstack/react-query';
import {
  fetchAdminCategorias,
  type AdminCategoriaListResponse,
} from '../../../shared/api/adminCatalogApi';

export function useAdminCategorias(eliminado?: boolean) {
  return useQuery<AdminCategoriaListResponse>({
    queryKey: ['admin-categorias', eliminado],
    queryFn: () => fetchAdminCategorias(eliminado),
    placeholderData: (prev) => prev,
  });
}
