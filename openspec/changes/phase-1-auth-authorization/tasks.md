# PHASE 1: Autenticación y Autorización — Tasks

## Estructura General

- **8 mega-tasks** (uno per change)
- Cada mega-task tiene **subtasks** (lo que realmente laburás)
- Marcá cada subtask como completa cuando termines

---

## CHANGE #8: Registro de Usuario (`auth-user-registration`)

**Dependencia**: Change #5 (Pattern base)
**Estimación**: 2-3 horas
**Status**: [ ] Pendiente

### Subtasks

#### Backend

- [ ] Crear `backend/app/auth/schemas.py`
  - [ ] `RegisterRequest` con `email`, `password`, `full_name`
  - [ ] Validar `email` (RFC 5322)
  - [ ] Validar `password` >= 8 chars
  - [ ] `UserResponse` con `id`, `email`, `roles`

- [ ] Crear `backend/app/auth/service.py`
  - [ ] `register(email, password, full_name)` service
  - [ ] Validar email único (query User por email)
  - [ ] Hash password con Argon2
  - [ ] Crear User + asignar rol CLIENT automático
  - [ ] Retornar UserResponse

- [ ] Crear `backend/app/auth/repository.py`
  - [ ] `UserRepository` heredar de BaseRepository[User]
  - [ ] `create_user(email, hashed_pwd, full_name)` → User
  - [ ] `get_user_by_email(email)` → User | None
  - [ ] `assign_role(user_id, role)` → UserRole

- [ ] Actualizar `backend/app/models/` (si no está)
  - [ ] `User` model con `id`, `email`, `hashed_password`, `full_name`, `telefono`, `created_at`, `soft_deleted_at`
  - [ ] `UserRole` model con `user_id`, `role`, `assigned_at`
  - [ ] Relaciones: `User.roles` ← → `UserRole.user`

- [ ] Crear `backend/app/auth/router.py`
  - [ ] `POST /api/v1/auth/register` endpoint
  - [ ] Recibir `RegisterRequest`
  - [ ] Llamar `service.register()`
  - [ ] Response 201 + UserResponse
  - [ ] Error 409 si email duplicado
  - [ ] Error 422 si validaciones fallan

- [ ] Actualizar `backend/app/main.py`
  - [ ] Importar y registrar auth router
  - [ ] `app.include_router(auth_router, prefix="/api/v1")`

#### Database

- [ ] Crear migración Alembic
  - [ ] `alembic revision --autogenerate -m "Add User and UserRole tables"`
  - [ ] Validar que genere las tablas correctas
  - [ ] `alembic upgrade head`

#### Testing

- [ ] Crear `backend/tests/test_auth_register.py`
  - [ ] Test 201 OK con datos válidos
  - [ ] Test 409 si email duplicado
  - [ ] Test 422 si contraseña < 8 chars
  - [ ] Test 422 si email inválido
  - [ ] Test que usuario creado tiene rol CLIENT
  - [ ] Test que contraseña fue hasheada (nunca guardar limpia)
  - [ ] Run: `pytest tests/test_auth_register.py -v`

---

## CHANGE #9: Login con Rate Limiting (`auth-user-login-rate-limiting`)

**Dependencia**: Change #8
**Estimación**: 3-4 horas
**Status**: [ ] Pendiente

### Subtasks

#### Backend

- [ ] Actualizar `backend/app/core/config.py`
  - [ ] `JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")`
  - [ ] `JWT_ALGORITHM = "HS256"`
  - [ ] `ACCESS_TOKEN_EXPIRE_MINUTES = 30`
  - [ ] `REFRESH_TOKEN_EXPIRE_DAYS = 7`

- [ ] Actualizar `backend/app/core/security.py`
  - [ ] `create_access_token(user_id, roles, exp_minutes=30)` → JWT string
  - [ ] `create_refresh_token(user_id, family_id)` → (token, token_hash)
  - [ ] Usar `jwt.encode()` con HS256
  - [ ] Usar `hashlib.sha256()` para hash del refresh token

