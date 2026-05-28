## Why

Actualmente no hay forma de consultar el estado de los pagos de un pedido ni reintentar un pago rechazado. El endpoint `POST /api/v1/pagos/crear` solo crea un pago nuevo, pero si falla, el cliente no puede ver qué pasó ni intentar de nuevo sin perder datos del intento anterior.

## What Changes

- **Nuevo endpoint GET /api/v1/pagos/{pedido_id}**: retorna el historial de pagos asociados a un pedido (soportando la relación 1:N Pedido→Pago para múltiples reintentos)
- **Nuevo endpoint POST /api/v1/pagos/reintentar**: permite al cliente crear un nuevo intento de pago para un pedido cuyo último pago fue rechazado, generando un nuevo `idempotency_key` y llamando a MercadoPago SDK nuevamente

No hay breaking changes. El endpoint `POST /api/v1/pagos/crear` existente no se modifica.

## Capabilities

### New Capabilities

- `payment-query-and-retry`: Consulta de historial de pagos por pedido y reintento de pagos rechazados

### Modified Capabilities

- (ninguna — los specs existentes de `payment-creation` y `payment-webhook` no cambian)

## Impact

- **Nuevos endpoints**:
  - `GET /api/v1/pagos/{pedido_id}` (autenticado, ownership check)
  - `POST /api/v1/pagos/reintentar` (autenticado, requiere CLIENT)
- **Archivos a modificar**:
  - `backend/app/pagos/schemas.py` — nuevo `PagoResponse` extendido o `PagoHistoryResponse`
  - `backend/app/pagos/service.py` — nuevos métodos `consultar_pagos()` y `reintentar_pago()`
  - `backend/app/pagos/router.py` — nuevas rutas GET y POST
- **Archivos existentes que se usan (sin modificar)**:
  - `backend/app/pedidos/repository.py` — para validar pedido existente
  - `backend/app/pagos/schemas.py` — `CrearPagoRequest` reutilizado para reintento
  - `backend/app/pagos/service.py` — lógica de `crear_pago` como base para reintento
- **Dependencias**: el SDK de MercadoPago ya está instalado y configurado
