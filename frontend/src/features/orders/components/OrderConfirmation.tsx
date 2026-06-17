interface Props {
  orderId: string;
  total: number;
  direccionSnapshot?: string;
  onViewOrders: () => void;
  onGoToPayment?: () => void;
  className?: string;
}

export function OrderConfirmation({
  orderId,
  total,
  direccionSnapshot,
  onViewOrders,
  onGoToPayment,
  className = '',
}: Props) {
  return (
    <div className={`mx-auto max-w-lg text-center ${className}`}>
      <div className="mx-auto mb-6 flex h-16 w-16 items-center justify-center rounded-full bg-green-100">
        <svg
          className="h-8 w-8 text-green-600"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
        </svg>
      </div>

      <h2 className="mb-2 text-2xl font-bold text-gray-900 dark:text-gray-100">¡Pedido creado exitosamente!</h2>
      <p className="mb-6 text-gray-500 dark:text-gray-400">Tu pedido ha sido registrado y está pendiente de pago.</p>

      <div className="mb-6 rounded-lg bg-gray-50 p-4 text-left dark:bg-gray-800">
        <div className="flex justify-between py-1">
          <span className="text-gray-500 dark:text-gray-400">Pedido</span>
          <span className="font-mono font-medium">{orderId.slice(0, 8)}...</span>
        </div>
        <div className="flex justify-between py-1">
          <span className="text-gray-500 dark:text-gray-400">Total</span>
          <span className="font-bold text-primary-700 dark:text-primary-400">${Number(total).toFixed(2)}</span>
        </div>
        {direccionSnapshot && (
          <div className="py-1">
            <span className="text-gray-500 dark:text-gray-400">Dirección</span>
            <p className="mt-1 text-sm">{direccionSnapshot}</p>
          </div>
        )}
      </div>

      <div className="flex justify-center gap-4">
        <button
          onClick={onViewOrders}
          className="rounded-lg border border-gray-300 px-6 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-700"
        >
          Ver mis pedidos
        </button>
        {onGoToPayment && (
          <button
            onClick={onGoToPayment}
            className="rounded-lg bg-primary px-6 py-2 text-sm font-medium text-white hover:bg-primary-700"
          >
            Ir a pagar
          </button>
        )}
      </div>
    </div>
  );
}

export default OrderConfirmation;