- [ ] Crear `backend/app/auth/schemas.py` (actualizar si existe)
  - [ ] `LoginRequest` con `email`, `password`
  - [ ] `TokenResponse` con `access_token`, `refresh_token`, `expires_in`, `token_type`

- [ ] Crear/actualizar `backend/app/auth/service.py`
  - [ ] `login(email, password)` service
  - [ ] Buscar usuario por email
  - [ ] Si no existe → error 401 genérico
  - [ ] Comparar password con hash
  - [ ] Si falla → error 401 genérico (igual mensaje, por seguridad)
  - [ ] Si OK → crear access + refresh tokens
  - [ ] Crear `RefreshToken` en BD
  - [ ] Retornar `TokenResponse`

- [ ] Crear `backend/app/auth/repository.py` (actualizar si existe)
  - [ ] `RefreshTokenRepository` heredar BaseRepository[RefreshToken]
  - [ ] `create_refresh_token(user_id, token_hash, family_id, expires_at)` → RefreshToken
  - [ ] `get_refresh_token_by_hash(token_hash)` → RefreshToken | None
  - [ ] `revoke_refresh_token(token_id)` → marca revoked_at

- [ ] Actualizar `backend/app/models/`
  - [ ] `RefreshToken` model: `id`, `user_id`, `token_hash`, `family_id`, `created_at`, `expires_at`, `revoked_at`

- [ ] Actualizar `backend/app/auth/router.py`
  - [ ] `POST /api/v1/auth/login` endpoint
  - [ ] Recibir `LoginRequest`
  - [ ] Aplicar rate limiter (slowapi): 5 intentos / 15 min
  - [ ] Llamar `service.login()`
  - [ ] Response 200 + TokenResponse
  - [ ] Error 401 genérico (no diferenciar email vs pwd)
  - [ ] Error 429 si rate limited

#### Database

- [ ] Crear migración para tabla `RefreshToken`
  - [ ] `alembic revision --autogenerate -m "Add RefreshToken table"`
  - [ ] Incluir índice en `(user_id, revoked_at)`
  - [ ] `alembic upgrade head`

#### Testing

- [ ] Crear `backend/tests/test_auth_login.py`
  - [ ] Test 200 OK con credenciales válidas
  - [ ] Test 401 si email no existe
  - [ ] Test 401 si password incorrecto
  - [ ] Test que no diferencia "email no existe" vs "pwd incorrecto" (mismo error 401)
  - [ ] Test que tokens están en response
  - [ ] Test 429 después de 5 intentos fallidos en 15 min
  - [ ] Test que access token expira en 30 min
  - [ ] Test que refresh token en BD está hasheado
  - [ ] Run: `pytest tests/test_auth_login.py -v`

---

## CHANGE #10: Refresh Token con Rotación (`auth-token-refresh-rotation`)

**Dependencia**: Change #9
**Estimación**: 2-3 horas
**Status**: [ ] Pendiente

### Subtasks

#### Backend

- [ ] Actualizar `backend/app/core/security.py`
  - [ ] `decode_token(token, secret)` → dict o raise
  - [ ] Validar firma JWT
  - [ ] Validar expiración
  - [ ] Manejar excepciones: ExpiredSignatureError, InvalidTokenError

- [ ] Actualizar `backend/app/core/dependencies.py`
  - [ ] `get_current_user(token: str = Depends(HTTPBearer()))` dependency
  - [ ] Decodificar JWT
  - [ ] Buscar usuario en BD
  - [ ] Si no existe → 401
  - [ ] Retornar Usuario (objeto completo con roles)

