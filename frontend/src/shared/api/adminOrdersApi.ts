import client from './client';

export interface AdminOrderListItem {
  id: string;
  cliente_nombre: string | null;
  usuario_id: string;
  estado_codigo: string;
  total: number;
  created_at: string;
  direccion_calle: string | null;
}

export interface AdminOrderListResponse {
  items: AdminOrderListItem[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface DetallePedidoRead {
  id: string;
  producto_id: string;
  nombre_snapshot: string;
  precio_snapshot: string;
  cantidad: number;
  subtotal: string;
  personalizacion: string[] | null;
}

export interface HistorialRead {
  estado_desde: string | null;
  estado_nuevo: string;
  actor_id: string | null;
  motivo: string | null;
  created_at: string;
}

export interface PedidoDetail {
  id: string;
  estado_codigo: string;
  subtotal: string;
  costo_envio: string;
  total: string;
  created_at: string;
  cliente_nombre: string | null;
  usuario_id: string;
  direccion_calle: string | null;
  items: DetallePedidoRead[];
  historial: HistorialRead[];
}

export interface AdminChangeStateRequest {
  nuevo_estado: string;
  motivo?: string | null;
}

export interface AdminOrdersParams {
  page?: number;
  size?: number;
  estado_codigo?: string;
  fecha_inicio?: string;
  fecha_fin?: string;
  usuario_id?: string;
  monto_min?: number;
  monto_max?: number;
  search?: string;
}

export async function fetchAdminOrders(
  params: AdminOrdersParams = {}
): Promise<AdminOrderListResponse> {
  const queryParams: Record<string, string | number> = {};
  if (params.page) queryParams.page = params.page;
  if (params.size) queryParams.size = params.size;
  if (params.estado_codigo) queryParams.estado_codigo = params.estado_codigo;
  if (params.fecha_inicio) queryParams.fecha_inicio = params.fecha_inicio;
  if (params.fecha_fin) queryParams.fecha_fin = params.fecha_fin;
  if (params.usuario_id) queryParams.usuario_id = params.usuario_id;
  if (params.monto_min !== undefined) queryParams.monto_min = params.monto_min;
  if (params.monto_max !== undefined) queryParams.monto_max = params.monto_max;
  if (params.search) queryParams.search = params.search;

  const response = await client.get<AdminOrderListResponse>('/admin/pedidos', {
    params: queryParams,
  });
  return response.data;
}

export async function fetchAdminOrderDetail(id: string): Promise<PedidoDetail> {
  const response = await client.get<PedidoDetail>(`/admin/pedidos/${id}`);
  return response.data;
}

export async function changeOrderState(
  id: string,
  body: AdminChangeStateRequest
): Promise<{ id: string; estado_codigo: string; total: string }> {
  const response = await client.patch<{ id: string; estado_codigo: string; total: string }>(
    `/admin/pedidos/${id}/estado`,
    body
  );
  return response.data;
}
