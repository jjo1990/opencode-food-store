## Context

Ya existe:

- Backend completo de pagos (crear, webhook, reintentar, historial)
- CartDrawer con botón "Ir a pagar" → `/checkout`
- CartStore con items, selectores getTotalItems/getTotalPrice
- AddressList/AddressCard para seleccionar dirección
- OrderConfirmation para post-creación de pedido
- OrderBadge/OrderTimeline para visualizar estados
- Componentes compartidos: Button, Card, Input, Modal, Spinner, Skeleton, ErrorDisplay, EmptyState

Falta: la página de checkout que integre todo.

## Goals / Non-Goals

**Goals:**

- Página `/checkout` protegida (requiere CLIENT)
- Resumen del carrito (items, subtotal, envío, total)
- Selector de dirección de entrega
- Formulario de pago con MercadoPago (tokenización vía SDK)
- POST a `/api/v1/pagos/crear` al hacer submit
- Pantallas post-pago: success, failure (con reintento), pending (con polling)
- Instalar `@mercadopago/sdk-react`

**Non-Goals:**

- No se implementan formas de pago alternativas (solo MERCADOPAGO)
- No se implementa admin de pagos (eso es Phase 7)
- No se modifican componentes existentes (solo se agregan nuevos)

## Decisions

### Decision 1: CheckoutPage como page independiente

Se crea `pages/CheckoutPage.tsx` que organiza el flujo en estados:

1. **review**: mostrar resumen carrito + dirección + forma de pago
2. **processing**: después de submit, mientras MP procesa
3. **success**: pago aprobado
4. **failure**: pago rechazado (con reintento)
5. **pending**: pago en proceso (con polling)

### Decision 2: Tokenización con SDK de MercadoPago

Se usa `@mercadopago/sdk-react` para generar el `card_token`. El frontend nunca ve el número de tarjeta completo — el SDK lo tokeniza directamente en el browser del usuario (PCI SAQ-A compliant).

### Decision 3: Polling con TanStack Query

Para el estado "pending", se usa `useQuery` con `refetchInterval: 5000` (5s) que llama a `GET /api/v1/pagos/{pedido_id}` para detectar cambios de estado. El polling se detiene cuando el estado ya no es pending.

### Decision 4: Reintento usa POST /api/v1/pagos/reintentar

En la pantalla de failure, el botón "Reintentar" llama a `POST /api/v1/pagos/reintentar` con el mismo `pedido_id` y un nuevo `card_token`. Si el reintento es exitoso, redirige a success.

## Flujo de checkout

```
CartDrawer → navigate('/checkout')
                │
                ▼
         CheckoutPage (review)
         ┌─────────────────────┐
         │ Resumen carrito     │
         │ Selector dirección  │
         │ CardPaymentForm (MP)│
         │ Botón "Pagar"       │
         └──────┬──────────────┘
                │ POST /api/v1/pagos/crear
                ▼
         Processing (spinner)
                │
                ▼
         ┌──────┴──────┐
         │             │
     approved       rejected     pending
         │             │            │
         ▼             ▼            ▼
    Success        Failure      Polling (5s)
    "Pedido #X"   Reintentar    GET /pagos/
    Rastrear      Volver        └→ approved/rejected
```

## Estructura de archivos nueva

```
src/
├── entities/payment/
│   ├── types.ts          → PaymentResult, PaymentHistory
│   └── api.ts            → useCreatePayment, useRetryPayment, usePaymentStatus
├── features/checkout/
│   └── components/
│       └── CheckoutForm.tsx   → Formulario con resumen + dirección + MP
├── pages/
│   └── CheckoutPage.tsx       → Página con manejo de estados
├── shared/api/
│   └── pagosApi.ts            → postCrearPago, postReintentarPago, getPagoByPedido
└── app/
    └── router.tsx             → + ruta /checkout
```
