## Why

Antes de crear un pedido, el sistema necesita validar que los items del carrito sean válidos: que los productos existan, estén disponibles, tengan stock suficiente, y que las personalizaciones (ingredientes a remover) sean válidas. Sin esta validación, el backend podría recibir pedidos inválidos que resulten en errores 500 o datos inconsistentes. Esta validación también permite al frontend mostrar advertencias (ej: "El precio de X cambió") antes de que el usuario confirme la compra.

## What Changes

- Nuevo módulo `backend/app/checkout/` con: schemas, service, router
- Endpoint `POST /api/v1/checkout/validar` que recibe items del carrito y retorna resultado de validación
- Validaciones por item:
  - Producto existe y no está soft-deleteado
  - Producto está disponible (disponible = true)
  - Stock suficiente (stock_cantidad >= cantidad solicitada)
  - Ingredientes en personalizacion existen en el producto y son removibles
  - Detección de cambios de precio (precio actual vs precio snapshot)
- Respuesta: `{ valido: boolean, errores: string[], advertencias: string[], detalles: ItemValidado[] }`
- Sin autenticación requerida (puede llamarse antes de login, aunque el carrito en sí requiere sesión)

## Capabilities

### New Capabilities

- `checkout-validation`: Validación previa de items del carrito antes de crear un pedido, verificando existencia, disponibilidad, stock, personalizaciones y cambios de precio

### Modified Capabilities

- _(ninguna)_

## Impact

- **Backend**: Nuevo módulo `backend/app/checkout/` (~4 archivos), registro en `main.py`
- **Dependencias**: `implement-products-crud` ✅ (productos con stock y relaciones), `implement-cart-zustand-store` ✅ (define el contrato de CartItem)
- **No breaking**: endpoint nuevo, no modifica APIs existentes
