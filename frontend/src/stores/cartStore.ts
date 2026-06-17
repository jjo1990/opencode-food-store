/**
 * Cart Store — Zustand store for shopping cart state
 *
 * Client-side only: no API calls, persists to localStorage.
 * Following Zustand v5 pattern with persist middleware.
 */
import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { devLogger } from '../shared/utils/logger';

// ── Types ───────────────────────────────────────────

export interface CartItem {
  producto_id: string;
  nombre: string;
  imagen_url: string | null;
  precio: number;
  cantidad: number;
  /** IDs of ingredients to remove */
  personalizacion: string[];
}

interface CartState {
  items: CartItem[];

  // Actions
  addItem: (item: Omit<CartItem, 'cantidad'> & { cantidad?: number }) => void;
  updateQuantity: (producto_id: string, personalizacion: string[], cantidad: number) => void;
  removeItem: (producto_id: string, personalizacion: string[]) => void;
  updateItemPersonalization: (
    producto_id: string,
    oldPersonalizacion: string[],
    newPersonalizacion: string[]
  ) => void;
  clearCart: () => void;
}

// ── Helpers ─────────────────────────────────────────

/**
 * Find the index of a cart item matching product + personalization.
 * Two items with the same product but different personalizations are separate entries.
 */
function findItemIndex(items: CartItem[], producto_id: string, personalizacion: string[]): number {
  return items.findIndex(
    (item) =>
      item.producto_id === producto_id &&
      item.personalizacion.length === personalizacion.length &&
      item.personalizacion.every((id) => personalizacion.includes(id))
  );
}

// ── Store ───────────────────────────────────────────

export const useCartStore = create<CartState>()(
  persist(
    (set, get) => ({
      items: [],

      addItem: (item) => {
        const producto_id = item.producto_id;
        const personalizacion = item.personalizacion || [];
        const cantidad = item.cantidad || 1;

        devLogger.info('Item added to cart', { productId: producto_id, name: item.nombre, quantity: cantidad });

        set((state) => {
          const index = findItemIndex(state.items, producto_id, personalizacion);

          if (index !== -1) {
            // Item exists — increment quantity
            const updated = [...state.items];
            updated[index] = {
              ...updated[index],
              cantidad: updated[index].cantidad + cantidad,
            };
            return { items: updated };
          }

          // New item — append
          return {
            items: [
              ...state.items,
              {
                producto_id,
                nombre: item.nombre,
                imagen_url: item.imagen_url ?? null,
                precio: item.precio,
                cantidad,
                personalizacion,
              },
            ],
          };
        });
      },

      updateQuantity: (producto_id, personalizacion, cantidad) => {
        if (cantidad <= 0) {
          // Remove item
          get().removeItem(producto_id, personalizacion);
          return;
        }

        set((state) => {
          const index = findItemIndex(state.items, producto_id, personalizacion);
          if (index === -1) return state;

          const updated = [...state.items];
          updated[index] = { ...updated[index], cantidad };
          return { items: updated };
        });
      },

      removeItem: (producto_id, personalizacion) => {
        devLogger.info('Item removed from cart', { productId: producto_id });
        set((state) => ({
          items: state.items.filter(
            (item) =>
              !(
                item.producto_id === producto_id &&
                item.personalizacion.length === personalizacion.length &&
                item.personalizacion.every((id) => personalizacion.includes(id))
              )
          ),
        }));
      },

      updateItemPersonalization: (producto_id, oldPersonalizacion, newPersonalizacion) => {
        set((state) => {
          const index = findItemIndex(state.items, producto_id, oldPersonalizacion);
          if (index === -1) return state;

          const updated = [...state.items];
          const item = updated[index];

          // Check if a item with the new personalization already exists
          const existingIndex = findItemIndex(state.items, producto_id, newPersonalizacion);
          if (existingIndex !== -1 && existingIndex !== index) {
            // Merge: add quantity to the existing entry and remove this one
            updated[existingIndex] = {
              ...updated[existingIndex],
              cantidad: updated[existingIndex].cantidad + item.cantidad,
            };
            updated.splice(index, 1);
            return { items: updated };
          }

          // Just update personalization
          updated[index] = { ...item, personalizacion: newPersonalizacion };
          return { items: updated };
        });
      },

      clearCart: () => {
        devLogger.info('Cart cleared');
        set({ items: [] });
      },
    }),
    {
      name: 'food-store-cart',
      // Persist the full items array
      partialize: (state) => ({ items: state.items }),
    }
  )
);

// ── Selectors (plain functions, not hooks) ──────────

/**
 * Get total number of items (sum of quantities).
 */
export function getTotalItems(items: CartItem[]): number {
  return items.reduce((sum, item) => sum + item.cantidad, 0);
}

/**
 * Get total price of all items (sum of precio × cantidad).
 */
export function getTotalPrice(items: CartItem[]): number {
  return items.reduce((sum, item) => sum + item.precio * item.cantidad, 0);
}

/**
 * Find a specific item by product ID and personalization.
 */
export function getItem(
  items: CartItem[],
  producto_id: string,
  personalizacion: string[]
): CartItem | undefined {
  const index = findItemIndex(items, producto_id, personalizacion);
  return index !== -1 ? items[index] : undefined;
}
