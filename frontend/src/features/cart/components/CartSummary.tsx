import { Button } from '../../../shared/components/Button';
import { getTotalPrice } from '../../../stores/cartStore';
import type { CartItem } from '../../../stores/cartStore';

interface CartSummaryProps {
  items: CartItem[];
  onClearCart: () => void;
  onCheckout: () => void;
}

const formatPrice = (price: number) =>
  new Intl.NumberFormat('es-AR', { style: 'currency', currency: 'ARS' }).format(price);

export function CartSummary({ items, onClearCart, onCheckout }: CartSummaryProps) {
  const total = getTotalPrice(items);

  return (
    <div className="border-t border-gray-200 p-4 dark:border-gray-700">
      <div className="space-y-2">
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-500 dark:text-gray-400">Subtotal</span>
          <span className="text-gray-900 dark:text-gray-100">{formatPrice(total)}</span>
        </div>
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-500 dark:text-gray-400">Envio</span>
          <span className="font-medium text-green-600">Gratis</span>
        </div>
      </div>

      <hr className="my-3 border-gray-200 dark:border-gray-700" />

      <div className="mb-4 flex items-center justify-between">
        <span className="text-base font-medium text-gray-900 dark:text-gray-100">Total</span>
        <span className="text-xl font-bold text-primary-700 dark:text-primary-400">{formatPrice(total)}</span>
      </div>

      <Button className="w-full" onClick={onCheckout}>
        Ir a pagar
      </Button>

      <Button variant="ghost" className="mt-2 w-full" onClick={onClearCart}>
        Vaciar carrito
      </Button>
    </div>
  );
}

export default CartSummary;
