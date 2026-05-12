# PHASE 1: Autenticación y Autorización — Diseño Técnico

## Arquitectura de Autenticación

```
┌─────────────────────────────────────────────────────────────┐
│  Frontend (React + Zustand)                                 │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ LoginForm → submit → authStore.login()              │   │
│  │            ↓                                         │   │
│  │ POST /api/v1/auth/login (email, password)           │   │
│  │            ↓                                         │   │
│  │ response: { access_token, refresh_token }           │   │
│  │            ↓                                         │   │
│  │ localStorage.setItem("refresh_token", ...)          │   │
│  │ authStore.setTokens({ access, refresh })           │   │
│  │ authStore.setUser(decoded_jwt)                      │   │
│  │            ↓                                         │   │
│  │ Todos los requests incluyen Authorization header:   │   │
│  │ Authorization: Bearer <access_token>                │   │
│  └──────────────────────────────────────────────────────┘   │
│                         │                                    │
└─────────────────────────┼────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│  FastAPI Backend                                            │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Router /api/v1/auth/                                │   │
│  │   - POST /register   → UserRepository.create()      │   │
│  │   - POST /login      → validar + emit JWT           │   │
│  │   - POST /refresh    → validar RT + rotate          │   │
│  │   - POST /logout     → revocar RT                   │   │
│  │                                                      │   │
│  │ Middleware                                          │   │
│  │   - Rate limiter: slowapi en /login (5/15min)      │   │
│  │   - get_current_user: decode JWT, valida exp       │   │
│  │   - require_role(): verifica roles del user        │   │
│  │                                                      │   │
│  │ Database                                            │   │
│  │   - User (id, email, hashed_pwd, roles)            │   │
│  │   - RefreshToken (id, user_id, token, revoked_at)  │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Modelo de Datos

### Tabla: User

```sql
CREATE TABLE "user" (
  id UUID PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  hashed_password VARCHAR(255) NOT NULL,  -- Argon2
  full_name VARCHAR(255),
  telefono VARCHAR(20),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  soft_deleted_at TIMESTAMP NULL
)
```

### Tabla: UserRole (M2M)

```sql
CREATE TABLE user_role (
  id UUID PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES "user"(id),
  role VARCHAR(20) NOT NULL,  -- CLIENT, STOCK, PEDIDOS, ADMIN
  assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(user_id, role)
)
```

### Tabla: RefreshToken

```sql
CREATE TABLE refresh_token (
  id UUID PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES "user"(id),
  token_hash VARCHAR(255) NOT NULL,  -- Almacenar hash, no token limpio
  family_id UUID,  -- Para detección de replay (todos del mismo login)
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  expires_at TIMESTAMP NOT NULL,  -- 7 días
  revoked_at TIMESTAMP NULL,  -- NULL = activo, no NULL = revocado
  INDEX (user_id, revoked_at)
)
```

## Flujos de Autenticación

### 1. Registro (Change #8)

```python
POST /api/v1/auth/register
{
  "email": "user@example.com",
  "password": "SecurePass123",
  "full_name": "Juan Pérez"
}

Response (200):
{
  "id": "uuid",
  "email": "user@example.com",
  "roles": ["CLIENT"]
}

Errors:
- 409: Email ya existe
- 422: Contraseña < 8 caracteres
- 422: Email inválido
```

**Validaciones**:

- Email único, válido RFC 5322
- Contraseña >= 8 caracteres, sin patrones débiles
- User creado automáticamente con rol CLIENT

### 2. Login (Change #9 + Rate Limiting)

```python
POST /api/v1/auth/login
{
  "email": "user@example.com",
  "password": "SecurePass123"
}

Response (200):
{
  "access_token": "eyJhbGc...",
  "refresh_token": "rt_...",
  "expires_in": 1800,  # 30 minutos
  "token_type": "Bearer"
}

Errors:
- 401: Email o contraseña incorrectos (mensajes genéricos)
- 429: Rate limited (5 intentos fallidos en 15 min)
```

**Tokens**:

- **access_token**: JWT con claims { sub, roles, exp: +30min }
- **refresh_token**: Almacenado en BD, exp: +7 días, family_id para replay detection
- Rate limiting: slowapi middleware, key=IP+email

### 3. Refresh Token (Change #10 - Token Rotation)

```python
POST /api/v1/auth/refresh
{
  "refresh_token": "rt_..."
}

Response (200):
{
  "access_token": "eyJhbGc...",  # Nuevo
  "refresh_token": "rt_...",  # Nuevo y anterior revocado
  "expires_in": 1800
}

Errors:
- 401: Token inválido, expirado o revocado
- 401: Si detecta replay (reuso de token):
  → Revocar TODOS los refresh tokens con mismo family_id
  → Lanzar error "Posible acceso no autorizado, revoque sesiones"
```

**Detección de Replay**:

- Cada login nuevo genera nuevo family_id
- Si recibimos refresh_token X cuando sabemos que fue revocado → REPLAY
- Acción: Revocar TODOS los tokens de ese usuario (RN-AU05)

### 4. Logout (Change #11)

```python
POST /api/v1/auth/logout
Authorization: Bearer <access_token>

