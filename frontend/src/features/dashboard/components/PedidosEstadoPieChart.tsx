import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import Card from '../../../shared/components/Card';
import Skeleton from '../../../shared/components/Skeleton';
import EmptyState from '../../../shared/components/EmptyState';
import ErrorDisplay from '../../../shared/components/ErrorDisplay';
import type { MetricsPedidosEstadoItem } from '../../../shared/api/dashboardApi';

interface PedidosEstadoPieChartProps {
  data: MetricsPedidosEstadoItem[] | undefined;
  isLoading: boolean;
  error?: string;
}

const ESTADO_COLORS: Record<string, string> = {
  PENDIENTE: '#eab308',
  CONFIRMADO: '#3b82f6',
  EN_PREPARACION: '#f97316',
  EN_CAMINO: '#8b5cf6',
  ENTREGADO: '#22c55e',
  CANCELADO: '#ef4444',
};

const FALLBACK_COLORS = [
  '#22c55e',
  '#eab308',
  '#f59e0b',
  '#3b82f6',
  '#ef4444',
  '#8b5cf6',
  '#ec4899',
  '#06b6d4',
  '#f97316',
  '#84cc16',
];

function getColor(estado: string, index: number): string {
  return ESTADO_COLORS[estado] || FALLBACK_COLORS[index % FALLBACK_COLORS.length];
}

interface ChartDataItem {
  name: string;
  value: number;
  porcentaje: number;
}

export function PedidosEstadoPieChart({ data, isLoading, error }: PedidosEstadoPieChartProps) {
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
          title="Sin pedidos"
          description="Aún no hay pedidos registrados en el sistema"
        />
      </Card>
    );
  }

  const chartData: ChartDataItem[] = data.map((item) => ({
    name: item.estado,
    value: item.cantidad,
    porcentaje: item.porcentaje,
  }));

  return (
    <Card>
      <h2 className="mb-4 text-lg font-semibold text-gray-800">Pedidos por estado</h2>
      <ResponsiveContainer width="100%" height={350}>
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            innerRadius={60}
            outerRadius={110}
            paddingAngle={2}
            dataKey="value"
            nameKey="name"
            label={(entry) => {
              const item = entry as unknown as ChartDataItem;
              return `${item.name}: ${item.porcentaje.toFixed(1)}%`;
            }}
          >
            {chartData.map((entry, index) => (
              <Cell key={entry.name} fill={getColor(entry.name, index)} />
            ))}
          </Pie>
          <Tooltip
            formatter={(value, _name, props) => {
              const { name, porcentaje } = (props as unknown as { payload: ChartDataItem }).payload;
              return [`${value} pedidos (${porcentaje.toFixed(1)}%)`, name];
            }}
          />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    </Card>
  );
}

export default PedidosEstadoPieChart;
