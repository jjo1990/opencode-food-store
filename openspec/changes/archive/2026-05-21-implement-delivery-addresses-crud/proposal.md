## Why

Los usuarios registrados necesitan poder gestionar sus direcciones de entrega para recibir pedidos. Actualmente no existe ninguna entidad de dirección en el sistema — el modelo User tiene campos básicos pero no soporta múltiples direcciones por usuario, ni la capacidad de marcar una como principal. Sin esto, el flujo de creación de pedidos (Change 28) no puede funcionar, ya que cada pedido requiere una dirección de entrega válida.

## What Changes

- Nuevo modelo `DireccionEntrega` con FK a `User`, campos de dirección completa, flag `es_principal`, timestamps de auditoría y soft delete
- Módulo `backend/app/direcciones/` completo con: `model.py`, `schemas.py`, `repository.py`, `service.py`, `router.py`
- **POST /api/v1/direcciones** — crear dirección (la primera se marca automáticamente como principal)
- **GET /api/v1/direcciones** — listar direcciones del usuario autenticado
- **GET /api/v1/direcciones/{id}** — detalle de dirección (verifica ownership)
- **PUT /api/v1/direcciones/{id}** — modificar dirección (solo propietario)
- **PATCH /api/v1/direcciones/{id}/principal** — establecer como principal (desactiva la anterior)
- **DELETE /api/v1/direcciones/{id}** — soft delete (solo propietario, no se puede eliminar si es la única)
- Validaciones: solo una principal por usuario, primera dirección siempre es principal
- Migración Alembic para tabla `direccion_entrega`
- Todos los endpoints autenticados y protegidos con rol CLIENT

## Capabilities

### New Capabilities

- `delivery-addresses`: CRUD completo de direcciones de entrega del usuario autenticado, con validación de ownership, flag de principal, y soft delete

### Modified Capabilities

- _(ninguna — no hay specs existentes que modificar)_

## Impact

- **Backend**: Nuevo módulo `backend/app/direcciones/` (~6 archivos), nuevo modelo `DireccionEntrega` en `backend/app/models/`, registro en `main.py`
- **Base de datos**: Nueva migración Alembic con tabla `direccion_entrega`, FK a `user.id`, unique partial index sobre `(usuario_id, es_principal)` donde `es_principal = true`
- **Dependencias activas**: `implement-user-profile-crud` ✅ (ya archivado) — los usuarios existen y tienen autenticación funcional
- **No breaking**: no modifica APIs existentes
