import { useState, useEffect } from 'react';
import { createPortal } from 'react-dom';
import { useNavigate } from 'react-router-dom';
import { useCartStore, getTotalItems } from '../../../stores/cartStore';
import { Button } from '../../../shared/components/Button';
import { Modal } from '../../../shared/components/Modal';
import { EmptyState } from '../../../shared/components/EmptyState';
import { CartItemRow } from './CartItemRow';
import { CartSummary } from './CartSummary';

interface CartDrawerProps {
  isOpen: boolean;
  onClose: () => void;
}

export function CartDrawer({ isOpen, onClose }: CartDrawerProps) {
  const { items, updateQuantity, removeItem, clearCart } = useCartStore();
  const navigate = useNavigate();
  const [showClearModal, setShowClearModal] = useState(false);

  const totalItems = getTotalItems(items);

  const handleCheckout = () => {
    onClose();
    navigate('/checkout');
  };

  const handleClearCart = () => {
    clearCart();
    setShowClearModal(false);
  };

  useEffect(() => {
    if (!isOpen) {
      setShowClearModal(false);
    }
  }, [isOpen]);

  const drawerContent = (
    <>
      <div className="flex items-center justify-between border-b border-gray-200 p-4">
        <h2 className="text-lg font-semibold text-gray-900">
          Mi Carrito
          {totalItems > 0 && (
            <span className="ml-2 text-sm font-normal text-gray-500">
              ({totalItems} {totalItems === 1 ? 'item' : 'items'})
            </span>
          )}
        </h2>
        <Button variant="ghost" className="h-8 w-8 !p-0" onClick={onClose}>
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

      {items.length === 0 ? (
        <div className="flex-1 p-4">
          <EmptyState
            title="Tu carrito esta vacio"
            description="Agrega productos del catalogo para empezar tu pedido"
            action={{
              label: 'Ver catalogo',
              onClick: () => {
                onClose();
                navigate('/catalog');
              },
            }}
          />
        </div>
      ) : (
        <>
          <div className="flex-1 overflow-y-auto px-4">
            {items.map((item, index) => (
              <CartItemRow
                key={`${item.producto_id}-${item.personalizacion.join(',')}-${index}`}
                item={item}
                onUpdateQuantity={updateQuantity}
                onRemove={removeItem}
              />
            ))}
          </div>
          <CartSummary
            items={items}
            onClearCart={() => setShowClearModal(true)}
            onCheckout={handleCheckout}
          />
        </>
      )}

      <Modal
        isOpen={showClearModal}
        onClose={() => setShowClearModal(false)}
        title="Vaciar carrito"
        footer={
          <>
            <Button variant="ghost" onClick={() => setShowClearModal(false)}>
              Cancelar
            </Button>
            <Button variant="danger" onClick={handleClearCart}>
              Vaciar
            </Button>
          </>
        }
      >
        <p className="text-sm text-gray-600">
          Se eliminaran todos los productos del carrito. Esta accion no se puede deshacer.
        </p>
      </Modal>
    </>
  );

  return createPortal(
    <>
      <div
        className={`fixed inset-0 z-40 bg-black/50 transition-opacity duration-300 ${
          isOpen ? 'opacity-100' : 'pointer-events-none opacity-0'
        }`}
        onClick={onClose}
      />
      <div
        className={`fixed right-0 top-0 z-50 flex h-full w-full flex-col bg-white shadow-xl transition-transform duration-300 md:max-w-lg ${
          isOpen ? 'translate-x-0' : 'translate-x-full'
        }`}
      >
        {drawerContent}
      </div>
    </>,
    document.body
  );
}

export default CartDrawer;
