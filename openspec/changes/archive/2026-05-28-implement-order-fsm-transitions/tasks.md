## 1. Schemas

- [x] 1.1 Agregar `AvanzarEstadoRequest` schema a `backend/app/pedidos/schemas.py` con `nuevo_estado: str` y `motivo: str | None`

## 2. Service — FSM

- [x] 2.1 Definir mapa `TRANSITIONS` hardcodeado con todas las transiciones válidas, roles requeridos y acciones de stock
- [x] 2.2 Implementar método `avanzar_estado(user, pedido_id, nuevo_estado, motivo)` con validación de transiciones, roles, ownership, restauración de stock y registro de historial

## 3. Router

- [x] 3.1 Agregar `PATCH /api/v1/pedidos/{pedido_id}/avanzar` con autenticación

## 4. Verificación

- [x] 4.1 Verificar imports y carga de la app
