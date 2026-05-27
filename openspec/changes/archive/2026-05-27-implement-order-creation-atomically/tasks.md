## 1. Modelos y Base de Datos

- [x] 1.1 Crear modelo `EstadoPedido` en `backend/app/models/estado_pedido.py` con PK semántica VARCHAR(20), campos: codigo, descripcion, orden (INT), es_terminal (BOOL), created_at
- [x] 1.2 Crear modelo `FormaPago` en `backend/app/models/forma_pago.py` con PK semántica VARCHAR(20), campos: codigo, descripcion, habilitado (BOOL), created_at
- [x] 1.3 Crear modelo `Pedido` en `backend/app/models/pedido.py` con UUID PK, usuario_id FK, estado_codigo FK, direccion_id FK, forma_pago_codigo FK, direccion_snapshot TEXT, subtotal DECIMAL(10,2), costo_envio DECIMAL(10,2), total DECIMAL(10,2), notas TEXT, created_at, updated_at, soft_deleted_at. Relaciones con User, EstadoPedido, DireccionEntrega, FormaPago, DetallePedido, HistorialEstadoPedido
- [x] 1.4 Crear modelo `DetallePedido` en `backend/app/models/detalle_pedido.py` con UUID PK, pedido_id FK, producto_id FK, cantidad INT, precio_snapshot DECIMAL(10,2), nombre_snapshot VARCHAR(200), subtotal DECIMAL(10,2), personalizacion ARRAY(UUID), created_at
- [x] 1.5 Crear modelo `HistorialEstadoPedido` en `backend/app/models/historial_estado_pedido.py` con UUID PK, pedido_id FK, estado_desde VARCHAR(20) nullable, estado_nuevo VARCHAR(20) NOT NULL, actor_id UUID nullable, motivo TEXT nullable, created_at (append-only)
- [x] 1.6 Actualizar `backend/app/models/__init__.py` para exportar los 5 nuevos modelos
- [x] 1.7 Generar migración Alembic con `alembic revision --autogenerate -m "add_order_tables"` — debe incluir tablas: estado_pedido, forma_pago, pedido, detalle_pedido, historial_estado_pedido
- [x] 1.8 Crear script seed `backend/app/db/seed.py` con INSERT idempotente de 6 estados y 3 formas de pago

## 2. Módulo Pedidos — Capa de Datos

- [x] 2.1 Crear `backend/app/pedidos/__init__.py` que exporte router
- [x] 2.2 Crear `backend/app/pedidos/schemas.py` con: CrearPedidoRequest, ItemPedidoRequest, PedidoRead, DetallePedidoRead schemas Pydantic
- [x] 2.3 Crear `backend/app/pedidos/repository.py` con PedidoRepository: métodos create_pedido (sin commit — solo add+flush), create_detalle, create_historial, get_by_id
- [x] 2.4 Crear `backend/app/pedidos/service.py` con PedidoService:
  - Validar items (productos existen, disponibles, stock suficiente con SELECT FOR UPDATE)
  - Validar dirección (pertenece al usuario, existe)
  - Validar forma de pago (existe y habilitada)
  - Capturar snapshots (precio, nombre, dirección serializada)
  - Calcular subtotales, costo_envio (50.00), total
  - Crear pedido → flush → crear detalles → crear historial → commit
  - Rollback explícito en caso de error
  - Mapear a PedidoRead response
- [x] 2.5 Crear `backend/app/pedidos/router.py` con endpoint `POST /api/v1/pedidos` protegido con `require_role("CLIENT")`

## 3. Integración

- [x] 3.1 Registrar `pedidos_router` en `backend/app/main.py`
- [x] 3.2 Registrar nuevos modelos en `backend/app/models/__init__.py` (si no se hizo en 1.6)
- [x] 3.3 Verificar imports: ejecutar `python -c "from app.pedidos.router import router"` sin errores
- [x] 3.4 Ejecutar migración Alembic: `alembic upgrade head` y verificar con `openspec verify` que todo esté en orden