- [ ] Actualizar `backend/app/auth/service.py`
  - [ ] `refresh_tokens(refresh_token_string)` service
  - [ ] Validar refresh token (decodificar hash y buscar en BD)
  - [ ] Si no existe, expirado o revocado → 401
  - [ ] **REPLAY DETECTION**: Si detecta que el token fue revocado Y no es nueva emisión
    - [ ] Query todos los RefreshToken con mismo family_id
    - [ ] Revocar TODOS (marcar revoked_at)
    - [ ] Lanzar error 401 "Posible acceso no autorizado"
  - [ ] Si OK → crear nuevos access + refresh tokens
  - [ ] Revocar token anterior
  - [ ] Retornar TokenResponse

- [ ] Actualizar `backend/app/auth/repository.py`
  - [ ] `get_active_refresh_tokens_by_family(family_id)` → list[RefreshToken]
  - [ ] `revoke_all_by_family(family_id)` → marcar todos revoked_at

- [ ] Actualizar `backend/app/auth/router.py`
  - [ ] `POST /api/v1/auth/refresh` endpoint
  - [ ] Recibir body con `refresh_token`
  - [ ] Llamar `service.refresh_tokens()`
  - [ ] Response 200 + TokenResponse (nuevos tokens)
  - [ ] Error 401 si token inválido/expirado/revocado/replay detectado

#### Testing

- [ ] Crear `backend/tests/test_auth_refresh.py`
  - [ ] Test 200 OK con refresh token válido
  - [ ] Test que acceso y refresh tokens son nuevos
  - [ ] Test que refresh token anterior es revocado
  - [ ] Test 401 si refresh token expirado
  - [ ] Test 401 si refresh token no existe
  - [ ] Test 401 + revocar TODOS si detecta replay (reuso de mismo token 2x)
  - [ ] Run: `pytest tests/test_auth_refresh.py -v`

---

## CHANGE #11: Logout (`auth-logout`)

**Dependencia**: Change #10
**Estimación**: 1 hora
**Status**: [ ] Pendiente

### Subtasks

#### Backend

- [ ] Actualizar `backend/app/auth/service.py`
  - [ ] `logout(user_id, refresh_token)` service
  - [ ] Buscar RefreshToken por hash
  - [ ] Marcar revoked_at = NOW()
  - [ ] Commit

- [ ] Actualizar `backend/app/auth/router.py`
  - [ ] `POST /api/v1/auth/logout` endpoint
  - [ ] Requiere autenticación (@require_role())
  - [ ] Recibir refresh_token en body (o header, TBD)
  - [ ] Llamar `service.logout(current_user.id, refresh_token)`
  - [ ] Response 204 No Content
  - [ ] Error 400 si refresh token falta

#### Testing

- [ ] Crear `backend/tests/test_auth_logout.py`
  - [ ] Test 204 OK
  - [ ] Test que RefreshToken es marcado como revocado
  - [ ] Test que intentar refrescar con ese token = 401
  - [ ] Run: `pytest tests/test_auth_logout.py -v`

---

## CHANGE #12: RBAC y Protección de Rutas (`auth-rbac-roles`)

**Dependencia**: Change #5 + Change #9
**Estimación**: 3-4 horas
**Status**: [ ] Pendiente

### Subtasks

#### Backend

- [ ] Actualizar `backend/app/core/dependencies.py`
  - [ ] `require_role(*allowed_roles)` → decorator factory
  - [ ] Retorna función que valida roles del usuario
  - [ ] Si usuario no tiene rol → 403 Forbidden
  - [ ] Si no autenticado → 401 Unauthorized
  - [ ] Ejemplo:
    ```python
    @router.get("/admin/dashboard")
    @require_role("ADMIN")
    async def dashboard(current_user = Depends(get_current_user)):
        pass
    ```

- [ ] Crear `backend/app/admin/router.py`
  - [ ] `PUT /api/v1/admin/users/:user_id/roles` endpoint
  - [ ] Requiere @require_role("ADMIN")
  - [ ] Recibir `{ "roles": ["CLIENT", "STOCK"] }`
  - [ ] Lógica de negocio:
    - [ ] Validar que no hay solo 1 ADMIN intento quitarse ADMIN a sí mismo
    - [ ] Borrar roles actuales del usuario
    - [ ] Asignar nuevos roles
  - [ ] Response 200 + usuario con nuevos roles
  - [ ] Error 403 si intenta quitarse único ADMIN
  - [ ] Error 403 si caller no es ADMIN

