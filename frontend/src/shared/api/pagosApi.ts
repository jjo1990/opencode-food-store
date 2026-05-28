import client from './client';

export interface CrearPagoRequest {
  pedido_id: string;
  card_token: string;
}

export interface PagoResponse {
  mp_payment_id: string | null;
  status: string;
  status_detail: string | null;
}

export interface PagoHistoryItem {
  mp_payment_id: string | null;
  mp_status: string;
  status_detail: string | null;
  created_at: string;
}

export interface PagoHistoryResponse {
  pagos: PagoHistoryItem[];
}

export async function postCrearPago(data: CrearPagoRequest): Promise<PagoResponse> {
  const { data: response } = await client.post('/pagos/crear', data);
  return response;
}

export async function postReintentarPago(data: CrearPagoRequest): Promise<PagoResponse> {
  const { data: response } = await client.post('/pagos/reintentar', data);
  return response;
}

export async function getPagoByPedido(pedidoId: string): Promise<PagoHistoryResponse> {
  const { data } = await client.get(`/pagos/${pedidoId}`);
  return data;
}
