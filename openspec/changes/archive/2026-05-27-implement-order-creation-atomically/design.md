## Context

El sistema actual tiene catálogo, carrito y validación checkout, pero no puede crear pedidos. No existen las tablas de pedidos, ni los modelos, ni el módulo. Tampoco existen los catálogos `EstadoPedido` y `FormaPago` (requeridos como FK en Pedido).

La creación de un pedido es la primera operación verdaderamente transaccional del sistema: involucra inserts en 3 tablas (pedido, detalle_pedido, historial_estado_pedido), validación contra productos y direcciones del usuario, captura de snapshots, y debe ser atómica — o todo persiste o nada.

**State actual:**

- No existen modelos ni tablas para pedidos
- Cada repositorio existente hace `self.db.commit()` inline (sin Unit of Work)
- Los catálogos EstadoPedido y FormaPago nunca se crearon

## Goals / Non-Goals

**Goals:**

- Crear las 5 tablas del Dominio 3 (ERD v5): estado_pedido, forma_pago, pedido, detalle_pedido, historial_estado_pedido
- Implementar seed data para estado_pedido (6 registros) y forma_pago (3 registros)
- Implementar `POST /api/v1/pedidos` con transacción atómica
- Aplicar patrón snapshot: precio_snapshot, nombre_snapshot en DetallePedido, direccion_snapshot en Pedido
- Calcular subtotal, costo_envio (fijo ARS 50), total
- Registrar historial inicial con estado_desde=NULL (RN-02)

**Non-Goals:**

- Transiciones de estado posteriores a PENDIENTE (eso va en Change 34 — FSM)
- Endpoints GET /api/v1/pedidos (Change 29)
- Pago (Phase 6)
- Interfaz frontend (Change 30)
- Tests unitarios (Change 48)

## Decisions

### 1. Estados y Formas de Pago como tablas catálogo con PK semántica

**Decisión**: `estado_pedido.codigo` y `forma_pago.codigo` son `VARCHAR(20)` PK — no UUID.
**Por qué**: El ERD v5 especifica PKs semánticas para catálogos. Los códigos (`PENDIENTE`, `MERCADOPAGO`) son legibles en queries, FK y logs sin joins. El seed define 6 estados y 3 formas de pago con IDs estables.
**Alternativa descartada**: UUIDs en catálogos — agrega joins innecesarios para datos que nunca cambian.

### 2. direccion_snapshot como JSON string en Pedido

**Decisión**: La dirección de entrega se serializa a JSON y se almacena como `TEXT` en el campo `direccion_snapshot` del pedido.
**Por qué**: El usuario puede modificar o eliminar su dirección después de crear el pedido. El snapshot garantiza que el pedido preserve la dirección exacta al momento de creación. Usar `TEXT` con JSON es simple y no requiere schema adicional.
**Alternativa descartada**: Tabla separada de snapshots — overkill para un solo snapshot.

### 3. Transacción atómica sin UnitOfWork class separada

**Decisión**: El PedidoService orquesta la transacción llamando `self.db.commit()` al final, y `self.db.rollback()` en caso de error. Los métodos del repositorio que participan en la transacción NO hacen commit (usan `self.db.flush()` para obtener IDs sin persistir).
**Por qué**: No existe una clase UnitOfWork en el código actual (es un patrón aspiracional). Introducir una ahora para un solo endpoint agregaría complejidad sin beneficio inmediato. El session de SQLAlchemy ya es transactional. Si en el futuro hay más operaciones transaccionales complejas, se puede extraer un UoW.
**Riesgo mitigado**: El `get_db()` de FastAPI cierra la session al final del request. Si hay una excepción, el session descarta cambios no commiteados.

### 4. SELECT ... FOR UPDATE en validación de stock

**Decisión**: Al validar stock, usar `with_for_update()` de SQLAlchemy para bloquear el row del producto hasta que termine la transacción.
**Por qué**: Previene race conditions donde dos pedidos simultáneos validan stock suficiente y ambos pasan, pero el stock real es insuficiente para ambos.
**Nota**: Requiere que la transacción esté activa (sesión no cerrada entre validación y commit).

### 5. personalizacion como ARRAY(UUID) en DetallePedido

**Decisión**: El campo `personalizacion` es un `ARRAY(UUID)` de PostgreSQL — almacena los IDs de ingredientes removidos.
**Por qué**: Coincide con el ERD v5 (INTEGER[] adaptado a UUID[] porque el proyecto usa UUIDs). Es un array inmutable que se lee siempre como un todo. No necesita tabla intermedia.
**Alternativa descartada**: Tabla intermedia DetallePedidoIngrediente — sobreingeniería para datos anexos.

## Risks / Trade-offs

| Riesgo                                                                 | Mitigación                                                                                                                             |
| ---------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| Deadlock si dos pedidos bloquean los mismos productos simultáneamente  | SELECT FOR UPDATE usa NOWAIT en PostgreSQL — si hay lock, falla rápido con error manejable                                             |
| direccion_snapshot en JSON no valida schema                            | El schema Pydantic `DireccionSnapshot` asegura que el JSON tenga estructura correcta antes de serializar                               |
| Sin UoW explícito, error a mitad de transacción deja cambios parciales | Try/except con rollback explícito en el service. El get_db() de FastAPI también hace close() que descarta transacciones no commiteadas |
| Seed data puede corromperse si se ejecuta múltiples veces              | Usar `INSERT ... ON CONFLICT DO NOTHING` para idempotencia                                                                             |

## Migration Plan

1. Generar migración Alembic: `alembic revision --autogenerate -m "add_order_tables"`
2. Verificar que el upgrade crea tablas en orden correcto (catálogos primero, luego tablas con FK)
3. Ejecutar: `alembic upgrade head`
4. El seed se ejecuta como script independiente (`python -m app.db.seed`) o integrado en un endpoint de setup

## Open Questions

- ¿El seed debe ser un script independiente o parte de la migración? Por ahora script independiente, consistente con el Change 4 de Phase 0 que nunca se implementó como tal.
- `costo_envio`: ¿valor fijo ARS 50 o debe ser configurable? Por ahora fijo, v1. Se hará configurable en Change 44.
