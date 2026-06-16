import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import {
  fetchAdminOrders,
  fetchAdminOrderDetail,
  changeOrderState,
  type AdminOrdersParams,
  type AdminOrderListResponse,
  type PedidoDetail,
  type AdminChangeStateRequest,
} from '../../../shared/api/adminOrdersApi';

export function useAdminOrders(params: AdminOrdersParams) {
  return useQuery<AdminOrderListResponse>({
    queryKey: ['admin-orders', params],
    queryFn: () => fetchAdminOrders(params),
    placeholderData: (prev) => prev,
    staleTime: 15000,
  });
}

export function useAdminOrderDetail(orderId: string | null) {
  return useQuery<PedidoDetail>({
    queryKey: ['admin-order-detail', orderId],
    queryFn: () => fetchAdminOrderDetail(orderId!),
    enabled: !!orderId,
  });
}

export function useChangeOrderState() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, body }: { id: string; body: AdminChangeStateRequest }) =>
      changeOrderState(id, body),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-orders'] });
      queryClient.invalidateQueries({ queryKey: ['admin-order-detail'] });
      toast.success('Estado del pedido actualizado correctamente');
    },
    onError: (error) => {
      const axiosError = error as { response?: { data?: { detail?: string } } };
      const msg = axiosError?.response?.data?.detail || 'Error al cambiar el estado del pedido';
      toast.error(msg);
    },
  });
}