- [ ] Crear `backend/app/admin/service.py`
  - [ ] `assign_roles_to_user(user_id, roles)` service
  - [ ] Validaciones de negocio (único ADMIN check)
  - [ ] Llamar repository

- [ ] Crear `backend/app/admin/repository.py`
  - [ ] Métodos para asignar/revocar roles

- [ ] Actualizar `backend/app/core/exceptions.py`
  - [ ] Error handler RFC 7807 para 403 Forbidden
  - [ ] Error handler para 401 Unauthorized

- [ ] Actualizar `backend/app/auth/router.py`
  - [ ] Aplicar @require_role() a rutas que lo necesitan
  - [ ] Ej: cambiar password solo usuario autenticado
  - [ ] Ej: ver historial de pedidos solo CLIENT

#### Database

- [ ] Migración (si es necesaria, probablemente no)

#### Testing

- [ ] Crear `backend/tests/test_auth_rbac.py`
  - [ ] Test GET /admin/dashboard sin token → 401
  - [ ] Test GET /admin/dashboard con token CLIENT → 403
  - [ ] Test GET /admin/dashboard con token ADMIN → 200
  - [ ] Test asignar roles a usuario
  - [ ] Test último ADMIN intenta quitarse ADMIN → error
  - [ ] Test que después de cambiar roles, nuevo JWT tiene nuevos roles
  - [ ] Run: `pytest tests/test_auth_rbac.py -v`

---

## CHANGE #13: Formularios de Auth Frontend (`frontend-auth-ui-forms`)

**Dependencia**: Change #9 + (Change #6 si existe, frontend patterns)
**Estimación**: 4-5 horas
**Status**: [ ] Pendiente

### Subtasks

#### Zustand Store (authStore)

- [ ] Crear `frontend/src/stores/authStore.ts`
  - [ ] State: `user`, `accessToken`, `refreshToken`, `isLoading`, `error`, `isAuthenticated`
  - [ ] Actions: `login(email, password)`, `register(email, password, full_name)`, `logout()`, `setTokens()`, `clearTokens()`
  - [ ] Persistencia: `localStorage.setItem("refreshToken", ...)` (NOT accessToken para XSS protection)
  - [ ] Recovery: Al montar app, verificar si hay token en localStorage y validar

#### Auth API Client

- [ ] Crear `frontend/src/shared/api/authApi.ts`
  - [ ] `postRegister(email, password, full_name)` → UserResponse
  - [ ] `postLogin(email, password)` → TokenResponse
  - [ ] `postRefresh(refreshToken)` → TokenResponse
  - [ ] `postLogout(refreshToken)` → void
  - [ ] Interceptor Axios que agrega `Authorization: Bearer <accessToken>` a todos los requests

#### Login Form

- [ ] Crear `frontend/src/features/auth/LoginForm.tsx`
  - [ ] Usa TanStack Form para validaciones
  - [ ] Campos: `email`, `password`
  - [ ] Validar: email válido, password no vacío
  - [ ] Submit → authStore.login()
  - [ ] Show error si falla (429, 401, 400)
  - [ ] Redirect a /dashboard si OK

- [ ] Crear `frontend/src/pages/LoginPage.tsx`
  - [ ] Layout simple con LoginForm
  - [ ] Link a "No tienes cuenta? Registrate"

#### Register Form

- [ ] Crear `frontend/src/features/auth/RegisterForm.tsx`
  - [ ] Usa TanStack Form
  - [ ] Campos: `email`, `password`, `passwordConfirm`, `full_name`
  - [ ] Validar: email válido, password >= 8, confirm match
  - [ ] Submit → authStore.register()
  - [ ] Show error si falta (409 duplicado, 422 validación)
  - [ ] Redirect a /login si OK

