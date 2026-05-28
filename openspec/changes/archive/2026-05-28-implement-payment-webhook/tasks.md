## 1. Configuración

- [x] 1.1 Agregar `MP_WEBHOOK_SECRET` a `backend/app/core/config.py`
- [x] 1.2 Agregar `MP_WEBHOOK_SECRET` a `backend/.env.example`

## 2. Schemas

- [x] 2.1 Agregar `WebhookNotification` schema a `backend/app/pagos/schemas.py` con `data.id`, `type`, `action`, `data.id`

## 3. Service — procesar_webhook()

- [x] 3.1 Implementar validación de firma `X-Signature` contra `MP_WEBHOOK_SECRET`
- [x] 3.2 Implementar consulta de verificación a `GET /v1/payments/{payment_id}` de MP API
- [x] 3.3 Implementar idempotencia: verificar si `mp_payment_id` ya fue procesado
- [x] 3.4 Implementar flujo `approved`: transacción atómica con actualización de Pago, transición Pedido a CONFIRMADO, decremento de stock (SELECT FOR UPDATE), registro en HistorialEstadoPedido con actor_id=NULL
- [x] 3.5 Implementar flujo `rejected`/`pending`: solo actualizar `mp_status` en Pago
- [x] 3.6 Manejar errores: stock insuficiente, pedido no encontrado, MP API caída

## 4. Router

- [x] 4.1 Agregar `POST /api/v1/pagos/webhook` en `backend/app/pagos/router.py` (sin autenticación, público)
- [x] 4.2 Validar que el request incluye `data.id` en el body

## 5. Registro del router

- [x] 5.1 Verificar que `pagos_router` está incluido en `backend/app/main.py` (ya debería estarlo)
