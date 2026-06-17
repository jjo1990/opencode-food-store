import { useState } from 'react';
import { Modal } from '../../../shared/components/Modal';
import { OrderBadge } from '../../../shared/components/OrderBadge';
import { useChangeOrderState } from '../hooks/useAdminOrders';
import { TRANSITIONS, ESTADO_LABELS } from '../constants';
import { devLogger } from '../../../shared/utils/logger';

interface Props {
  orderId: string;
  currentEstado: string;
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export function EstadoChangeModal({ orderId, currentEstado, isOpen, onClose, onSuccess }: Props) {
  const transitions = TRANSITIONS[currentEstado] || [];
  const [selectedState, setSelectedState] = useState(transitions[0] || '');
  const [motivo, setMotivo] = useState('');

  const mutation = useChangeOrderState();

  const isCancelTarget = selectedState === 'CANCELADO';
  const isMotivoValid = isCancelTarget ? motivo.trim().length > 0 : true;

  const handleConfirm = async () => {
    try {
      await mutation.mutateAsync({
        id: orderId,
        body: {
          nuevo_estado: selectedState,
          motivo: motivo.trim() || null,
        },
      });
      devLogger.info('Order state changed', { orderId, newState: selectedState, motivo: motivo.trim() || null });
      onSuccess();
      onClose();
    } catch {
      // error handled by mutation hook
    }
  };

  if (transitions.length === 0) {
    return (
      <Modal isOpen={isOpen} onClose={onClose} title="Cambiar Estado">
        <p className="text-sm text-gray-500 dark:text-gray-400">
          Este pedido está en estado terminal y no puede ser modificado.
        </p>
      </Modal>
    );
  }

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Cambiar Estado del Pedido"
      footer={
        <>
          <button
            type="button"
            onClick={onClose}
            className="rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:bg-gray-800 transition-colors"
          >
            Cancelar
          </button>
          <button
            type="button"
            onClick={handleConfirm}
            disabled={!isMotivoValid || mutation.isPending}
            className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-50 transition-colors"
          >
            {mutation.isPending ? 'Procesando...' : 'Confirmar'}
          </button>
        </>
      }
    >
      <div className="space-y-4">
        <div>
          <span className="text-sm text-gray-500 dark:text-gray-400">Estado actual</span>
          <div className="mt-1">
            <OrderBadge estado={currentEstado} />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Nuevo estado</label>
          <select
            value={selectedState}
            onChange={(e) => setSelectedState(e.target.value)}
            className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus-visible:border-indigo-500 focus:outline-none focus-visible:ring-1 focus-visible:ring-indigo-500"
          >
            {transitions.map((estado) => (
              <option key={estado} value={estado}>
                {ESTADO_LABELS[estado] || estado}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
            {isCancelTarget ? 'Motivo de cancelación *' : 'Motivo del cambio'}
          </label>
          <textarea
            value={motivo}
            onChange={(e) => setMotivo(e.target.value)}
            maxLength={500}
            rows={3}
            placeholder={
              isCancelTarget
                ? 'Describí el motivo de la cancelación (obligatorio)'
                : 'Motivo del cambio (opcional)'
            }
            className="mt-1 block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus-visible:border-indigo-500 focus:outline-none focus-visible:ring-1 focus-visible:ring-indigo-500 resize-none"
          />
          {isCancelTarget && !motivo.trim() && (
            <p className="mt-1 text-xs text-red-500">
              El motivo es obligatorio para cancelar un pedido.
            </p>
          )}
        </div>
      </div>
    </Modal>
  );
}

export default EstadoChangeModal;
