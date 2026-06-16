import { useQuery } from '@tanstack/react-query';
import {
  fetchDashboardResumen,
  fetchDashboardVentas,
  fetchDashboardProductosTop,
  fetchDashboardPedidosEstado,
  type MetricsResumenResponse,
  type MetricsVentasResponse,
  type MetricsProductosTopResponse,
  type MetricsPedidosEstadoResponse,
} from '../../../shared/api/dashboardApi';

export function useMetricsResumen() {
  return useQuery<MetricsResumenResponse>({
    queryKey: ['metrics-resumen'],
    queryFn: fetchDashboardResumen,
    staleTime: 30000,
  });
}

export function useMetricsVentas(
  fechaInicio: string,
  fechaFin: string,
  granularidad: 'day' | 'week' | 'month'
) {
  return useQuery<MetricsVentasResponse>({
    queryKey: ['metrics-ventas', fechaInicio, fechaFin, granularidad],
    queryFn: () =>
      fetchDashboardVentas({ fecha_inicio: fechaInicio, fecha_fin: fechaFin, granularidad }),
    staleTime: 30000,
    enabled: !!fechaInicio && !!fechaFin,
  });
}

export function useMetricsProductosTop() {
  return useQuery<MetricsProductosTopResponse>({
    queryKey: ['metrics-productos-top'],
    queryFn: fetchDashboardProductosTop,
    staleTime: 30000,
  });
}

export function useMetricsPedidosPorEstado() {
  return useQuery<MetricsPedidosEstadoResponse>({
    queryKey: ['metrics-pedidos-estado'],
    queryFn: fetchDashboardPedidosEstado,
    staleTime: 30000,
  });
}
