import { useQuery } from '@tanstack/react-query';
import {
  fetchAdminIngredientes,
  type AdminIngredientesParams,
  type AdminIngredienteListResponse,
} from '../../../shared/api/adminCatalogApi';

export function useAdminIngredientes(params: AdminIngredientesParams) {
  return useQuery<AdminIngredienteListResponse>({
    queryKey: ['admin-ingredientes', params],
    queryFn: () => fetchAdminIngredientes(params),
    placeholderData: (prev) => prev,
  });
}
