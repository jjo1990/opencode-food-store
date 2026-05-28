import { useMutation, useQuery } from '@tanstack/react-query';
import { postCrearPago, postReintentarPago, getPagoByPedido } from '../../shared/api/pagosApi';
import type {
  CrearPagoRequest,
  PagoResponse,
  PagoHistoryResponse,
} from '../../shared/api/pagosApi';

export function useCreatePayment() {
  return useMutation<PagoResponse, Error, CrearPagoRequest>({
    mutationFn: (data) => postCrearPago(data),
  });
}

export function useRetryPayment() {
  return useMutation<PagoResponse, Error, CrearPagoRequest>({
    mutationFn: (data) => postReintentarPago(data),
  });
}

export function usePaymentStatus(pedidoId: string | null, enabled: boolean) {
  return useQuery<PagoHistoryResponse>({
    queryKey: ['payment-status', pedidoId],
    queryFn: () => getPagoByPedido(pedidoId!),
    enabled: enabled && !!pedidoId,
    refetchInterval: (query) => {
      const data = query.state.data;
      if (!data || data.pagos.length === 0) return 5000;
      const lastStatus = data.pagos[0].mp_status;
      return lastStatus === 'pending' ? 5000 : false;
    },
  });
}
