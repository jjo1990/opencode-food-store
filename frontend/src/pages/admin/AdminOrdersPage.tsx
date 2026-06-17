import { useState, useEffect, useRef } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { useAdminOrders } from '../../features/admin-orders/hooks/useAdminOrders';
import { AdminOrderTable } from '../../features/admin-orders/components/AdminOrderTable';
import { OrderDetailModal } from '../../features/admin-orders/components/OrderDetailModal';
import { EstadoChangeModal } from '../../features/admin-orders/components/EstadoChangeModal';
import { Card } from '../../shared/components/Card';
import { ConfirmationModal } from '../../shared/components/ConfirmationModal';
import { ErrorDisplay } from '../../shared/components/ErrorDisplay';
import { EmptyState } from '../../shared/components/EmptyState';

const PAGE_SIZE = 20;

export function AdminOrdersPage() {
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [localSearch, setLocalSearch] = useState('');
  const [estadoCodigo, setEstadoCodigo] = useState('');
  const [fechaInicio, setFechaInicio] = useState('');
  const [fechaFin, setFechaFin] = useState('');
  const [selectedOrderId, setSelectedOrderId] = useState<string | null>(null);
  const [changeStateOrder, setChangeStateOrder] = useState<{
    id: string;
    estado: string;
  } | null>(null);
  const [cancelConfirmOrder, setCancelConfirmOrder] = useState<{
    id: string;
    estado: string;
  } | null>(null);

  const queryClient = useQueryClient();
  const debounceRef = useRef<ReturnType<typeof setTimeout>>();

  useEffect(() => {
    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => {
      setSearch(localSearch);
      setPage(1);
    }, 300);
    return () => {
      if (debounceRef.current) clearTimeout(debounceRef.current);
    };
  }, [localSearch]);

  const params = {
    page,
    size: PAGE_SIZE,
    ...(search && { search }),
    ...(estadoCodigo && { estado_codigo: estadoCodigo }),
    ...(fechaInicio && { fecha_inicio: fechaInicio }),
    ...(fechaFin && { fecha_fin: fechaFin }),
  };

  const { data, isLoading, isError, error, refetch } = useAdminOrders(params);

  const handleFilterChange = (setter: (v: string) => void, value: string) => {
    setter(value);
    setPage(1);
  };

  const handleAdvanceState = (orderId: string, currentState: string) => {
    setSelectedOrderId(null);
    setChangeStateOrder({ id: orderId, estado: currentState });
  };

  const handleCancelOrder = (orderId: string, currentState: string) => {
    setSelectedOrderId(null);
    setCancelConfirmOrder({ id: orderId, estado: currentState });
  };

  const handleCancelConfirm = () => {
    if (!cancelConfirmOrder) return;
    setChangeStateOrder(cancelConfirmOrder);
    setCancelConfirmOrder(null);
  };

  const handleChangeSuccess = () => {
    queryClient.invalidateQueries({ queryKey: ['admin-orders'] });
    queryClient.invalidateQueries({ queryKey: ['admin-order-detail'] });
  };

  const renderContent = () => {
    if (isLoading) {
      return (
        <Card>
          <AdminOrderTable orders={[]} isLoading={true} onSelectOrder={() => {}} />
        </Card>
      );
    }

    if (isError) {
      return (
        <ErrorDisplay
          message={(error as Error)?.message || 'Error al cargar pedidos'}
          onRetry={() => refetch()}
        />
      );
    }

    if (!data || data.items.length === 0) {
      const hasFilters = search || estadoCodigo || fechaInicio || fechaFin;
      return (
        <EmptyState
          title={hasFilters ? 'Sin resultados' : 'No hay pedidos registrados'}
          description={
            hasFilters
              ? 'No se encontraron pedidos con esos filtros.'
              : 'Aún no hay pedidos en el sistema.'
          }
        />
      );
    }

    return (
      <>
        <Card>
          <AdminOrderTable
            orders={data.items}
            isLoading={false}
            onSelectOrder={setSelectedOrderId}
          />
        </Card>

        <div className="mt-4 flex items-center justify-between">
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Mostrando {(page - 1) * PAGE_SIZE + 1}–{Math.min(page * PAGE_SIZE, data.total)} de{' '}
            {data.total}
          </p>
          <div className="flex gap-2">
            <button
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page <= 1}
              className="rounded-lg border border-gray-300 dark:border-gray-700 px-3 py-1.5 text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700/50 disabled:cursor-not-allowed disabled:opacity-50 transition-colors"
            >
              Anterior
            </button>
            <button
              onClick={() => setPage((p) => p + 1)}
              disabled={page >= data.pages}
              className="rounded-lg border border-gray-300 dark:border-gray-700 px-3 py-1.5 text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700/50 disabled:cursor-not-allowed disabled:opacity-50 transition-colors"
            >
              Siguiente
            </button>
          </div>
        </div>
      </>
    );
  };

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100">Gestión de Pedidos</h1>
        <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">Administración de pedidos y cambios de estado.</p>
      </div>

      <div className="mb-6 flex flex-wrap gap-3 items-end">
        <input
          type="text"
          placeholder="Buscar por ID o cliente..."
          value={localSearch}
          onChange={(e) => setLocalSearch(e.target.value)}
          className="rounded-lg border border-gray-300 dark:border-gray-700 px-4 py-2 text-sm focus-visible:border-indigo-500 focus:outline-none focus-visible:ring-1 focus-visible:ring-indigo-500"
        />
        <select
          value={estadoCodigo}
          onChange={(e) => handleFilterChange(setEstadoCodigo, e.target.value)}
          className="rounded-lg border border-gray-300 dark:border-gray-700 px-4 py-2 text-sm focus-visible:border-indigo-500 focus:outline-none focus-visible:ring-1 focus-visible:ring-indigo-500"
        >
          <option value="">Todos</option>
          <option value="PENDIENTE">Pendiente</option>
          <option value="CONFIRMADO">Confirmado</option>
          <option value="EN_PREPARACION">En Preparación</option>
          <option value="EN_CAMINO">En Camino</option>
          <option value="ENTREGADO">Entregado</option>
          <option value="CANCELADO">Cancelado</option>
        </select>
        <div>
          <label className="block text-xs text-gray-500 dark:text-gray-400 mb-1">Desde</label>
          <input
            type="date"
            value={fechaInicio}
            onChange={(e) => handleFilterChange(setFechaInicio, e.target.value)}
            className="rounded-lg border border-gray-300 dark:border-gray-700 px-4 py-2 text-sm focus-visible:border-indigo-500 focus:outline-none focus-visible:ring-1 focus-visible:ring-indigo-500"
          />
        </div>
        <div>
          <label className="block text-xs text-gray-500 dark:text-gray-400 mb-1">Hasta</label>
          <input
            type="date"
            value={fechaFin}
            onChange={(e) => handleFilterChange(setFechaFin, e.target.value)}
            className="rounded-lg border border-gray-300 dark:border-gray-700 px-4 py-2 text-sm focus-visible:border-indigo-500 focus:outline-none focus-visible:ring-1 focus-visible:ring-indigo-500"
          />
        </div>
      </div>

      {renderContent()}

      <OrderDetailModal
        orderId={selectedOrderId}
        isOpen={!!selectedOrderId}
        onClose={() => setSelectedOrderId(null)}
        onAdvanceState={handleAdvanceState}
        onCancelOrder={handleCancelOrder}
      />

      {changeStateOrder && (
        <EstadoChangeModal
          orderId={changeStateOrder.id}
          currentEstado={changeStateOrder.estado}
          isOpen={!!changeStateOrder}
          onClose={() => setChangeStateOrder(null)}
          onSuccess={handleChangeSuccess}
        />
      )}

      <ConfirmationModal
        isOpen={!!cancelConfirmOrder}
        onClose={() => setCancelConfirmOrder(null)}
        onConfirm={handleCancelConfirm}
        title="Cancelar pedido"
        message="¿Estás seguro de cancelar este pedido? Esta acción no se puede deshacer."
        variant="danger"
        confirmLabel="Cancelar pedido"
        cancelLabel="Volver"
      />
    </div>
  );
}

export default AdminOrdersPage;
