## Context

El sistema ya tiene:

- Modelos `Pedido`, `EstadoPedido`, `HistorialEstadoPedido`, `DetallePedido`
- `PedidoService` con métodos `crear_pedido()`, `listar_pedidos()`, `obtener_pedido()`
- `PedidoRepository` con `create_historial()`, `commit()`, `rollback()`
- Webhook que cambia PENDIENTE → CONFIRMADO (Change 32)

Lo que falta: un mecanismo centralizado para transiciones manuales con validación de reglas de negocio.

## Goals / Non-Goals

**Goals:**

- Método `avanzar_estado()` con mapa de transiciones hardcodeado
- Validación de roles por transición (CLIENT, ADMIN, PEDIDOS)
- Regla especial: PENDIENTE → CONFIRMADO solo vía webhook (excluido del endpoint)
- Restauración de stock al cancelar desde CONFIRMADO o EN_PREPARACIÓN
- Registro de historial en cada transición
- Endpoint `PATCH /api/v1/pedidos/{id}/avanzar`

**Non-Goals:**

- No se implementa frontend (eso es Change 30 + 43)
- No se implementa el webhook (Change 32)
- No se modifica `POST /api/v1/pedidos` existente

## Decisions

### Decision 1: Mapa de transiciones hardcodeado como dict

```python
TRANSITIONS = {
    "PENDIENTE": {
        "CONFIRMADO": {"roles": [], "stock": None},  # Solo webhook
        "CANCELADO": {"roles": ["CLIENT", "ADMIN", "PEDIDOS"], "stock": None},
    },
    "CONFIRMADO": {
        "EN_PREPARACION": {"roles": ["ADMIN", "PEDIDOS"], "stock": None},
        "CANCELADO": {"roles": ["CLIENT", "ADMIN", "PEDIDOS"], "stock": "restore"},
    },
    "EN_PREPARACION": {
        "EN_CAMINO": {"roles": ["ADMIN", "PEDIDOS"], "stock": None},
        "CANCELADO": {"roles": ["ADMIN"], "stock": "restore"},
    },
    "EN_CAMINO": {
        "ENTREGADO": {"roles": ["ADMIN", "PEDIDOS"], "stock": None},
    },
    "ENTREGADO": {},  # Terminal
    "CANCELADO": {},  # Terminal
}
```

**Alternativa considerada**: Tabla en BD con configuración de transiciones.
**Descartada por**: Overkill para 6 estados con reglas estables. El mapa hardcodeado es más legible y testeable.

### Decision 2: PENDIENTE → CONFIRMADO bloqueado en endpoint

El endpoint `avanzar` rechaza explícitamente la transición a CONFIRMADO. Solo el webhook (Change 32) puede hacer ese cambio. Esto implementa RN-02 del diseño.

### Decision 3: Restauración de stock atómica

Al cancelar desde CONFIRMADO o EN_PREPARACIÓN, se debe restaurar el stock de cada producto del pedido usando `SELECT ... FOR UPDATE` para evitar race conditions, exactamente como se hace en el webhook para decrementar.

### Decision 4: Un solo endpoint PATCH /avanzar

En lugar de tener `/cancelar` separado, se usa un solo endpoint `PATCH /pedidos/{id}/avanzar` que recibe `{ nuevo_estado, motivo? }`. La cancelación es simplemente una transición a CANCELADO con su propia validación de roles.

## Risks / Trade-offs

| Risk                                                                   | Mitigation                                                                             |
| ---------------------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| **Race condition**: dos admins avanzan el mismo pedido simultáneamente | La transacción y el check de estado actual dentro del método evitan doble avance       |
| **Stock negativo**: restauración duplicada                             | Cada transición es única — no se puede CANCELAR dos veces porque CANCELADO es terminal |
| **Transición inválida**: alguien intenta EN_CAMINO → CONFIRMADO        | El mapa de transiciones solo permite las válidas                                       |

## Mapa de transiciones

```
PENDIENTE ──────→ CONFIRMADO (solo webhook)
PENDIENTE ──────→ CANCELADO (CLIENT, ADMIN, PEDIDOS)

CONFIRMADO ─────→ EN_PREPARACIÖN (ADMIN, PEDIDOS)
CONFIRMADO ─────→ CANCELADO + restaurar stock (CLIENT, ADMIN, PEDIDOS)

EN_PREPARACIÖN ─→ EN_CAMINO (ADMIN, PEDIDOS)
EN_PREPARACIÖN ─→ CANCELADO + restaurar stock (solo ADMIN)

EN_CAMINO ──────→ ENTREGADO (ADMIN, PEDIDOS)

ENTREGADO ──────→ (terminal)
CANCELADO ──────→ (terminal)
```
