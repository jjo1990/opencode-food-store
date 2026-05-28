## Why

Los pagos creados con MercadoPago (`POST /api/v1/pagos/crear`) quedan huérfanos — el sistema registra el intento de pago pero nunca recibe la confirmación de si fue aprobado, rechazado o está pendiente. Sin el webhook IPN de MercadoPago, el Pedido permanece en PENDIENTE para siempre, el stock nunca se descuenta, y el ciclo de compra está roto.

## What Changes

- **Nuevo endpoint público** `POST /api/v1/pagos/webhook` que recibe notificaciones IPN de MercadoPago
- **Validación de firma**: verifica `X-Signature` header para autenticar el origen
- **Consulta de verificación**: hace GET a la API de MercadoPago para confirmar el estado real del pago (nunca confiar solo en el body del webhook)
- **Transición de estado PENDIENTE → CONFIRMADO**: cuando el pago es `approved`, avanza el Pedido atómicamente
- **Decremento de stock**: descuenta `stock_cantidad` de cada Producto en el pedido (SELECT FOR UPDATE)
- **Registro en HistorialEstadoPedido**: crea entrada de auditoría con actor=SISTEMA
- **Manejo de rechazos/pendientes**: solo actualiza `mp_status` en la tabla Pago sin cambiar el pedido
- **Idempotencia**: si el `mp_payment_id` ya fue procesado, ignora el webhook

No hay breaking changes. No se modifican endpoints existentes.

## Capabilities

### New Capabilities

- `payment-webhook`: Procesamiento de notificaciones IPN de MercadoPago con validación de firma, consulta de verificación, transición de estado de pedido y decremento de stock

### Modified Capabilities

- (ninguna — el comportamiento existente de `payment-creation` no cambia)

## Impact

- **Nuevo endpoint**: `POST /api/v1/pagos/webhook` (público, sin autenticación)
- **Archivos a modificar**:
  - `backend/app/pagos/service.py` — nuevo método `procesar_webhook()`
  - `backend/app/pagos/schemas.py` — nuevo schema `WebhookNotification`
  - `backend/app/pagos/router.py` — nueva ruta webhook
- **Archivos existentes que se usan (sin modificar)**:
  - `backend/app/pedidos/repository.py` — para actualizar estado del pedido
  - `backend/app/productos/repository.py` — para decrementar stock
  - `backend/app/core/config.py` — `MP_ACCESS_TOKEN` ya existe
- **Dependencias**: `mercadopago` SDK ya está instalado
- **Riesgo de seguridad**: endpoint público → requiere validación de firma obligatoria
