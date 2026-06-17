import { Button } from '../../../shared/components/Button';
import type { CartItem } from '../../../stores/cartStore';

interface CartItemRowProps {
  item: CartItem;
  onUpdateQuantity: (producto_id: string, personalizacion: string[], cantidad: number) => void;
  onRemove: (producto_id: string, personalizacion: string[]) => void;
}

const formatPrice = (price: number) =>
  new Intl.NumberFormat('es-AR', { style: 'currency', currency: 'ARS' }).format(price);

export function CartItemRow({ item, onUpdateQuantity, onRemove }: CartItemRowProps) {
  return (
    <>
      <div className="flex items-center gap-4 py-4">
        <div className="h-[60px] w-[60px] flex-shrink-0 overflow-hidden rounded-lg bg-gray-100 dark:bg-gray-700">
          {item.imagen_url ? (
            <img src={item.imagen_url} alt={item.nombre} className="h-full w-full object-cover" />
          ) : (
            <svg
              className="h-full w-full p-3 text-gray-300"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1.5}
                d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
              />
            </svg>
          )}
        </div>

        <div className="min-w-0 flex-1">
          <p className="truncate font-medium text-gray-900 dark:text-gray-100">{item.nombre}</p>
          <p className="text-sm text-gray-500 dark:text-gray-400">{formatPrice(item.precio)}</p>
          {item.personalizacion.length > 0 && (
            <p className="mt-0.5 truncate text-xs text-gray-500">
              Sin: {item.personalizacion.join(', ')}
            </p>
          )}
        </div>

        <div className="flex items-center gap-1">
          <Button
            variant="ghost"
          className="min-h-[44px] min-w-[44px] !p-0"
          disabled={item.cantidad <= 1}
          onClick={() =>
            onUpdateQuantity(item.producto_id, item.personalizacion, item.cantidad - 1)
          }
          aria-label="Disminuir cantidad"
          >
            <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 12H4" />
            </svg>
          </Button>

          <span className="flex h-8 w-8 items-center justify-center text-sm font-medium">
            {item.cantidad}
          </span>

          <Button
            variant="ghost"
          className="min-h-[44px] min-w-[44px] !p-0"
          onClick={() =>
            onUpdateQuantity(item.producto_id, item.personalizacion, item.cantidad + 1)
          }
          aria-label="Aumentar cantidad"
          >
            <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 4v16m8-8H4"
              />
            </svg>
          </Button>
        </div>

        <p className="w-20 text-right font-semibold text-gray-900 dark:text-gray-100">
          {formatPrice(item.precio * item.cantidad)}
        </p>

        <Button
          variant="ghost"
          className="min-h-[44px] min-w-[44px] !p-0 text-gray-500 hover:text-red-500 dark:text-gray-400 dark:hover:text-red-400"
          onClick={() => onRemove(item.producto_id, item.personalizacion)}
        >
          <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M6 18L18 6M6 6l12 12"
            />
          </svg>
        </Button>
      </div>
      <hr className="border-gray-100" />
    </>
  );
}

export default CartItemRow;