- [ ] Crear `frontend/src/pages/RegisterPage.tsx`
  - [ ] Layout simple con RegisterForm
  - [ ] Link a "Ya tienes cuenta? Inicia sesión"

#### Protected Routes

- [ ] Crear `frontend/src/features/auth/ProtectedRoute.tsx` (HOC o Wrapper)
  - [ ] Si `!authStore.isAuthenticated` → Redirect a /login
  - [ ] Si sí → render children

#### Testing

- [ ] Crear `frontend/tests/auth.test.tsx`
  - [ ] Test que LoginForm renderiza
  - [ ] Test que validaciones funcionan (email, password)
  - [ ] Test que submit llama authApi.postLogin
  - [ ] Test que RegisterForm renderiza
  - [ ] Test flow: register → login → token en store
  - [ ] Run: `npm test -- auth.test.tsx`

---

## CHANGE #14: Navegación Adaptada por Rol (`frontend-navigation-rbac`)

**Dependencia**: Change #13
**Estimación**: 2-3 horas
**Status**: [ ] Pendiente

### Subtasks

#### Navigation Component

- [ ] Crear `frontend/src/widgets/Navigation.tsx` (o actualizar si existe)
  - [ ] Mostrar/ocultar menú items según roles del authStore
  - [ ] Items por rol:
    - [ ] **CLIENT**: Catálogo, Mi Carrito, Mis Pedidos, Perfil, Logout
    - [ ] **STOCK**: Productos, Categorías, Gestionar Stock, Logout
    - [ ] **PEDIDOS**: Panel Pedidos, Reportes, Logout
    - [ ] **ADMIN**: Dashboard, Usuarios, Catálogo, Stock, Pedidos, Reportes, Logout
  - [ ] Usar condicionales: `authStore.user.roles.includes("ADMIN")`

- [ ] Crear `frontend/src/widgets/Sidebar.tsx`
  - [ ] Panel lateral colapsable
  - [ ] Items con íconos
  - [ ] Mostrar email del usuario actual
  - [ ] Botón de logout

#### Route Guards

- [ ] Actualizar `frontend/src/app/AppRoutes.tsx` (o router config)
  - [ ] Rutas públicas: /login, /register, / (home)
  - [ ] Rutas privadas (requiere autenticación): /dashboard, /profile, /cart
  - [ ] Rutas admin-only: /admin/users, /admin/dashboard
  - [ ] Usar ProtectedRoute wrapper
  - [ ] ¿Usar role-based route guards? (future feature, puedo ser manual por ahora)

#### Testing

- [ ] Crear tests visuales/E2E
  - [ ] CLIENT loguea → ve Catálogo, no ve Dashboard Admin
  - [ ] ADMIN loguea → ve todo
  - [ ] Sin token → ve solo login/register
  - [ ] Navegar a /admin sin ADMIN role → redirect a /
  - [ ] Run: `npm test -- navigation.test.tsx`

---

## CHANGE #15: Error Handling Global (`frontend-error-handling-global`)

**Dependencia**: Change #7 (si existe, frontend patterns) o Change #13
**Estimación**: 2 horas
**Status**: [ ] Pendiente

### Subtasks

#### Error Boundary

- [ ] Crear `frontend/src/shared/components/ErrorBoundary.tsx`
  - [ ] Class component que captura errores de React
  - [ ] Muestra fallback UI
  - [ ] Log error en console (desarrollo)

#### Axios Interceptor

- [ ] Actualizar `frontend/src/shared/api/authApi.ts` (o crear nuevo)
  - [ ] Response interceptor que mapea códigos HTTP a mensajes:
    - [ ] 401 → "Sesión expirada, inicia sesión nuevamente"
    - [ ] 403 → "No tienes permiso para esta acción"
    - [ ] 400 → mostrar detalles de validación
    - [ ] 409 → "Este recurso ya existe"
    - [ ] 429 → "Demasiados intentos, espera 15 minutos"
    - [ ] 500 → "Error del servidor, intenta más tarde"
  - [ ] Error interceptor para manejar:
    - [ ] Network errors
    - [ ] Timeout errors

