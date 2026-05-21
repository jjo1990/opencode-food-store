## 1. Cart Feature Components

- [x] 1.1 Crear `features/cart/components/CartItemRow.tsx` con imagen, nombre, precio, +/- qty, remove, ingredientes removidos
- [x] 1.2 Crear `features/cart/components/CartSummary.tsx` con subtotal, envío, total, botones Vaciar e Ir a Pagar
- [x] 1.3 Crear `features/cart/components/CartDrawer.tsx` con overlay, animación slide, lista, summary, empty state

## 2. Integración en Header y ProductDetail

- [x] 2.1 Modificar `widgets/Header.tsx` para incluir botón carrito con badge de cantidad
- [x] 2.2 Modificar `features/catalog/components/ProductDetail.tsx` para que botón "Agregar al carrito" use cartStore + toast

## 3. Verify

- [x] 3.1 Type-check: `npx tsc --noEmit` sin errores
- [x] 3.2 Build: `npm run build` exitoso
