import { OrderBadge } from '../../../shared/components/OrderBadge';
import { Pagination } from '../../../shared/components/Pagination';
import type { Order } from '../../../entities/order/types';

interface Props {
  orders: Order[];
  total: number;
  skip: number;
  limit: number;
  onPageChange: (skip: number) => void;
  onViewDetail: (order: Order) => void;
  showClientColumn?: boolean;
  className?: string;
}

export function OrderList({
  orders,
  total,
  skip,
  limit,
  onPageChange,
  onViewDetail,
  showClientColumn = false,
  className = '',
}: Props) {
  const currentPage = Math.floor(skip / limit) + 1;
  const totalPages = Math.ceil(total / limit);

  const handlePageChange = (page: number) => {
    onPageChange((page - 1) * limit);
  };

  return (
    <div className={className}>
      <div className="overflow-x-auto rounded-lg border border-gray-200 dark:border-gray-700">
        <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <thead className="bg-gray-50 dark:bg-gray-800">
            <tr>
              <th                 className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500 dark:text-gray-400">
                ID
              </th>
              <th                 className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500 dark:text-gray-400">
                Estado
              </th>
              {showClientColumn && (
                <th                 className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500 dark:text-gray-400">
                  Cliente
                </th>
              )}
              <th                 className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500 dark:text-gray-400">
                Total
              </th>
              <th                 className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500 dark:text-gray-400">
                Fecha
              </th>
              <th className="px-4 py-3 text-right text-xs font-medium uppercase tracking-wider text-gray-500 dark:text-gray-400">
                Acción
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200 bg-white dark:divide-gray-700 dark:bg-gray-900">
            {orders.map((order) => (
              <tr key={order.id} className="hover:bg-gray-50 transition-colors duration-150 dark:hover:bg-gray-700">
                <td className="whitespace-nowrap px-4 py-3 font-mono text-sm text-gray-900 dark:text-gray-100">
                  {order.id.slice(0, 8)}...
                </td>
                <td className="whitespace-nowrap px-4 py-3">
                  <OrderBadge estado={order.estado_codigo} />
                </td>
                {showClientColumn && (
                  <td className="whitespace-nowrap px-4 py-3 text-sm text-gray-500 dark:text-gray-400">—</td>
                )}
                <td className="whitespace-nowrap px-4 py-3 text-sm font-medium text-gray-900 dark:text-gray-100">
                  ${Number(order.total).toFixed(2)}
                </td>
                <td className="whitespace-nowrap px-4 py-3 text-sm text-gray-500 dark:text-gray-400">
                  {new Date(order.created_at).toLocaleDateString()}
                </td>
                <td className="whitespace-nowrap px-4 py-3 text-right">
                  <button
                    onClick={() => onViewDetail(order)}
                    className="text-sm font-medium text-primary hover:text-primary-700"
                  >
                    Ver detalle
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {total > limit && (
        <div className="mt-4">
          <Pagination
            currentPage={currentPage}
            totalPages={totalPages}
            onPageChange={handlePageChange}
          />
        </div>
      )}
    </div>
  );
}

export default OrderList;
