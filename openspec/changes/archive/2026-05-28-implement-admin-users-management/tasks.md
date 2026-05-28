## 1. Schemas y Repository

- [x] 1.1 Crear `admin/schemas.py` con `AdminUserResponse`, `AdminUserListResponse`, `AdminUserUpdateRequest`
- [x] 1.2 Crear `admin/repository.py` con métodos: `list_users(page, size, rol, search, estado)`, `get_user_by_id_including_deleted(user_id)`, `soft_delete_user(user_id)`, `reactivate_user(user_id)`

## 2. Service

- [x] 2.1 Agregar `list_users(page, size, rol, search, estado)` a `AdminService`
- [x] 2.2 Agregar `get_user_detail(user_id)` a `AdminService`
- [x] 2.3 Agregar `update_user(user_id, data)` a `AdminService` (actualiza campos + roles, revoca refresh tokens si roles cambiaron)
- [x] 2.4 Agregar `deactivate_user(user_id)` a `AdminService` (protege último ADMIN)
- [x] 2.5 Agregar `reactivate_user(user_id)` a `AdminService`

## 3. Router

- [x] 3.1 Agregar `GET /admin/usuarios` con paginación y filtros
- [x] 3.2 Agregar `GET /admin/usuarios/{user_id}` con detalle
- [x] 3.3 Agregar `PUT /admin/usuarios/{user_id}` para actualización completa
- [x] 3.4 Agregar `DELETE /admin/usuarios/{user_id}` para soft delete
- [x] 3.5 Agregar `PATCH /admin/usuarios/{user_id}/reactivar` para restaurar

## 4. Verificación

- [x] 4.1 Verificar que el servidor FastAPI inicia sin errores de import
- [x] 4.2 Verificar que los endpoints responden correctamente
