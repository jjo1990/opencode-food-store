import client from './client';

export interface MetricsResumenResponse {
  total_ventas: number;
  cantidad_pedidos: number;
  pedidos_por_estado: Record<string, number>;
  usuarios_registrados: number;
}

export interface MetricsVentasItem {
  fecha: string;
  monto_total: number;
  cantidad_pedidos: number;
}

export interface MetricsVentasResponse {
  items: MetricsVentasItem[];
}

export interface MetricsProductoTopItem {
  producto_id: string;
  nombre: string;
  cantidad_vendida: number;
  monto_total: number;
}

export interface MetricsProductosTopResponse {
  items: MetricsProductoTopItem[];
}

export interface MetricsPedidosEstadoItem {
  estado: string;
  cantidad: number;
  porcentaje: number;
}

export interface MetricsPedidosEstadoResponse {
  items: MetricsPedidosEstadoItem[];
}

export interface MetricsVentasParams {
  fecha_inicio: string;
  fecha_fin: string;
  granularidad: 'day' | 'week' | 'month';
}

export async function fetchDashboardResumen(): Promise<MetricsResumenResponse> {
  const response = await client.get<MetricsResumenResponse>('/admin/metricas/resumen');
  return response.data;
}

export async function fetchDashboardVentas(
  params: MetricsVentasParams
): Promise<MetricsVentasResponse> {
  const response = await client.get<MetricsVentasResponse>('/admin/metricas/ventas', { params });
  return response.data;
}

export async function fetchDashboardProductosTop(): Promise<MetricsProductosTopResponse> {
  const response = await client.get<MetricsProductosTopResponse>('/admin/metricas/productos-top');
  return response.data;
}

export async function fetchDashboardPedidosEstado(): Promise<MetricsPedidosEstadoResponse> {
  const response = await client.get<MetricsPedidosEstadoResponse>(
    '/admin/metricas/pedidos-por-estado'
  );
  return response.data;
}
