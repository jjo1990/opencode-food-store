## Context

El módulo `admin/` existe con 2 endpoints de roles (`PUT /admin/users/{id}/roles`, `DELETE /admin/users/{id}/roles/{role}`) y el service correspondiente. El `auth/repository.py` ya tiene métodos para CRUD básico de usuarios y roles. No existe `admin/schemas.py` ni `admin/repository.py`. El frontend AdminUsersPage es placeholder.

El modelo `User` tiene `soft_deleted_at` para baja lógica. Los roles se manejan vía tabla `UserRole` (M:M). Los refresh tokens se almacenan en `RefreshToken` con soporte de revocación por usuario.

## Goals / Non-Goals

**Goals:**

- Backend completo de gestión admin de usuarios: listar, buscar, ver detalle, editar, desactivar/reactivar
- Protección: solo ADMIN accede, no se puede eliminar al último admin
- Invalidación de sesión al cambiar roles (revocar refresh tokens)

**Non-Goals:**

- Frontend UI (Change 42)
- Gestión de productos, pedidos, métricas (Changes 38-44)
- Tests automatizados (Change 48)

## Decisions

### 1. Paginación con page/size (no skip/limit)

- **Decisión**: Usar `page` y `size` como parámetros de query (1-indexed), retornar `{ items, total, page, size, pages }`.
- **Por qué**: Más intuitivo para el frontend que maneja páginas, no offsets. Consistente con APIs públicas modernas.
- **Alternativa**: skip/limit — más eficiente en BD pero menos amigable para UI.

### 2. Filtros combinados vía query params

- **Decisión**: `rol` (string exacto), `search` (ILIKE sobre email y full_name), `estado` ("activo"|"inactivo"|"todos").
- **Por qué**: Sinergia simple, evita body en GET. ILIKE es suficientemente rápido con índices existentes en email.
- **Alternativa**: Filtro por JSON body (POST) — rompe semántica REST, overkill para este caso.

### 3. Endpoint PUT para update completo

- **Decisión**: PUT reemplaza todos los campos enviados. Roles se reemplazan completamente (no PATCH parcial).
- **Por qué**: Más simple y predecible. PUT /users/{id} recibe `{ full_name, email, telefono, roles }` y actualiza todo. Para cambios parciales, el frontend puede leer primero y enviar el estado completo.
- **Nota**: Si solo se quieren cambiar roles, el frontend usa el endpoint existente `PUT /admin/users/{id}/roles`.

### 4. Soft delete, no hard delete

- **Decisión**: DELETE marca `soft_deleted_at`, no borra el registro. PATCH /reactivar lo limpia.
- **Por qué**: Consistente con el modelo User existente. Los soft-delete conservan integridad referencial (pedidos, pagos del usuario siguen siendo consultables).
- **Riesgo**: Usuario soft-deleteado no puede hacer login (filtrado en `get_user_by_email`).

### 5. Invalidación de tokens en el service

- **Decisión**: Al cambiar roles (PUT /users/{id}), el service llama a `RefreshTokenRepository.revoke_all_user_tokens(user_id)`.
- **Por qué**: El JWT actual del usuario contiene los roles viejos. Forzar re-login garantiza que el nuevo JWT refleje los roles actualizados.
- **Riesgo**: UX ligeramente peor (el admin force-logout al usuario), pero necesario para seguridad.

## API Contract

### `GET /api/v1/admin/usuarios`

Query params: `page` (default 1), `size` (default 20, max 100), `rol` (opcional), `search` (opcional), `estado` ("activo" default, "inactivo", "todos")

Response 200:

```json
{
  "items": [
    {
      "id": "uuid",
      "email": "user@example.com",
      "full_name": "John Doe",
      "telefono": "+541112345678",
      "roles": ["CLIENT"],
      "activo": true,
      "created_at": "2026-01-01T00:00:00Z"
    }
  ],
  "total": 42,
  "page": 1,
  "size": 20,
  "pages": 3
}
```

### `GET /api/v1/admin/usuarios/{user_id}`

Response 200: Igual que item pero con `soft_deleted_at` incluido.
Response 404: Usuario no encontrado.

### `PUT /api/v1/admin/usuarios/{user_id}`

Request body:

```json
{
  "full_name": "Updated Name",
  "email": "newemail@example.com",
  "telefono": "+541111111111",
  "roles": ["CLIENT", "ADMIN"]
}
```

Todos los campos opcionales (solo se actualizan los enviados). Roles se reemplazan completamente.

Response 200: User actualizado.
Response 403: Si se intenta remover ADMIN del último admin.
Response 404: Usuario no encontrado.

### `DELETE /api/v1/admin/usuarios/{user_id}`

Response 200: `{ "mensaje": "Usuario desactivado correctamente" }`
Response 403: No se puede desactivar al último ADMIN.
Response 404: Usuario no encontrado.

### `PATCH /api/v1/admin/usuarios/{user_id}/reactivar`

Response 200: Usuario reactivado.
Response 404: Usuario no encontrado o no estaba desactivado.

## Risks / Trade-offs

| Risk                                                   | Mitigation                                                                                                                              |
| ------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------- |
| Un admin malintencionado puede desactivar otros admins | Protección: no se puede desactivar al último ADMIN. Queda audit trail via HistorialEstadoPedido (para otras operaciones).               |
| Cambio de roles deja JWTs inválidos hasta que expiren  | Se revocan refresh tokens del usuario inmediatamente. El access token (30 min) sigue válido pero el refresh fallará, forzando re-login. |
| ILIKE search es lento en tablas grandes                | El índice en email ya existe. Para full_name se puede agregar índice si es necesario. Con <100K usuarios no debería ser problema.       |
