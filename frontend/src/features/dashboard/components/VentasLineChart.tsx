import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import Card from '../../../shared/components/Card';
import Skeleton from '../../../shared/components/Skeleton';
import EmptyState from '../../../shared/components/EmptyState';
import ErrorDisplay from '../../../shared/components/ErrorDisplay';
import type { MetricsVentasItem } from '../../../shared/api/dashboardApi';

interface VentasLineChartProps {
  data: MetricsVentasItem[] | undefined;
  isLoading: boolean;
  error?: string;
  granularidad: 'day' | 'week' | 'month';
}

function formatFecha(fecha: string, granularidad: 'day' | 'week' | 'month'): string {
  if (granularidad === 'week') return fecha;
  if (granularidad === 'month') return fecha;
  try {
    const parts = fecha.split('-');
    return `${parts[2]}/${parts[1]}`;
  } catch {
    return fecha;
  }
}

function formatCurrency(value: number): string {
  return `$${value.toLocaleString('es-AR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

export function VentasLineChart({ data, isLoading, error, granularidad }: VentasLineChartProps) {
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
          title="Sin datos de ventas"
          description="No hay ventas registradas en el período seleccionado"
        />
      </Card>
    );
  }

  return (
    <Card>
      <h2 className="mb-4 text-lg font-semibold text-gray-800">Ventas en el tiempo</h2>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis
            dataKey="fecha"
            tickFormatter={(v: string) => formatFecha(v, granularidad)}
            tick={{ fontSize: 12 }}
            stroke="#9ca3af"
          />
          <YAxis
            yAxisId="left"
            tickFormatter={(v: number) => formatCurrency(v)}
            tick={{ fontSize: 12 }}
            stroke="#9ca3af"
          />
          <YAxis
            yAxisId="right"
            orientation="right"
            tickFormatter={(v: number) => v.toString()}
            tick={{ fontSize: 12 }}
            stroke="#9ca3af"
          />
          <Tooltip
            formatter={(value, name) => {
              if (name === 'monto_total') return [formatCurrency(Number(value)), 'Ventas ($)'];
              return [value, 'Pedidos'];
            }}
            labelFormatter={(label) => formatFecha(String(label), granularidad)}
          />
          <Legend />
          <Line
            yAxisId="left"
            type="monotone"
            dataKey="monto_total"
            name="Ventas ($)"
            stroke="#16a34a"
            strokeWidth={2}
            dot={{ r: 3 }}
            activeDot={{ r: 5 }}
          />
          <Line
            yAxisId="right"
            type="monotone"
            dataKey="cantidad_pedidos"
            name="Pedidos"
            stroke="#f59e0b"
            strokeWidth={2}
            dot={{ r: 3 }}
            activeDot={{ r: 5 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </Card>
  );
}

export default VentasLineChart;