Response (204 No Content)
```

**Acciones**:

- Marcar RefreshToken.revoked_at = NOW()
- Frontend borra tokens locales

### 5. RBAC (Change #12)

```python
# Asignar rol (solo ADMIN)
PUT /api/v1/admin/users/:user_id/roles
Authorization: Bearer <access_token>  # ADMIN
{
  "roles": ["CLIENT", "STOCK"]
}

# GET usuario con sus roles
GET /api/v1/users/:id
→ { id, email, roles: ["CLIENT", "STOCK"] }

# Protección de ruta
@router.get("/api/v1/admin/dashboard")
@require_role("ADMIN")
def admin_dashboard(current_user: User = Depends(get_current_user)):
    pass

# Si usuario no tiene rol → 403 Forbidden
# Si no tiene token → 401 Unauthorized
```

**Roles**:

- **CLIENT**: Compra, ve su historial, profile
- **STOCK**: Actualiza stock, ve reporte de inventario
- **PEDIDOS**: Procesa pedidos, ve status
- **ADMIN**: Todo

## Seguridad

### JWT (PyJWT con HS256)

```python
import jwt
from datetime import datetime, timedelta

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"

# Crear token
payload = {
    "sub": str(user.id),
    "email": user.email,
    "roles": [role.role for role in user.roles],
    "exp": datetime.utcnow() + timedelta(minutes=30)
}
token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

# Validar token
try:
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    user_id = payload["sub"]
except jwt.ExpiredSignatureError:
    raise HTTPException(status_code=401, detail="Token expirado")
except jwt.InvalidTokenError:
    raise HTTPException(status_code=401, detail="Token inválido")
```

### Hashing de Contraseñas (Argon2)

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# Hash
hashed = pwd_context.hash(password)

# Verify
is_valid = pwd_context.verify(password, hashed)
```

### Refresh Token Hash

```python
# NO almacenar refresh token limpio en BD
# Almacenar hash + salt
token = secrets.token_urlsafe(32)
token_hash = hashlib.sha256(token.encode()).hexdigest()
# BD: token_hash
# Respuesta: token (solo una vez)
```

## Estructura de Archivos

### Backend

```
backend/
├── app/
│   ├── auth/
│   │   ├── router.py          # POST /register, /login, /refresh, /logout
│   │   ├── service.py         # Lógica de auth (validar, crear tokens)
│   │   └── repository.py      # UserRepository, RefreshTokenRepository
│   ├── core/
│   │   ├── config.py          # JWT_SECRET_KEY, JWT_EXPIRY, etc.
│   │   ├── dependencies.py    # get_current_user, require_role
│   │   ├── exceptions.py      # RFC 7807 error handling
│   │   └── security.py        # hash_password, verify_password, create_jwt
│   ├── models/
│   │   └── schemas.py         # LoginRequest, RegisterRequest, TokenResponse
│   └── main.py                # Registrar router de auth
└── tests/
    ├── test_auth_register.py
    ├── test_auth_login.py
    ├── test_auth_refresh.py
    └── test_auth_rbac.py
```

### Frontend

```
frontend/
├── src/
│   ├── pages/
│   │   ├── LoginPage.tsx
│   │   └── RegisterPage.tsx
│   ├── features/auth/
│   │   ├── LoginForm.tsx
│   │   ├── RegisterForm.tsx
│   │   └── ProtectedRoute.tsx   # HOC para rutas privadas
│   ├── stores/
│   │   └── authStore.ts         # Zustand store con user, tokens, roles
│   ├── shared/
│   │   └── api/
│   │       └── authApi.ts       # Llamadas HTTP a /auth/*
│   └── widgets/
│       ├── Navigation.tsx        # Sidebar/NavBar adaptado por rol
│       └── ErrorBoundary.tsx
└── tests/
    └── auth.test.tsx
```

## Testing

### Backend

- ✅ Registro duplicado → 409
- ✅ Contraseña débil → 422
- ✅ Login válido → 200 + tokens
- ✅ Rate limiting → 5 intentos fallidos = 429 en el 6to
- ✅ Refresh válido → nuevo access + refresh
- ✅ Refresh reusado (replay) → 401 + revocar todos
- ✅ Logout → refrescar con mismo token = 401
- ✅ RBAC: CLIENT en ruta ADMIN → 403
- ✅ RBAC: Sin token → 401

### Frontend

- ✅ Formularios validan antes de submit
- ✅ Login/registro E2E funciona
- ✅ Token guardado en authStore
- ✅ ProtectedRoute redirige a login si no autenticado
- ✅ Navegación cambia según roles

## Decisiones de Diseño

1. **JWT sin BD**: Rápido, pero refresh tokens requieren BD para revocación
2. **Refresh token rotation**: Seguro contra token hijacking
3. **Rate limiting en IP+email**: Protege contra brute force
4. **Access token en memory, refresh en localStorage**: XSS protection
5. **Roles en JWT**: Rápido para autorización, pero requiere refresh al cambiar rol
6. **Soft delete de users**: Permite auditoría
7. **family_id en refresh tokens**: Detecta replay attacks automáticamente

## Próximos Pasos Después de Phase 1

- Change #16: Catálogo de productos (depende de RBAC)
- 2FA/MFA (Change posterior)
- OAuth2 (Google, GitHub, etc.)
