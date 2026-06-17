import { CardPayment, initMercadoPago } from '@mercadopago/sdk-react';
import { Card } from '../../../shared/components/Card';
import { postCrearPedido } from '../../../shared/api/pedidosApi';
import { postCrearPago } from '../../../shared/api/pagosApi';
import { devLogger } from '../../../shared/utils/logger';
import type { CartItem } from '../../../stores/cartStore';

initMercadoPago(import.meta.env.VITE_MP_PUBLIC_KEY);

interface CheckoutFormProps {
  amount: number;
  items: CartItem[];
  selectedAddressId: string;
  onComplete: (result: { pedidoId: string; status: string; statusDetail?: string }) => void;
  onError: (error: Error) => void;
}

export function CheckoutForm({ amount, items, selectedAddressId, onComplete, onError }: CheckoutFormProps) {
  return (
    <Card>
      <h2 className="mb-4 text-lg font-semibold text-gray-900 dark:text-gray-100">Tarjeta de crédito/débito</h2>
      <p className="mb-4 text-sm text-gray-500 dark:text-gray-400">
        Completá los datos de tu tarjeta para realizar el pago.
      </p>
      <CardPayment
        initialization={{ amount }}
        onSubmit={async (formData) => {
          try {
            const pedido = await postCrearPedido({
              items: items.map((i) => ({
                producto_id: i.producto_id,
                cantidad: i.cantidad,
                personalizacion: i.personalizacion,
              })),
              direccion_id: selectedAddressId,
              forma_pago_codigo: 'MERCADOPAGO',
            });
            devLogger.info('Payment initiated', { orderId: pedido.id });
            const result = await postCrearPago({
              pedido_id: pedido.id,
              card_token: formData.token,
            });
            onComplete({
              pedidoId: pedido.id,
              status: result.status,
              statusDetail: result.status_detail ?? undefined,
            });
          } catch (err) {
            onError(err as Error);
          }
        }}
        onError={(error) => {
          onError(new Error(error.message));
        }}
      />
    </Card>
  );
}

export default CheckoutForm;
