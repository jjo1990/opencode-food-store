import { Modal } from '../../../shared/components/Modal';
import { OrderBadge } from '../../../shared/components/OrderBadge';
import { OrderTimeline } from '../../../shared/components/OrderTimeline';
import { Spinner } from '../../../shared/components/Spinner';
import { ErrorDisplay } from '../../../shared/components/ErrorDisplay';
import { useAdminOrderDetail } from '../hooks/useAdminOrders';
import { TERMINAL_STATES } from '../constants';

interface Props {
  orderId: string | null;
  isOpen: boolean;
  onClose: () => void;
  onAdvanceState: (orderId: string, currentState: string) => void;
  onCancelOrder: (orderId: string, currentState: string) => void;
}

function formatPrice(amount: string | number): string {
  const num = typeof amount === 'string' ? parseFloat(amount) : amount;
  return `$${num.toFixed(2)}`;
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString('es-AR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

export function OrderDetailModal({
  orderId,
  isOpen,
  onClose,
  onAdvanceState,
  onCancelOrder,
}: Props) {
  const { data: order, isLoading, isError, refetch } = useAdminOrderDetail(orderId);

  const renderContent = () => {
    if (isLoading) {
      return (
        <div className="flex items-center justify-center py-12">
          <Spinner size="lg" />
        </div>
      );
    }

    if (isError || !order) {
      return (
        <ErrorDisplay message="Error al cargar el detalle del pedido" onRetry={() => refetch()} />
      );
    }

    const isTerminal = TERMINAL_STATES.includes(order.estado_codigo);

    const timelineEntries = order.historial.map((h) => ({
      created_at: h.created_at,
      estado_nuevo: h.estado_nuevo,
      actor_id: h.actor_id,
      motivo: h.motivo,
    }));

    return (
      <div className="space-y-6">
        <div className="flex items-center gap-3">
          <h3 className="text-sm font-mono text-gray-500">Pedido #{order.id.slice(0, 8)}...</h3>
          <OrderBadge estado={order.estado_codigo} />
        </div>

        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="text-gray-500">Subtotal</span>
            <p className="font-medium">{formatPrice(order.subtotal)}</p>
          </div>
          <div>
            <span className="text-gray-500">Costo envío</span>
            <p className="font-medium">{formatPrice(order.costo_envio)}</p>
          </div>
          <div>
            <span className="text-gray-500">Total</span>
            <p className="font-semibold text-lg">{formatPrice(order.total)}</p>
          </div>
          <div>
            <span className="text-gray-500">Fecha</span>
            <p className="font-medium">{formatDate(order.created_at)}</p>
          </div>
        </div>

        {order.items.length > 0 && (
          <div>
            <h4 className="mb-2 text-sm font-semibold text-gray-700">Productos</h4>
            <div className="overflow-x-auto rounded-lg border border-gray-200">
              <table className="min-w-full divide-y divide-gray-200 text-sm">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-3 py-2 text-left text-xs font-medium uppercase text-gray-500">
                      Producto
                    </th>
                    <th className="px-3 py-2 text-right text-xs font-medium uppercase text-gray-500">
                      Precio Unit.
                    </th>
                    <th className="px-3 py-2 text-center text-xs font-medium uppercase text-gray-500">
                      Cant.
                    </th>
                    <th className="px-3 py-2 text-right text-xs font-medium uppercase text-gray-500">
                      Subtotal
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200 bg-white">
                  {order.items.map((item) => (
                    <tr key={item.id}>
                      <td className="px-3 py-2 font-medium text-gray-900">
                        {item.nombre_snapshot}
                      </td>
                      <td className="px-3 py-2 text-right">{formatPrice(item.precio_snapshot)}</td>
                      <td className="px-3 py-2 text-center">{item.cantidad}</td>
                      <td className="px-3 py-2 text-right">{formatPrice(item.subtotal)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {order.historial.length > 0 && (
          <div>
            <h4 className="mb-2 text-sm font-semibold text-gray-700">Historial</h4>
            <OrderTimeline history={timelineEntries} currentState={order.estado_codigo} />
          </div>
        )}

        {isTerminal && (
          <p className="text-center text-sm text-gray-500 italic">Pedido en estado final</p>
        )}
      </div>
    );
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Detalle del Pedido"
      footer={
        order && !TERMINAL_STATES.includes(order.estado_codigo) ? (
          <>
            <button
              type="button"
              onClick={() => onCancelOrder(order.id, order.estado_codigo)}
              className="rounded-lg border border-red-300 px-4 py-2 text-sm font-medium text-red-700 hover:bg-red-50 transition-colors"
            >
              Cancelar Pedido
            </button>
            <button
              type="button"
              onClick={() => onAdvanceState(order.id, order.estado_codigo)}
              className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 transition-colors"
            >
              Avanzar Estado
            </button>
          </>
        ) : undefined
      }
    >
      {renderContent()}
    </Modal>
  );
}

export default OrderDetailModal;