#### Toast System (para notificaciones)

- [ ] Instalar librería de toast (ej: react-hot-toast, sonner, o simple toast div)
  - [ ] `npm install react-hot-toast` (o similar)

- [ ] Crear `frontend/src/shared/hooks/useToast.ts`
  - [ ] Helper para mostrar toasts en errores
  - [ ] Usarlo desde el interceptor Axios

- [ ] Crear `frontend/src/shared/components/ToastContainer.tsx`
  - [ ] Componente que renderiza los toasts

#### Testing

- [ ] Crear `frontend/tests/error-handling.test.tsx`
  - [ ] Test que error 400 muestra validaciones
  - [ ] Test que error 403 muestra "Sin permisos"
  - [ ] Test que error 429 muestra mensaje de rate limit
  - [ ] Run: `npm test -- error-handling.test.tsx`

---

## Meta-Tasks (transversales)

- [ ] **Database**:
  - [ ] Generar todas las migraciones
  - [ ] `alembic upgrade head` sin errores
  - [ ] Seed data carga correctamente

- [ ] **Testing Coverage**:
  - [ ] Backend: mínimo 80% coverage en auth/
  - [ ] Frontend: mínimo 70% coverage en auth/
  - [ ] `pytest --cov=app.auth` y ver reportes
  - [ ] `npm test -- --coverage` y ver reportes

- [ ] **Environment Variables**:
  - [ ] Backend `.env.example` tiene: `JWT_SECRET_KEY`, `JWT_ALGORITHM`, etc.
  - [ ] Frontend `.env.example` tiene: `VITE_API_BASE_URL`

- [ ] **Documentation**:
  - [ ] Actualizar `docs/API.md` con endpoints de auth
  - [ ] Crear `docs/AUTH.md` explicando flow y seguridad
  - [ ] Actualizar `CONTRIBUTING.md` si hay nuevas convenciones

- [ ] **Verificación Final**:
  - [ ] Backend: `pytest tests/ -v` (todo pasa)
  - [ ] Frontend: `npm test` (todo pasa)
  - [ ] Frontend build: `npm run build` (sin errores)
  - [ ] App en dev: `npm run dev` + manual E2E (register → login → dashboard)

---

## Notas Importantes

1. **No guardar access token en localStorage** → XSS risk. Guardar en memory (authStore) o sessionStorage como máximo. Refresh token sí en localStorage porque se necesita al refresh.

2. **Rate limiting en rate limiter** → La lógica en slowapi key debe ser `f"{request.client.host}:{email_from_body}"` para diferenciar intentos por usuario.

3. **Mensajes de error genéricos** → No diferenciar "usuario no existe" vs "contraseña incorrecta" (ambos 401 con "Credenciales inválidas").

4. **Replay attack detection** → Almacenar `family_id` en RefreshToken. Si detecta que fue revocado pero intenta reusar → revocar TODOS de ese family_id.

5. **TypeScript strict: true** → Asegurate que no hay `any`. Tipear todo.

6. **Testing de seguridad** → No confíes solo en tests automatizados. Hacer pruebas manuales de replay attacks, rate limiting, etc.

---

## Status Actual

| Change | Estado       | Completado |
| ------ | ------------ | ---------- |
| #8     | ⏳ Pendiente | 0%         |
| #9     | ⏳ Pendiente | 0%         |
| #10    | ⏳ Pendiente | 0%         |
| #11    | ⏳ Pendiente | 0%         |
| #12    | ⏳ Pendiente | 0%         |
| #13    | ⏳ Pendiente | 0%         |
| #14    | ⏳ Pendiente | 0%         |
| #15    | ⏳ Pendiente | 0%         |

**Total**: 0/71 tasks completadas

---
