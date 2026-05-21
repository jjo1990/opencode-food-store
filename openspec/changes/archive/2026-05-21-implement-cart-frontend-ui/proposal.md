## Why

El carrito existe como store Zustand (Change 25) pero no tiene interfaz visual. El usuario no puede ver qué productos agregó, modificar cantidades, ni iniciar el proceso de pago. Sin esta UI, el carrito es invisible e inutilizable.

## What Changes

- Nuevo componente `CartDrawer`: drawer deslizable desde la derecha con overlay, lista de items, totales, botones "Vaciar" y "Ir a Pagar"
- Nuevo componente `CartItemRow`: cada línea del carrito con imagen, nombre, precio, controles +/- de cantidad, botón eliminar, ingredientes removidos
- Nuevo componente `CartSummary`: badge en el header con cantidad de items, desglose de totales en el drawer
- Modificar `Header` para incluir botón del carrito con badge de cantidad
- Modificar `ProductDetail` para que el botón "Agregar al carrito" llame al cartStore
- Responsive: drawer full-width en mobile

## Capabilities

### New Capabilities

- `cart-frontend-ui`: Interfaz visual del carrito de compras con drawer, controles de cantidad, e integración en header

### Modified Capabilities

- _(ninguna)_

## Impact

- **Frontend**: 3 componentes nuevos, 2 modificaciones (Header, ProductDetail)
- **Dependencias**: `implement-cart-zustand-store` ✅, `implement-catalog-frontend-ui` ✅
- **No breaking**: no cambia APIs, no modifica stores existentes
