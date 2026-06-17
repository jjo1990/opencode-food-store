import { useState, useCallback } from 'react';
import { useOrders } from '../../entities/order/api';
import { OrderList } from '../../features/orders/components/OrderList';
import { OrderDetailModal } from '../../features/orders/components/OrderDetail';
import { Skeleton } from '../../shared/components/Skeleton';
import { ErrorDisplay } from '../../shared/components/ErrorDisplay';
import { EmptyState } from '../../shared/components/EmptyState';
import type { Order } from '../../entities/order/types';

export function PedidosPanelPage() {
  const [skip, setSkip] = useState(0);
  const [selectedOrder, setSelectedOrder] = useState<Order | null>(null);
  const limit = 20;

  const { data, isLoading, isError, error, refetch } = useOrders({ skip, limit });

  const handlePageChange = useCallback((newSkip: number) => {
    setSkip(newSkip);
  }, []);

  if (isLoading) {
    return (
      <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <div className="mb-6 h-8 w-48 animate-pulse rounded bg-gray-200" />
        <div className="space-y-4">
          {Array.from({ length: 6 }).map((_, i) => (
            <Skeleton key={i} variant="card" />
          ))}
        </div>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <ErrorDisplay message={(error as Error).message} onRetry={refetch} />
      </div>
    );
  }

  if (!data || data.items.length === 0) {
    return (
      <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <EmptyState title="No hay pedidos" description="No se encontraron pedidos registrados." />
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <h1 className="mb-6 text-2xl font-bold text-gray-900 dark:text-gray-100">Gestión de Pedidos</h1>
      <OrderList
        orders={data.items}
        total={data.total}
        skip={skip}
        limit={limit}
        onPageChange={handlePageChange}
        onViewDetail={setSelectedOrder}
      />
      {selectedOrder && (
        <OrderDetailModal
          order={selectedOrder}
          isOpen={!!selectedOrder}
          onClose={() => setSelectedOrder(null)}
        />
      )}
    </div>
  );
}

export default PedidosPanelPage;
