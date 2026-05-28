## 1. Schemas

- [x] 1.1 Agregar `HistorialResponse` schema con `estado_desde`, `estado_nuevo`, `actor_id`, `actor_nombre`, `motivo`, `created_at`

## 2. Service

- [x] 2.1 Implementar método `obtener_historial(user, pedido_id)` con validación, LEFT JOIN a User para actor_nombre, orden ASC

## 3. Router

- [x] 3.1 Agregar `GET /api/v1/pedidos/{pedido_id}/historial` con autenticación

## 4. Verificación

- [x] 4.1 Verificar imports y carga de la app
