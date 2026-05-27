import client from './client';

export interface ItemPedidoResponse {
  id: string;
  producto_id: string;
  nombre_snapshot: string;
  precio_snapshot: string;
  cantidad: number;
  subtotal: string;
  personalizacion: string[] | null;
}

export interface HistorialResponse {
  estado_desde: string | null;
  estado_nuevo: string;
  actor_id: string | null;
  motivo: string | null;
  created_at: string;
}

export interface PedidoListResponse {
  id: string;
  estado_codigo: string;
  subtotal: string;
  costo_envio: string;
  total: string;
  created_at: string;
}

export interface PedidoDetailResponse extends PedidoListResponse {
  items: ItemPedidoResponse[];
  historial: HistorialResponse[];
}

export interface PedidoListResult {
  items: PedidoListResponse[];
  total: number;
  skip: number;
  limit: number;
}

export async function getPedidos(params?: {
  skip?: number;
  limit?: number;
  estado_codigo?: string;
}): Promise<PedidoListResult> {
  const { data } = await client.get('/pedidos', { params });
  return data;
}

export async function getPedido(id: string): Promise<PedidoDetailResponse> {
  const { data } = await client.get(`/pedidos/${id}`);
  return data;
}
