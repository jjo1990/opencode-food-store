import { useQuery } from '@tanstack/react-query';
import {
  getPedidos,
  getPedido,
  type PedidoListResponse,
  type PedidoDetailResponse,
  type ItemPedidoResponse,
  type HistorialResponse,
} from '../../shared/api/pedidosApi';
import type { Order, OrderDetail } from './types';

function mapOrder(item: PedidoListResponse): Order {
  return {
    id: item.id,
    estado_codigo: item.estado_codigo,
    subtotal: Number(item.subtotal),
    costo_envio: Number(item.costo_envio),
    total: Number(item.total),
    created_at: item.created_at,
  };
}

function mapOrderDetail(data: PedidoDetailResponse): OrderDetail {
  return {
    id: data.id,
    estado_codigo: data.estado_codigo,
    subtotal: Number(data.subtotal),
    costo_envio: Number(data.costo_envio),
    total: Number(data.total),
    created_at: data.created_at,
    items: (data.items || []).map((i: ItemPedidoResponse) => ({
      id: i.id,
      producto_id: i.producto_id,
      nombre_snapshot: i.nombre_snapshot,
      precio_snapshot: Number(i.precio_snapshot),
      cantidad: i.cantidad,
      subtotal: Number(i.subtotal),
      personalizacion: i.personalizacion,
    })),
    historial: (data.historial || []).map((h: HistorialResponse) => ({
      estado_desde: h.estado_desde,
      estado_nuevo: h.estado_nuevo,
      actor_id: h.actor_id,
      motivo: h.motivo,
      created_at: h.created_at,
    })),
  };
}

export function useOrders(params?: { skip?: number; limit?: number; estado_codigo?: string }) {
  return useQuery<{ items: Order[]; total: number; skip: number; limit: number }>({
    queryKey: ['orders', params],
    queryFn: async () => {
      const result = await getPedidos(params);
      return {
        items: result.items.map(mapOrder),
        total: result.total,
        skip: result.skip,
        limit: result.limit,
      };
    },
    placeholderData: (prev) => prev,
  });
}

export function useOrder(id: string | undefined) {
  return useQuery<OrderDetail>({
    queryKey: ['order', id],
    queryFn: async () => {
      const data = await getPedido(id!);
      return mapOrderDetail(data);
    },
    enabled: !!id,
  });
}
