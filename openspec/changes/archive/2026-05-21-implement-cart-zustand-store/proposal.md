## Why

El carrito de compras es el estado transicional más importante del sistema: almacena los productos que el cliente quiere comprar, sus cantidades, y personalizaciones (ingredientes a remover). Sin un carrito funcional, el usuario no puede avanzar al checkout. Este store Zustand manejará todo el estado del carrito en el cliente, con persistencia local para sobrevivir a cierres de navegador y refrescos de página.

## What Changes

- Nuevo store Zustand `cartStore` en `stores/cartStore.ts`
- Interface `CartItem` con: producto_id, nombre, imagen_url, precio, cantidad, personalizacion (ingredientIds[])
- Acciones sincrónicas: addItem, updateQuantity, removeItem, clearCart, updateItemPersonalization
- Selectores derivados: totalItems, totalPrice
- Persistencia con `zustand/middleware/persist` en localStorage bajo clave `food-store-cart`
- Sin dependencia de APIs — es estado puramente del cliente

## Capabilities

### New Capabilities

- `cart-client-state`: Store Zustand para el carrito de compras con persistencia local, acciones CRUD de items, y selectores de totales

### Modified Capabilities

- _(ninguna)_

## Impact

- **Frontend**: 1 archivo nuevo (`stores/cartStore.ts`), sin cambios a otros archivos
- **Dependencias**: `setup-zustand-stores` ✅ (ya implementado)
- **No breaking**: store independiente, no modifica stores existentes
