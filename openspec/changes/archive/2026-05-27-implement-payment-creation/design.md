## Context

El sistema puede crear pedidos en estado PENDIENTE pero no procesar pagos. MercadoPago es la única pasarela de pago (las otras formas de pago — EFECTIVO y TRANSFERENCIA — son offline y no requieren integración).

El SDK `mercadopago` v2.x de Python permite crear pagos con tokens de tarjeta generados por el frontend (PCI SAQ-A compliant — los datos de tarjeta nunca tocan el servidor).

La tabla `pago` no existe ni como modelo ni como migración. Usa una relación 1:N con Pedido (un pedido puede tener múltiples intentos de pago).

## Goals / Non-Goals

**Goals:**

- Instalar SDK `mercadopago` en el backend
- Crear modelo `Pago` en `models/pago.py` y registrarlo en `models/__init__.py`
- Generar migración Alembic con la tabla `pago`
- Endpoint `POST /api/v1/pagos/crear` que:
  1. Recibe `pedido_id` y `card_token`
  2. Valida pedido (existe, PENDIENTE, ownership)
  3. Genera `idempotency_key`
  4. Llama a MercadoPago SDK con external_reference = pedido_id
  5. Registra intento en tabla Pago
  6. Retorna mp_payment_id, status, status_detail

**Non-Goals:**

- Webhook IPN de MercadoPago (Change 32)
- Consulta/reintento de pagos (Change 33)
- Frontend de pagos (Change 36)
- Avanzar estado del pedido (Change 34)

## Decisions

### 1. SDK mercadopago v2.x con access token

**Decisión**: Usar `mercadopago` SDK Python con `MP_ACCESS_TOKEN` de variable de entorno para autenticar.
**Por qué**: Es el SDK oficial de MercadoPago. Maneja retry, timeouts y serialización automáticamente.

### 2. idempotency_key como UUID string

**Decisión**: Generar un UUID v4 como `idempotency_key` para cada intento de pago, enviarlo a MP y almacenarlo en la tabla Pago con unique constraint.
**Por qué**: Previene cobros duplicados si el frontend reintenta la misma solicitud o si MP envía webhooks duplicados.

### 3. Modelo Pago con relación 1:N a Pedido

**Decisión**: Un pedido puede tener múltiples registros en Pago (intentos fallidos + exitoso).
**Por qué**: El ERD v5 especifica que un pedido puede tener múltiples intentos de pago (rechazado → reintentar). La tabla Pago tiene `pedido_id` FK.

### 4. Sin cambios en el estado del pedido desde este endpoint

**Decisión**: El endpoint solo registra el intento de pago. No avanza el estado del pedido a CONFIRMADO. Eso lo hace el webhook (Change 32) cuando MP confirma que el pago se acreditó.
**Por qué**: Separación de concerns. El endpoint de creación registra el intento; el webhook confirma. Si confiáramos en la respuesta sincrónica de MP, un pago que queda "pending" (ej. Rapipago) no podría avanzar.

## Risks / Trade-offs

| Riesgo                                             | Mitigación                                                                    |
| -------------------------------------------------- | ----------------------------------------------------------------------------- |
| Sin MP_ACCESS_TOKEN configurado → error en runtime | Validar al inicio: si no hay token, el endpoint retorna 503 con mensaje claro |
| Token de tarjeta expirado o inválido               | MercadoPago retorna error específico; se propaga al frontend                  |
| Timeout en llamada a MP                            | SDK tiene timeout default. Capturar y retornar 502                            |
| Idempotency key duplicado                          | Unique constraint en BD + manejo de excepción                                 |
| MP devuelve status=rejected                        | Se registra igual en BD (para historial de intentos) y se retorna al frontend |
