import { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useCartStore, getTotalPrice } from '../stores/cartStore';
import { useAddresses } from '../entities/address/api';
import { useCreatePayment, useRetryPayment, usePaymentStatus } from '../entities/payment/api';
import { Button } from '../shared/components/Button';
import { Card } from '../shared/components/Card';
import { Spinner } from '../shared/components/Spinner';
import { Skeleton } from '../shared/components/Skeleton';
import { EmptyState } from '../shared/components/EmptyState';
import { ErrorDisplay } from '../shared/components/ErrorDisplay';
import type { Address } from '../entities/address/types';
import type { CheckoutStep } from '../entities/payment/types';

const formatPrice = (price: number) =>
  new Intl.NumberFormat('es-AR', { style: 'currency', currency: 'ARS' }).format(price);

export function CheckoutPage() {
  const navigate = useNavigate();
  const { items, clearCart } = useCartStore();
  const [step, setStep] = useState<CheckoutStep>('review');
  const [selectedAddressId, setSelectedAddressId] = useState<string | null>(null);
  const [pedidoId, setPedidoId] = useState<string | null>(null);
  const [paymentResult, setPaymentResult] = useState<{ status: string; detail?: string } | null>(
    null
  );

  const total = getTotalPrice(items);

  const {
    data: addresses,
    isLoading: addressesLoading,
    isError: addressesError,
    refetch: refetchAddresses,
  } = useAddresses();
  const createPayment = useCreatePayment();
  const retryPayment = useRetryPayment();
  const { data: paymentStatus } = usePaymentStatus(pedidoId, step === 'pending');

  const handlePayment = useCallback(async () => {
    if (!selectedAddressId) return;
    setStep('processing');

    try {
      const { postCrearPedido } = await import('../shared/api/pedidosApi');
      const pedido = await postCrearPedido({
        items: items.map((i) => ({
          producto_id: i.producto_id,
          cantidad: i.cantidad,
          personalizacion: i.personalizacion,
        })),
        direccion_id: selectedAddressId,
        forma_pago_codigo: 'MERCADOPAGO',
      });

      setPedidoId(pedido.id);

      const result = await createPayment.mutateAsync({
        pedido_id: pedido.id,
        card_token: 'dummy-token',
      });

      setPaymentResult({ status: result.status, detail: result.status_detail || undefined });

      if (result.status === 'approved') {
        setStep('success');
        clearCart();
      } else if (result.status === 'pending') {
        setStep('pending');
      } else {
        setStep('failure');
      }
    } catch (err) {
      setPaymentResult({ status: 'error', detail: (err as Error).message });
      setStep('failure');
    }
  }, [items, selectedAddressId, createPayment, clearCart]);

  const handleRetry = useCallback(async () => {
    if (!pedidoId) return;
    setStep('processing');

    try {
      const result = await retryPayment.mutateAsync({
        pedido_id: pedidoId,
        card_token: 'dummy-token',
      });

      setPaymentResult({ status: result.status, detail: result.status_detail || undefined });

      if (result.status === 'approved') {
        setStep('success');
        clearCart();
      } else if (result.status === 'pending') {
        setStep('pending');
      } else {
        setStep('failure');
      }
    } catch (err) {
      setPaymentResult({ status: 'error', detail: (err as Error).message });
      setStep('failure');
    }
  }, [pedidoId, retryPayment, clearCart]);

  // Check payment status while pending
  if (step === 'pending' && paymentStatus && paymentStatus.pagos.length > 0) {
    const last = paymentStatus.pagos[0];
    if (last.mp_status !== 'pending') {
      setPaymentResult({ status: last.mp_status, detail: last.status_detail || undefined });
      setStep(last.mp_status === 'approved' ? 'success' : 'failure');
    }
  }

  if (items.length === 0 && step === 'review') {
    return (
      <div className="mx-auto max-w-7xl px-4 py-8">
        <EmptyState
          title="Tu carrito está vacío"
          description="Agregá productos desde el catálogo para empezar a comprar."
          action={{ label: 'Ver catálogo', onClick: () => navigate('/catalog') }}
        />
      </div>
    );
  }

  if (step === 'processing') {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <div className="text-center">
          <Spinner size="lg" />
          <p className="mt-4 text-lg text-gray-600">Procesando tu pago...</p>
        </div>
      </div>
    );
  }

  if (step === 'success') {
    return (
      <div className="mx-auto max-w-lg px-4 py-16 text-center">
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
        <h2 className="mb-2 text-2xl font-bold text-gray-900">¡Pago confirmado!</h2>
        <p className="mb-6 text-gray-500">
          Tu pedido está siendo procesado. Podés seguir su estado desde la sección de pedidos.
        </p>
        <Button onClick={() => navigate('/orders')}>Rastrear pedido</Button>
      </div>
    );
  }

  if (step === 'failure') {
    return (
      <div className="mx-auto max-w-lg px-4 py-16 text-center">
        <div className="mx-auto mb-6 flex h-16 w-16 items-center justify-center rounded-full bg-red-100">
          <svg
            className="h-8 w-8 text-red-600"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M6 18L18 6M6 6l12 12"
            />
          </svg>
        </div>
        <h2 className="mb-2 text-2xl font-bold text-gray-900">Pago rechazado</h2>
        <p className="mb-2 text-gray-500">
          {paymentResult?.detail || 'No se pudo procesar el pago. Intentalo de nuevo.'}
        </p>
        <div className="mt-6 flex justify-center gap-4">
          <Button onClick={handleRetry} isLoading={retryPayment.isPending}>
            Reintentar
          </Button>
          <Button variant="ghost" onClick={() => navigate('/cart')}>
            Volver al carrito
          </Button>
        </div>
      </div>
    );
  }

  if (step === 'pending') {
    return (
      <div className="mx-auto max-w-lg px-4 py-16 text-center">
        <div className="mx-auto mb-6 flex h-16 w-16 items-center justify-center rounded-full bg-yellow-100">
          <svg
            className="h-8 w-8 text-yellow-600"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
        </div>
        <h2 className="mb-2 text-2xl font-bold text-gray-900">Pago en proceso</h2>
        <p className="mb-4 text-gray-500">
          Tu pago está siendo procesado. Esperá la confirmación por favor.
        </p>
        <Spinner />
        <p className="mt-4 text-sm text-gray-400">Verificando estado del pago...</p>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-4xl px-4 py-8 sm:px-6 lg:px-8">
      <h1 className="mb-8 text-2xl font-bold text-gray-900">Checkout</h1>

      <div className="grid gap-8 lg:grid-cols-3">
        <div className="space-y-6 lg:col-span-2">
          <Card>
            <h2 className="mb-4 text-lg font-semibold text-gray-900">Dirección de entrega</h2>
            {addressesLoading ? (
              <div className="space-y-3">
                <Skeleton variant="card" />
                <Skeleton variant="card" />
              </div>
            ) : addressesError ? (
              <ErrorDisplay message="Error al cargar direcciones" onRetry={refetchAddresses} />
            ) : !addresses || addresses.length === 0 ? (
              <div className="py-4 text-center">
                <p className="mb-2 text-gray-500">No tenés direcciones guardadas</p>
                <Button variant="secondary" onClick={() => navigate('/addresses')}>
                  Agregar dirección
                </Button>
              </div>
            ) : (
              <div className="space-y-3">
                {addresses.map((addr: Address) => (
                  <label
                    key={addr.id}
                    className={`block cursor-pointer rounded-lg border-2 p-4 transition-colors ${
                      selectedAddressId === addr.id
                        ? 'border-primary bg-primary-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <input
                      type="radio"
                      name="address"
                      value={addr.id}
                      checked={selectedAddressId === addr.id}
                      onChange={() => setSelectedAddressId(addr.id)}
                      className="sr-only"
                    />
                    <div className="flex items-start justify-between">
                      <div>
                        <p className="font-medium text-gray-900">{addr.alias || 'Dirección'}</p>
                        <p className="text-sm text-gray-500">
                          {addr.calle} {addr.numero}
                          {addr.piso ? `, Piso ${addr.piso}` : ''}
                          {addr.departamento ? `, Depto ${addr.departamento}` : ''}
                        </p>
                        <p className="text-sm text-gray-500">
                          {addr.ciudad}, CP {addr.codigo_postal}
                        </p>
                        {addr.referencia && (
                          <p className="mt-1 text-xs text-gray-400">Ref: {addr.referencia}</p>
                        )}
                      </div>
                      {addr.es_principal && (
                        <span className="rounded bg-green-100 px-2 py-0.5 text-xs font-medium text-green-700">
                          Principal
                        </span>
                      )}
                    </div>
                  </label>
                ))}
                <Button variant="ghost" onClick={() => navigate('/addresses')} className="text-sm">
                  + Agregar nueva dirección
                </Button>
              </div>
            )}
          </Card>

          <Card>
            <h2 className="mb-4 text-lg font-semibold text-gray-900">Forma de pago</h2>
            <div className="rounded-lg border border-gray-200 bg-gray-50 p-4">
              <div className="flex items-center gap-3">
                <div className="flex h-8 w-12 items-center justify-center rounded bg-blue-500 text-xs font-bold text-white">
                  MP
                </div>
                <div>
                  <p className="font-medium text-gray-900">MercadoPago</p>
                  <p className="text-sm text-gray-500">Tarjeta de crédito/débito</p>
                </div>
              </div>
            </div>
            <p className="mt-2 text-xs text-gray-400">
              Tus datos de pago están protegidos por MercadoPago (PCI SAQ-A).
            </p>
          </Card>
        </div>

        <div>
          <Card>
            <h2 className="mb-4 text-lg font-semibold text-gray-900">Resumen</h2>
            <div className="space-y-3">
              {items.map((item) => (
                <div
                  key={`${item.producto_id}-${item.personalizacion.join(',')}`}
                  className="flex justify-between text-sm"
                >
                  <span className="text-gray-600">
                    {item.nombre} x{item.cantidad}
                  </span>
                  <span className="text-gray-900">{formatPrice(item.precio * item.cantidad)}</span>
                </div>
              ))}
            </div>

            <hr className="my-3 border-gray-200" />

            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-500">Subtotal</span>
                <span className="text-gray-900">{formatPrice(total)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Envío</span>
                <span className="font-medium text-green-600">Gratis</span>
              </div>
            </div>

            <hr className="my-3 border-gray-200" />

            <div className="mb-6 flex justify-between">
              <span className="text-base font-medium text-gray-900">Total</span>
              <span className="text-xl font-bold text-primary">{formatPrice(total)}</span>
            </div>

            <Button
              className="w-full"
              onClick={handlePayment}
              disabled={!selectedAddressId || createPayment.isPending}
              isLoading={createPayment.isPending}
            >
              Pagar {formatPrice(total)}
            </Button>

            {!selectedAddressId && (
              <p className="mt-2 text-center text-xs text-amber-600">
                Seleccioná una dirección de entrega para continuar
              </p>
            )}
          </Card>
        </div>
      </div>
    </div>
  );
}

export default CheckoutPage;
