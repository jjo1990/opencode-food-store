## Why

Los pedidos se crean en estado PENDIENTE pero no hay forma de procesar el pago. Sin integración MercadoPago, el pedido nunca avanza a CONFIRMADO y el ciclo de compra está muerto. Este change implementa el primer endpoint de pago que crea una transacción en MercadoPago y registra el intento en la tabla `pago`.

## What Changes

- **Nuevo modelo `Pago`**: tabla con mp_payment_id, mp_status, external_reference, idempotency_key, relación 1:N con Pedido
- **Nueva migración Alembic**: `add_pago_table` con la tabla `pago`
- **Instalación de dependencia**: `mercadopago` SDK v2.3+ en backend
- **Nuevo módulo `pagos/`**: schemas, service, router
- **Nuevo endpoint**: `POST /api/v1/pagos/crear` — crea pago en MercadoPago con token de tarjeta
- **Config**: `MP_ACCESS_TOKEN` en variables de entorno para el SDK

## Capabilities

### New Capabilities

- `payment-creation`: Creación de pagos vía MercadoPago Checkout API con tokenización del lado del cliente (PCI SAQ-A), registro de transacciones en tabla Pago, y clave de idempotencia para prevenir cobros duplicados.

## Impact

- **Backend**: nuevo módulo `backend/app/pagos/` con schemas, service, router + modelo Pago en models/
- **Dependencias**: `mercadopago` SDK agregado a requirements.txt
- **Base de datos**: nueva tabla `pago` con migración Alembic
- **Config**: `MP_ACCESS_TOKEN` debe estar configurado en el entorno
