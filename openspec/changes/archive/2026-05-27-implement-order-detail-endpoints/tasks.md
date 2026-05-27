## 1. Repositorio — Métodos de Lectura

- [x] 1.1 Agregar `get_by_id(id: UUID) -> Pedido | None` en PedidoRepository con `selectinload` de `detalles` e `historial`, filtrando soft_deleted
- [x] 1.2 Agregar `get_by_user(user_id: UUID, skip: int, limit: int, estado_codigo: str | None) -> list[Pedido]` con filtro soft_deleted, ordenado por created_at DESC
- [x] 1.3 Agregar `get_all(skip: int, limit: int, estado_codigo: str | None) -> list[Pedido]` para ADMIN/PEDIDOS, con filtro soft_deleted
- [x] 1.4 Agregar `count_by_user(user_id: UUID, estado_codigo: str | None) -> int`
- [x] 1.5 Agregar `count_all(estado_codigo: str | None) -> int`

## 2. Schemas — Response de Listado y Detalle

- [x] 2.1 Agregar `PedidoListRead` en schemas.py: id, estado_codigo, total, created_at (compacto para listados)
- [x] 2.2 Agregar `HistorialRead` en schemas.py: estado_desde, estado_nuevo, actor_id, motivo, created_at
- [x] 2.3 Actualizar `PedidoDetail` en schemas.py para incluir: items list[DetallePedidoRead], historial list[HistorialRead], y datos del pedido

## 3. Service — Lógica de Lectura

- [x] 3.1 Agregar `listar_pedidos(user: User, skip: int, limit: int, estado_codigo: str | None) -> dict` con role-aware filtering (CLIENT vs ADMIN/PEDIDOS)
- [x] 3.2 Agregar `obtener_pedido(user: User, pedido_id: UUID) -> PedidoDetail` con ownership check y eager loading

## 4. Router — Endpoints

- [x] 4.1 Agregar `GET /api/v1/pedidos` con query params skip, limit, estado_codigo, protegido con `get_current_user`
- [x] 4.2 Agregar `GET /api/v1/pedidos/{id}` con path param UUID, protegido con `get_current_user`

## 5. Verificación

- [x] 5.1 Verificar imports: `python -c "from app.pedidos.router import router"` sin errores
