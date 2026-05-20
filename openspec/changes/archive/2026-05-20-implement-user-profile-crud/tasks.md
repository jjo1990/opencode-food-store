# Tasks: implement-user-profile-crud

## 1. Module Setup

- [x] 1.1 Create `backend/app/usuarios/` package with `__init__.py`
- [x] 1.2 Create `backend/app/usuarios/schemas.py` — ProfileUpdateRequest (full_name opcional, telefono opcional), PasswordChangeRequest (current_password, new_password), UserProfileResponse (id, email, full_name, telefono, roles, created_at)
- [x] 1.3 Create `backend/app/usuarios/repository.py` — UserProfileRepository con métodos: `update_profile(user_id, data)`, `soft_delete_user(user_id)`, `invalidate_refresh_tokens(user_id)`, sin BaseRepository (no existe en codebase real)
- [x] 1.4 Create `backend/app/usuarios/service.py` — UserProfileService: get_profile, update_profile, change_password, delete_account. Implementa lógica de cambio de contraseña (verificar actual con argon2, hashear nueva, invalidar refresh tokens)
- [x] 1.5 Create `backend/app/usuarios/router.py` — 4 endpoints: GET /me, PUT /me, PUT /me/contrasena, DELETE /me, todos protegidos con get_current_user. DELETE solo para CLIENT (require_role("CLIENT"))

## 2. Auth Schema Update

- [x] 2.1 Modify `backend/app/auth/schemas.py` — agregar `telefono: str | None = None` al `UserResponse`

## 3. Router Registration

- [x] 3.1 Register `usuarios.router` in `backend/app/main.py` under prefix `/api/v1/usuarios`

## 4. Tests

- [x] 4.1 Create `backend/tests/test_usuarios_profile.py` — test GET /me (autenticado, no autenticado), PUT /me (actualización exitosa, parcial, validación nombre), PUT /me/contrasena (éxito, contraseña incorrecta, nueva corta), DELETE /me (CLIENT success, ADMIN 403, no auth 401)

## 5. Verification

- [x] 5.1 Run tests: `python -m pytest backend/tests/test_usuarios_profile.py -v`
- [x] 5.2 Verify all imports in new modules
