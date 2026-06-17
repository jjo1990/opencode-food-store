import { useCallback } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { useDashboardStore } from '../../stores/dashboardStore';
import {
  useMetricsResumen,
  useMetricsVentas,
  useMetricsProductosTop,
  useMetricsPedidosPorEstado,
} from '../../features/dashboard/hooks/useDashboardMetrics';
import StatCard from '../../features/dashboard/components/StatCard';
import DashboardFilters from '../../features/dashboard/components/DashboardFilters';
import VentasLineChart from '../../features/dashboard/components/VentasLineChart';
import ProductosTopBarChart from '../../features/dashboard/components/ProductosTopBarChart';
import PedidosEstadoPieChart from '../../features/dashboard/components/PedidosEstadoPieChart';

export function AdminDashboardPage() {
  const filters = useDashboardStore((s) => s.filters);
  const queryClient = useQueryClient();

  const resumen = useMetricsResumen();
  const ventas = useMetricsVentas(filters.fechaInicio, filters.fechaFin, filters.granularidad);
  const productosTop = useMetricsProductosTop();
  const pedidosEstado = useMetricsPedidosPorEstado();

  const handleRefresh = useCallback(() => {
    queryClient.invalidateQueries({ queryKey: ['metrics-'] });
  }, [queryClient]);

  const resumenData = resumen.data;

  const errorMessage = (err: unknown): string => {
    if (err instanceof Error) return err.message;
    return 'Error desconocido';
  };

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100">Dashboard</h1>
          <p className="text-sm text-gray-500 dark:text-gray-400">Métricas y KPIs del sistema</p>
        </div>
        <button
          onClick={handleRefresh}
          className="rounded-lg bg-primary px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-primary-600"
        >
          Actualizar datos
        </button>
      </div>

      <DashboardFilters />

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="Ventas Totales"
          value={resumenData?.total_ventas ?? 0}
          subtitle="Monto acumulado"
          icon="💰"
          isLoading={resumen.isLoading}
          error={resumen.error ? errorMessage(resumen.error) : undefined}
        />
        <StatCard
          title="Pedidos Pendientes"
          value={resumenData?.pedidos_por_estado?.['PENDIENTE'] ?? 0}
          icon="📋"
          isLoading={resumen.isLoading}
          error={resumen.error ? errorMessage(resumen.error) : undefined}
        />
        <StatCard
          title="Usuarios Registrados"
          value={resumenData?.usuarios_registrados ?? 0}
          icon="👥"
          isLoading={resumen.isLoading}
          error={resumen.error ? errorMessage(resumen.error) : undefined}
        />
        <StatCard
          title="Órdenes Entregadas"
          value={resumenData?.pedidos_por_estado?.['ENTREGADO'] ?? 0}
          icon="✅"
          isLoading={resumen.isLoading}
          error={resumen.error ? errorMessage(resumen.error) : undefined}
        />
      </div>

      <div className="mt-8">
        <VentasLineChart
          data={ventas.data?.items}
          isLoading={ventas.isLoading}
          error={ventas.error ? errorMessage(ventas.error) : undefined}
          granularidad={filters.granularidad}
        />
      </div>

      <div className="mt-8 grid grid-cols-1 gap-6 lg:grid-cols-2">
        <PedidosEstadoPieChart
          data={pedidosEstado.data?.items}
          isLoading={pedidosEstado.isLoading}
          error={pedidosEstado.error ? errorMessage(pedidosEstado.error) : undefined}
        />
        <ProductosTopBarChart
          data={productosTop.data?.items}
          isLoading={productosTop.isLoading}
          error={productosTop.error ? errorMessage(productosTop.error) : undefined}
        />
      </div>
    </div>
  );
}

export default AdminDashboardPage;
