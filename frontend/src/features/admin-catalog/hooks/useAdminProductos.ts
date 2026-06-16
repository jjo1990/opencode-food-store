import { useQuery } from '@tanstack/react-query';
import {
  fetchAdminProductos,
  type AdminProductosParams,
  type AdminProductoListResponse,
} from '../../../shared/api/adminCatalogApi';

export function useAdminProductos(params: AdminProductosParams) {
  return useQuery<AdminProductoListResponse>({
    queryKey: ['admin-productos', params],
    queryFn: () => fetchAdminProductos(params),
    placeholderData: (prev) => prev,
  });
}
