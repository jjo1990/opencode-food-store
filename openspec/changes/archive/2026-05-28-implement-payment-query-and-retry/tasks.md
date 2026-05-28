## 1. Schemas

- [x] 1.1 Agregar `PagoHistoryItem` schema a `backend/app/pagos/schemas.py` con `mp_payment_id`, `mp_status`, `status_detail`, `created_at`
- [x] 1.2 Agregar `PagoHistoryResponse` schema con `pagos: list[PagoHistoryItem]`
- [x] 1.3 Agregar `ReintentarPagoRequest` schema con `pedido_id` y `card_token`

## 2. Service

- [x] 2.1 Agregar método `consultar_pagos(pedido_id, user)` que retorna todos los pagos de un pedido con ownership check
- [x] 2.2 Agregar método `reintentar_pago(user, data)` que valida pedido PENDIENTE con pago previo rechazado, genera nueva idempotency_key, llama a MP SDK, registra nuevo Pago

## 3. Router

- [x] 3.1 Agregar `GET /api/v1/pagos/{pedido_id}` con autenticación y ownership check (CLIENT ve propios, ADMIN ve todos)
- [x] 3.2 Agregar `POST /api/v1/pagos/reintentar` con autenticación CLIENT

## 4. Verificación

- [x] 4.1 Verificar imports y carga de la app
