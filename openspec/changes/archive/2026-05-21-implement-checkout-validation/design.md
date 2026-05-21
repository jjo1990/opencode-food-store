## Context

El backend tiene módulos de productos y direcciones funcionales. El frontend tiene carrito con items (cartStore). Falta un paso de validación antes de la creación del pedido (Change 28).

El patrón de módulos backend:

- `schemas.py` → Pydantic request/response
- `service.py` → lógica de negocio
- `router.py` → endpoints
- `__init__.py` → export router

## Goals / Non-Goals

**Goals:**

- Validar items del carrito contra el backend
- Detectar productos inexistentes, no disponibles, sin stock
- Validar personalizaciones (ingredientes removidos deben ser válidos y removibles)
- Detectar cambios de precio (precio snapshot vs precio actual)
- Respuesta estructurada con errores y advertencias separados
- Endpoint público (no requiere auth, para facilitar llamadas desde frontend)

**Non-Goals:**

- Crear pedido (Change 28)
- Reservar stock (solo lectura)
- Validar dirección de entrega (se hace en order creation)
- Calcular costos de envío

## Decisions

### 1. Módulo `checkout/` separado

- **Decisión**: Crear `backend/app/checkout/` en vez de ponerlo en `pedidos/`
- **Por qué**: El módulo pedidos aún no existe (se crea en Change 28). Checkout es conceptualmente independiente: es validación pre-pedido. Separarlos mantiene cada módulo enfocado.
- **Alternativa**: Ponerlo en pedidos/ — descartado porque crearía dependencias adelantadas.

### 2. Endpoint sin autenticación

- **Decisión**: `POST /api/v1/checkout/validar` sin `Depends(get_current_user)`
- **Por qué**: La validación de carrito no necesita saber quién es el usuario. Solo necesita los datos del item. El frontend puede llamarlo incluso en modo anónimo.
- **Alternativa**: Con autenticación — innecesario para esta validación. La autenticación se requerirá en order creation (Change 28).

### 3. Validación item por item con reporte completo

- **Decisión**: Validar TODOS los items, retornar errores y advertencias de TODOS en una sola respuesta (no detenerse en el primer error)
- **Por qué**: UX mejor — el usuario ve todos los problemas de una vez en vez de tener que corregir uno por uno.
- **Alternativa**: Fail-fast en el primer error — peor experiencia de usuario.

### 4. Precio snapshot vs actual como advertencia

- **Decisión**: Si el precio_base actual difiere del precio que el carrito muestra, se retorna una advertencia (no error)
- **Por qué**: El precio puede cambiar entre que el usuario agrega al carrito y checkout. Queremos informar pero no bloquear. El usuario decide si acepta el nuevo precio.

## Risks / Trade-offs

| Riesgo                                                                   | Mitigación                                                                                                    |
| ------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------- |
| Condición de carrera: stock cambia entre validación y creación de pedido | La validación es solo lectura. El stock real se verifica con SELECT FOR UPDATE en order creation (Change 28). |
| Items duplicados en el request (mismo producto + personalización)        | El service debe agrupar cantidades de items duplicados antes de validar.                                      |
| Muchos items (ej: 50) en un solo request                                 | Timeout normal de request. La validación es O(n) con queries individuales. Para v1 no hay límite.             |
