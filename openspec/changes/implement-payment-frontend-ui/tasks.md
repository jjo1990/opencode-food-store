## 1. Dependencia

- [ ] 1.1 Instalar `@mercadopago/sdk-react` con npm

## 2. API Layer

- [ ] 2.1 Crear `shared/api/pagosApi.ts` con `postCrearPago()`, `postReintentarPago()`, `getPagoByPedido()`

## 3. Entity Payment

- [ ] 3.1 Crear `entities/payment/types.ts` con `PaymentResult`, `PaymentHistory`
- [ ] 3.2 Crear `entities/payment/api.ts` con `useCreatePayment()`, `useRetryPayment()`, `usePaymentStatus()` hooks TanStack Query

## 4. Checkout Components

- [ ] 4.1 Crear `features/checkout/components/CheckoutForm.tsx` con resumen carrito, selector dirección, CardPaymentForm de MP
- [ ] 4.2 Crear `pages/CheckoutPage.tsx` con manejo de estados (review, processing, success, failure, pending)

## 5. Router

- [ ] 5.1 Agregar ruta `/checkout` protegida (CLIENT) en `frontend/src/app/router.tsx`
