## Why

El backend de pagos está completo (creación, webhook, reintento, consulta de historial), pero no existe interfaz de usuario para que el cliente pueda pagar. El CartDrawer ya tiene un botón "Ir a pagar" que navega a `/checkout`, pero la ruta no existe. Sin este change, el ciclo de compra está roto: el usuario agrega items al carrito pero no puede finalizar la compra.

## What Changes

- **CheckoutPage** (`/checkout`): paso a paso con resumen del carrito, selector de dirección, formulario de pago con MercadoPago SDK
- **Integración MercadoPago SDK**: instalación de `@mercadopago/sdk-react`, tokenización de tarjeta en frontend (PCI SAQ-A compliant)
- **Pagos API layer**: `shared/api/pagosApi.ts` con funciones para crear pago, reintentar, consultar historial
- **Entity payment**: `entities/payment/` con tipos y hooks TanStack Query
- **Pantallas post-pago**: success (redirect tracking), failure (reintentar), pending (polling)
- **Ruta `/checkout`** protegida para CLIENT

## Capabilities

### New Capabilities

- `payment-frontend-ui`: Interfaz de checkout con integración MercadoPago SDK, selección de dirección, y pantallas post-pago

### Modified Capabilities

- (ninguna)

## Impact

- **Nuevo paquete**: `@mercadopago/sdk-react` (instalar con npm)
- **Nuevos archivos frontend**:
  - `frontend/src/shared/api/pagosApi.ts` — funciones API
  - `frontend/src/entities/payment/types.ts` — tipos
  - `frontend/src/entities/payment/api.ts` — hooks TanStack Query
  - `frontend/src/features/checkout/components/CheckoutForm.tsx` — formulario checkout
  - `frontend/src/features/checkout/components/PaymentStatus.tsx` — post-pago
  - `frontend/src/pages/CheckoutPage.tsx` — página completa
- **Archivos a modificar**:
  - `frontend/package.json` — agregar dependencia
  - `frontend/src/app/router.tsx` — agregar ruta `/checkout`
