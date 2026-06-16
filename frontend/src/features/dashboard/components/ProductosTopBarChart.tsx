import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import Card from '../../../shared/components/Card';
import Skeleton from '../../../shared/components/Skeleton';
import EmptyState from '../../../shared/components/EmptyState';
import ErrorDisplay from '../../../shared/components/ErrorDisplay';
import type { MetricsProductoTopItem } from '../../../shared/api/dashboardApi';

interface ProductosTopBarChartProps {
  data: MetricsProductoTopItem[] | undefined;
  isLoading: boolean;
  error?: string;
}

function truncateName(nombre: string, maxLen = 20): string {
  if (nombre.length <= maxLen) return nombre;
  return nombre.slice(0, maxLen) + '...';
}

interface ChartDataItem {
  nombre: string;
  nombreCompleto: string;
  cantidad_vendida: number;
  monto_total: number;
}

export function ProductosTopBarChart({ data, isLoading, error }: ProductosTopBarChartProps) {
  if (error) {
    return (
      <Card>
        <ErrorDisplay message={error} />
      </Card>
    );
  }

  if (isLoading) {
    return (
      <Card>
        <Skeleton variant="card" />
      </Card>
    );
  }

  if (!data || data.length === 0) {
    return (
      <Card>
        <EmptyState
          title="Sin productos vendidos"
          description="Aún no hay ventas registradas en el sistema"
        />
      </Card>
    );
  }

  const chartData: ChartDataItem[] = data.map((item) => ({
    nombre: truncateName(item.nombre),
    nombreCompleto: item.nombre,
    cantidad_vendida: item.cantidad_vendida,
    monto_total: item.monto_total,
  }));

  return (
    <Card>
      <h2 className="mb-4 text-lg font-semibold text-gray-800">Top productos más vendidos</h2>
      <ResponsiveContainer width="100%" height={400}>
        <BarChart
          data={chartData}
          layout="vertical"
          margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis type="number" tick={{ fontSize: 12 }} stroke="#9ca3af" />
          <YAxis
            dataKey="nombre"
            type="category"
            tick={{ fontSize: 12 }}
            stroke="#9ca3af"
            width={140}
          />
          <Tooltip
            formatter={(value, name) => {
              if (name === 'cantidad_vendida') return [value, 'Cantidad'];
              return [`$${Number(value).toFixed(2)}`, 'Monto total'];
            }}
            labelFormatter={(_label, payload) => {
              if (Array.isArray(payload) && payload.length > 0) {
                const entry = payload[0] as unknown as { payload: ChartDataItem };
                return entry.payload.nombreCompleto;
              }
              return '';
            }}
          />
          <Bar dataKey="cantidad_vendida" fill="#22c55e" radius={[0, 4, 4, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </Card>
  );
}

export default ProductosTopBarChart;
