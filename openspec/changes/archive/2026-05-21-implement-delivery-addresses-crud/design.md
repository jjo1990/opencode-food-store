## Context

Los usuarios registrados (rol CLIENT) necesitan gestionar direcciones de entrega para poder recibir pedidos. Actualmente el sistema no tiene ninguna entidad ni tabla para direcciones — el User model tiene `full_name` y `telefono` pero no direcciones. El Change 28 (order-creation-atomically) depende de tener direcciones funcionales.

El backend existente usa un patrón feature-first consistente:

- Cada módulo en `backend/app/<nombre>/` con `model.py`, `schemas.py`, `repository.py`, `service.py`, `router.py`
- Repos sincrónicos con `Session` directa (sin UnitOfWork ni BaseRepository genérico)
- Service stateless que recibe `db: Session`, crea repo internamente
- Router con `prefix` y `tags`, `response_model` explícito, `Depends(get_current_user)` o `require_role()`
- Autenticación vía JWT con `get_current_user` en `core.dependencies`
- Roles disponibles: CLIENT, ADMIN, STOCK, ORDER

## Goals / Non-Goals

**Goals:**

- CRUD completo de direcciones de entrega para usuarios autenticados
- Validación de ownership (solo el dueño puede ver/editar/eliminar sus direcciones)
- Flag `es_principal` con constraint de única principal por usuario
- Primera dirección creada se marca automáticamente como principal
- Soft delete (no destrucción física)
- Protección: no eliminar si es la única dirección del usuario

**Non-Goals:**

- Geocodificación o validación de direcciones reales contra servicios externos
- Direcciones compartidas entre usuarios (cada usuario tiene las suyas)
- Historial de cambios en direcciones
- Direcciones de facturación (solo entrega)

## Decisions

### 1. Modelo `DireccionEntrega` separado (no campos embedidos en User)

- **Decisión**: Tabla propia `direccion_entrega` con FK a `user.id`
- **Por qué**: Un usuario puede tener múltiples direcciones. Meterlas en User sería desnormalizado y rompería el modelo relacional. Además, cada dirección necesita sus propios timestamps de auditoría y soft delete.
- **Alternativa**: JSON column en User — descartado por falta de integridad referencial, no se puede hacer FK, no se puede consultar ni indexar eficientemente.

### 2. Partial unique index para `es_principal`

- **Decisión**: Index único `(usuario_id, es_principal)` con condición `WHERE es_principal = true`
- **Por qué**: Garantiza a nivel BD que un usuario tenga exactamente UNA dirección principal. No se puede lograr con UNIQUE CONSTRAINT tradicional porque `es_principal` es booleano y queremos permitir múltiples `false`.
- **Implementación**: `Index("ix_direccion_principal", "usuario_id", "es_principal", unique=True, postgresql_where=text("es_principal = true"))`

### 3. Soft delete lógico

- **Decisión**: Columna `soft_deleted_at` nullable, misma convención que el resto de modelos
- **Por qué**: Consistencia con todos los demás modelos del proyecto (Categoria, Ingrediente, Producto, User). El repo excluye automáticamente registros con `soft_deleted_at IS NOT NULL`.

### 4. Ownership en service layer

- **Decisión**: El service verifica que `direccion.usuario_id == current_user.id` antes de cualquier operación
- **Por qué**: Los endpoints son multi-tenant por usuario. No queremos que un usuario vea direcciones de otro. La validación en service (no en router) permite reuso y testeo.

### 5. Sync repos (mismo patrón existente)

- **Decisión**: Repository sincrónico con `Session` directa, igual que `usuarios/repository.py` y `categorias/repository.py`
- **Por qué**: Consistencia con el código existente. Aunque los routers son async, los repos existentes son sync con inyección de Session.

## Risks / Trade-offs

| Riesgo                                                                                                           | Mitigación                                                                                                                                                              |
| ---------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Condición de carrera al marcar dirección como principal (dos requests simultáneos podrían crear dos principales) | El partial unique index en BD rechazará el segundo INSERT/UPDATE con error de unique violation. El service debe capturar `IntegrityError` y responder con 409 Conflict. |
| Usuario elimina su única dirección y se queda sin direcciones para pedidos                                       | Validación en service: si es la única dirección activa, rechazar DELETE con 400 Bad Request y mensaje claro.                                                            |
| Migración de tabla existente sin datos                                                                           | Es una tabla nueva, no hay datos que migrar. La migración es straightforward `CREATE TABLE`.                                                                            |
