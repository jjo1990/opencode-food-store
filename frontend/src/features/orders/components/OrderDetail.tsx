import { Modal } from '../../../shared/components/Modal';
import { OrderBadge } from '../../../shared/components/OrderBadge';
import { OrderTimeline } from '../../../shared/components/OrderTimeline';
import { Skeleton } from '../../../shared/components/Skeleton';
import { useOrder } from '../../../entities/order/api';
import type { Order } from '../../../entities/order/types';

interface Props {
  order: Order;
  isOpen: boolean;
  onClose: () => void;
}

export function OrderDetailModal({ order, isOpen, onClose }: Props) {
  const { data: detail, isLoading, isError, error, refetch } = useOrder(order.id);

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={`Pedido #${order.id.slice(0, 8)}`}>
      {isLoading && (
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <Skeleton variant="text" />
            <Skeleton variant="text" />
            <Skeleton variant="text" />
            <Skeleton variant="text" />
          </div>
          <Skeleton variant="card" />
          <Skeleton variant="card" />
        </div>
      )}

      {isError && (
        <div className="flex flex-col items-center gap-4 py-8 text-center">
          <p className="text-sm text-red-600">{(error as Error).message}</p>
          <button
            onClick={() => refetch()}
            className="rounded-lg bg-primary px-4 py-2 text-sm font-medium text-white hover:bg-primary-600"
          >
            Reintentar
          </button>
        </div>
      )}

      {detail && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <OrderBadge estado={detail.estado_codigo} />
            <p className="text-lg font-bold text-primary">${Number(detail.total).toFixed(2)}</p>
          </div>

          <hr />

          <div className="grid grid-cols-2 gap-4">
            <div>
              <span className="text-sm text-gray-500">Subtotal</span>
              <p className="font-medium">${Number(detail.subtotal).toFixed(2)}</p>
            </div>
            <div>
              <span className="text-sm text-gray-500">Costo Envío</span>
              <p className="font-medium">${Number(detail.costo_envio).toFixed(2)}</p>
            </div>
            <div>
              <span className="text-sm text-gray-500">Total</span>
              <p className="text-lg font-bold text-primary">${Number(detail.total).toFixed(2)}</p>
            </div>
            <div>
              <span className="text-sm text-gray-500">Fecha</span>
              <p className="font-medium">{new Date(detail.created_at).toLocaleString()}</p>
            </div>
          </div>

          <hr />

          <div>
            <h3 className="mb-3 font-semibold text-gray-900">Items</h3>
            <div className="overflow-x-auto rounded-lg border border-gray-200">
              <table className="min-w-full divide-y divide-gray-200 text-sm">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-3 py-2 text-left font-medium text-gray-500">Producto</th>
                    <th className="px-3 py-2 text-right font-medium text-gray-500">Precio</th>
                    <th className="px-3 py-2 text-right font-medium text-gray-500">Cant.</th>
                    <th className="px-3 py-2 text-right font-medium text-gray-500">Subtotal</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {detail.items.map((item) => (
                    <tr key={item.id}>
                      <td className="px-3 py-2">
                        <p className="font-medium text-gray-900">{item.nombre_snapshot}</p>
                        {item.personalizacion && item.personalizacion.length > 0 && (
                          <p className="mt-0.5 text-xs text-gray-400">
                            {item.personalizacion.join(', ')}
                          </p>
                        )}
                      </td>
                      <td className="px-3 py-2 text-right text-gray-700">
                        ${Number(item.precio_snapshot).toFixed(2)}
                      </td>
                      <td className="px-3 py-2 text-right text-gray-700">{item.cantidad}</td>
                      <td className="px-3 py-2 text-right font-medium text-gray-900">
                        ${Number(item.subtotal).toFixed(2)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <hr />

          <div>
            <h3 className="mb-3 font-semibold text-gray-900">Historial</h3>
            <OrderTimeline history={detail.historial} currentState={detail.estado_codigo} />
          </div>
        </div>
      )}
    </Modal>
  );
}

export default OrderDetailModal;
