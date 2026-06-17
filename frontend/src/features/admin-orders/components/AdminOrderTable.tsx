import { OrderBadge } from '../../../shared/components/OrderBadge';
import { EmptyState } from '../../../shared/components/EmptyState';
import { Skeleton } from '../../../shared/components/Skeleton';
import type { AdminOrderListItem } from '../../../shared/api/adminOrdersApi';
import { TERMINAL_STATES } from '../constants';

interface Props {
  orders: AdminOrderListItem[];
  isLoading: boolean;
  onSelectOrder: (id: string) => void;
}

function formatPrice(amount: number): string {
  return `$${amount.toFixed(2)}`;
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString('es-AR', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
}

function truncateUUID(id: string): string {
  return id.slice(0, 8) + '...';
}

export function AdminOrderTable({ orders, isLoading, onSelectOrder }: Props) {
  if (isLoading) {
    return (
      <div className="overflow-x-auto rounded-lg border border-gray-200 dark:border-gray-700">
        <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <thead className="bg-gray-50 dark:bg-gray-800">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-medium uppercase text-gray-500 dark:text-gray-400">
                ID
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium uppercase text-gray-500 dark:text-gray-400">
                Cliente
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium uppercase text-gray-500 dark:text-gray-400">
                Monto
              </th>
              <th className="px-4 py-3 text-center text-xs font-medium uppercase text-gray-500 dark:text-gray-400">
                Estado
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium uppercase text-gray-500 dark:text-gray-400">
                Fecha
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium uppercase text-gray-500 dark:text-gray-400">
                Direccion
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200 bg-white dark:divide-gray-700 dark:bg-gray-900">
            {Array.from({ length: 5 }).map((_, i) => (
              <tr key={i}>
                <td className="px-4 py-3">
                  <Skeleton width="80px" height="16px" />
                </td>
                <td className="px-4 py-3">
                  <Skeleton width="120px" height="16px" />
                </td>
                <td className="px-4 py-3">
                  <Skeleton width="80px" height="16px" />
                </td>
                <td className="px-4 py-3">
                  <Skeleton width="90px" height="16px" />
                </td>
                <td className="px-4 py-3">
                  <Skeleton width="100px" height="16px" />
                </td>
                <td className="px-4 py-3">
                  <Skeleton width="140px" height="16px" />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  }

  if (orders.length === 0) {
    return (
      <EmptyState
        title="No se encontraron pedidos"
        description="No hay pedidos registrados en el sistema."
      />
    );
  }

  return (
    <div className="overflow-x-auto rounded-lg border border-gray-200 dark:border-gray-700">
      <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700" aria-label="Listado de pedidos">
        <thead className="bg-gray-50 dark:bg-gray-800">
          <tr>
            <th className="px-4 py-3 text-left text-xs font-medium uppercase text-gray-500 dark:text-gray-400">ID</th>
            <th className="px-4 py-3 text-left text-xs font-medium uppercase text-gray-500 dark:text-gray-400">
              Cliente
            </th>
            <th className="px-4 py-3 text-left text-xs font-medium uppercase text-gray-500 dark:text-gray-400">
              Monto
            </th>
            <th className="px-4 py-3 text-center text-xs font-medium uppercase text-gray-500 dark:text-gray-400">
              Estado
            </th>
            <th className="px-4 py-3 text-left text-xs font-medium uppercase text-gray-500 dark:text-gray-400">
              Fecha
            </th>
            <th className="px-4 py-3 text-left text-xs font-medium uppercase text-gray-500 dark:text-gray-400">
              Direccion
            </th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-200 bg-white dark:divide-gray-700 dark:bg-gray-900">
          {orders.map((order) => {
            const isTerminal = TERMINAL_STATES.includes(order.estado_codigo);
            const tooltipContent =
              `Cliente: ${order.cliente_nombre || truncateUUID(order.usuario_id)}` +
              `\nDireccion: ${order.direccion_calle || '—'}`;

            return (
              <tr
                key={order.id}
                onClick={() => onSelectOrder(order.id)}
                title={tooltipContent}
                className={`cursor-pointer transition-colors duration-150 hover:bg-gray-50 dark:hover:bg-gray-800 group relative${
                  isTerminal ? ' opacity-75' : ''
                }`}
              >
                <td className="px-4 py-3 text-sm font-mono dark:text-gray-300">{truncateUUID(order.id)}</td>
                <td className="px-4 py-3 text-sm font-medium text-gray-900 dark:text-gray-100">
                  {order.cliente_nombre || truncateUUID(order.usuario_id)}
                </td>
                <td className="px-4 py-3 text-sm dark:text-gray-300">{formatPrice(order.total)}</td>
                <td className="px-4 py-3 text-center">
                  <OrderBadge estado={order.estado_codigo} />
                </td>
                <td className="px-4 py-3 text-sm whitespace-nowrap dark:text-gray-300">
                  {formatDate(order.created_at)}
                </td>
                <td className="px-4 py-3 text-sm text-gray-500 dark:text-gray-400">{order.direccion_calle || '—'}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

export default AdminOrderTable;
