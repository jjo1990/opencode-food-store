# Especificaciones — Phase 1: Autenticación y Autorización

## Data Models

### User (Tabla: `user`)

| Campo             | Tipo         | Constraint                          | Descripción                    |
| ----------------- | ------------ | ----------------------------------- | ------------------------------ |
| `id`              | UUID         | PK                                  | Identificador único            |
| `email`           | VARCHAR(255) | UNIQUE NOT NULL                     | Email del usuario              |
| `hashed_password` | VARCHAR(255) | NOT NULL                            | Contraseña hasheada con Argon2 |
| `full_name`       | VARCHAR(255) | -                                   | Nombre completo                |
| `telefono`        | VARCHAR(20)  | -                                   | Teléfono (opcional)            |
| `created_at`      | TIMESTAMP    | DEFAULT CURRENT_TIMESTAMP           | Fecha de creación              |
| `updated_at`      | TIMESTAMP    | DEFAULT CURRENT_TIMESTAMP ON UPDATE | Fecha de actualización         |
| `soft_deleted_at` | TIMESTAMP    | -                                   | Soft delete (NULL = activo)    |

**Índices**:

- `UNIQUE(email)` para búsquedas rápidas y garantizar unicidad
- `INDEX(soft_deleted_at)` para filtrar registros activos

**Relaciones**:

- `1:N` con `UserRole` (un usuario, múltiples roles)
- `1:N` con `RefreshToken` (un usuario, múltiples tokens)

---

### UserRole (Tabla: `user_role`)

| Campo         | Tipo        | Constraint                | Descripción                         |
| ------------- | ----------- | ------------------------- | ----------------------------------- |
| `id`          | UUID        | PK                        | Identificador único                 |
| `user_id`     | UUID        | FK → User.id              | Usuario                             |
| `role`        | VARCHAR(20) | NOT NULL                  | Rol (CLIENT, STOCK, PEDIDOS, ADMIN) |
| `assigned_at` | TIMESTAMP   | DEFAULT CURRENT_TIMESTAMP | Fecha de asignación                 |

**Índices**:

- `UNIQUE(user_id, role)` para evitar roles duplicados
- `INDEX(user_id)` para búsquedas por usuario
- `INDEX(role)` para búsquedas por rol

**Validaciones**:

- `role` IN ('CLIENT', 'STOCK', 'PEDIDOS', 'ADMIN')
- No borrar, solo insertar/actualizar (auditoría)

---

### RefreshToken (Tabla: `refresh_token`)

| Campo        | Tipo         | Constraint                | Descripción                                     |
| ------------ | ------------ | ------------------------- | ----------------------------------------------- |
| `id`         | UUID         | PK                        | Identificador único                             |
| `user_id`    | UUID         | FK → User.id              | Usuario propietario del token                   |
| `token_hash` | VARCHAR(255) | NOT NULL                  | Hash SHA256 del token (nunca almacenar limpio)  |
| `family_id`  | UUID         | -                         | ID de "familia" para detectar replay attacks    |
| `created_at` | TIMESTAMP    | DEFAULT CURRENT_TIMESTAMP | Fecha de creación                               |
| `expires_at` | TIMESTAMP    | NOT NULL                  | Expiración (7 días)                             |
| `revoked_at` | TIMESTAMP    | -                         | Soft revoke (NULL = activo, no NULL = revocado) |

**Índices**:

- `COMPOSITE INDEX(user_id, revoked_at)` para búsquedas rápidas y filtrar activos
- `INDEX(family_id)` para detectar replay attacks
- `INDEX(expires_at)` para limpiar tokens expirados (cleanup task)

**Lógica**:

- `revoked_at = NULL` → token activo
- `revoked_at = NOW()` → token revocado (puede ser por logout, refresh, o replay detection)

---

## Business Rules (RN)

### Autenticación (RN-AU)

| Código  | Regla                                                                                                                                          |
| ------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| RN-AU01 | Email debe ser único en el sistema (UNIQUE constraint)                                                                                         |
| RN-AU02 | Contraseña mínimo 8 caracteres, hasheada con Argon2 (nunca almacenar limpia)                                                                   |
| RN-AU03 | Email debe ser válido según RFC 5322                                                                                                           |
| RN-AU04 | Refresh tokens son revocables (soft delete con revoked_at)                                                                                     |
| RN-AU05 | **REPLAY ATTACK DETECTION**: Si se detecta reuso de refresh token revocado → revocar TODOS los tokens con mismo `family_id`                    |
| RN-AU06 | Access token expira en 30 minutos                                                                                                              |
| RN-AU07 | Refresh token expira en 7 días                                                                                                                 |
| RN-AU08 | Rate limiting: máximo 5 intentos fallidos de login por email por 15 minutos (HTTP 429)                                                         |
| RN-AU09 | Mensajes de error en login deben ser genéricos: no diferenciar "email no existe" vs "password incorrecto" (ambos 401 "Credenciales inválidas") |
| RN-AU10 | JWT firmado con HS256, secreto en variable de entorno `JWT_SECRET_KEY`                                                                         |

### Autorización (RN-RB)

| Código  | Regla                                                                                               |
| ------- | --------------------------------------------------------------------------------------------------- |
| RN-RB01 | 4 roles permitidos: CLIENT, STOCK, PEDIDOS, ADMIN                                                   |
| RN-RB02 | Un usuario puede tener múltiples roles simultáneamente                                              |
| RN-RB03 | Roles asignables solo por ADMIN (endpoint `PUT /api/v1/admin/users/:id/roles`)                      |
| RN-RB04 | Rutas protegidas requieren token válido (401 si falta)                                              |
| RN-RB05 | Rutas role-restricted requieren rol específico (403 si no tiene)                                    |
| RN-RB06 | No puede haber 0 ADMIN en el sistema (prevención: si es último ADMIN, no permitir quitarle ese rol) |
| RN-RB07 | Al crear usuario, asignar rol CLIENT automáticamente                                                |
| RN-RB08 | Cambiar rol de usuario requiere fetch nuevo JWT (roles en JWT, no se actualizan al vuelo)           |
| RN-RB09 | Roles incluidos en JWT para autorización rápida (sin queries a BD en cada request)                  |
| RN-RB10 | Endpoint `GET /api/v1/users/:id` retorna roles del usuario en response                              |

### Datos Sensibles (RN-DA)

| Código  | Regla                                                                         |
| ------- | ----------------------------------------------------------------------------- |
| RN-DA01 | Contraseña nunca se devuelve en API (ni hasheada)                             |
| RN-DA02 | Refresh token se devuelve solo UNA VEZ en login/refresh (no en GET)           |
| RN-DA03 | Access token guardado en memory/sessionStorage (NOT localStorage) en frontend |
| RN-DA04 | Soft delete: usuarios archivados pueden quedar en la BD (soft_deleted_at)     |

---

## API Contracts

### Endpoints de Auth

#### 1. POST /api/v1/auth/register

**Request**:

```json
{
  "email": "usuario@example.com",
  "password": "SecurePass123",
  "full_name": "Juan Pérez"
}
```

**Response (201 Created)**:

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "usuario@example.com",
  "full_name": "Juan Pérez",
  "roles": ["CLIENT"]
}
```

**Errors**:

- `400 Bad Request`: Datos faltantes
- `409 Conflict`: Email ya registrado
- `422 Unprocessable Entity`: Validación fallida (email inválido, password < 8)

---

#### 2. POST /api/v1/auth/login

**Request**:

```json
{
  "email": "usuario@example.com",
  "password": "SecurePass123"
}
```

**Response (200 OK)**:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "rt_1234567890abcdef1234567890abcdef1234567890abcdef",
  "expires_in": 1800,
  "token_type": "Bearer"
}
```

**Errors**:

- `401 Unauthorized`: Credenciales inválidas (email no existe o password incorrecto, mensaje genérico)
- `429 Too Many Requests`: Rate limited (5 intentos fallidos en 15 min)

---

#### 3. POST /api/v1/auth/refresh

**Request**:

```json
{
  "refresh_token": "rt_1234567890abcdef1234567890abcdef1234567890abcdef"
}
```

**Response (200 OK)**:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "rt_9876543210fedcba9876543210fedcba9876543210fedcba",
  "expires_in": 1800,
  "token_type": "Bearer"
}
```

**Errors**:

- `401 Unauthorized`: Token inválido, expirado, revocado, o REPLAY ATTACK detectado

---

#### 4. POST /api/v1/auth/logout

**Headers**:

```
Authorization: Bearer <access_token>
```

**Request**:

```json
{
  "refresh_token": "rt_..."
}
```

**Response (204 No Content)**:
(sin body)

**Errors**:

- `400 Bad Request`: Refresh token faltante
- `401 Unauthorized`: Access token inválido o expirado

---

#### 5. PUT /api/v1/admin/users/:user_id/roles

**Headers**:

```
Authorization: Bearer <access_token>  (requiere rol ADMIN)
```

**Request**:

```json
{
  "roles": ["CLIENT", "STOCK"]
}
```

**Response (200 OK)**:

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "usuario@example.com",
  "full_name": "Juan Pérez",
  "roles": ["CLIENT", "STOCK"]
}
```

**Errors**:

- `400 Bad Request`: Roles inválidos o estructura errónea
- `401 Unauthorized`: Sin token o token expirado
- `403 Forbidden`: No es ADMIN, o intenta quitarle único ADMIN su rol
- `404 Not Found`: Usuario no existe

---

## JWT Payload (Claims)

```json
{
  "sub": "550e8400-e29b-41d4-a716-446655440000",
  "email": "usuario@example.com",
  "roles": ["CLIENT", "STOCK"],
  "exp": 1672531200,
  "iat": 1672527600,
  "type": "access"
}
```

**Fields**:

- `sub`: User ID
- `email`: Email del usuario
- `roles`: Array de roles del usuario
- `exp`: Expiration time (Unix timestamp, +30 min)
- `iat`: Issued at time (Unix timestamp)
- `type`: "access" o "refresh" (para diferenciar tipos)

---

## Security Considerations

1. **Password Hashing**: Usar `passlib` con Argon2
   - `CryptContext(schemes=["argon2"], deprecated="auto")`
   - Nunca almacenar passwords plaintext ni con MD5/SHA1

2. **Token Storage**:
   - **Access Token**: Memory (Zustand store) + Memory del servidor
   - **Refresh Token**: localStorage (necesario para persist) + BD (para revocation)

3. **CORS**: Permitir solo `https://` en producción (no `http://`)

4. **Rate Limiting**: Implementar por IP + email, no por usuario autenticado

5. **Replay Attack Detection**:
   - Almacenar `family_id` en cada RefreshToken
   - Si token revocado pero intenta reusar → revocar TODOS con mismo family_id
   - User ve error: "Posible acceso no autorizado. Vuelve a loguear."

6. **Audit Logging**: Log todos los intentos de login (éxito/fallo), cambios de rol

---

## Validaciones en Frontend (TanStack Form)

### LoginForm

```
email:
  - required
  - valid email format
password:
  - required
  - not empty
```

### RegisterForm

```
email:
  - required
  - valid email format
password:
  - required
  - >= 8 characters
  - ✓ strong enough (opcional: uppercase, number, special char)
passwordConfirm:
  - required
  - must match password
full_name:
  - required
  - not empty
```

---

## Testing Scenarios

### Backend

| Scenario                        | Expected          | Test                                     |
| ------------------------------- | ----------------- | ---------------------------------------- |
| Registrar con email nuevo       | 201 OK            | `test_register_success`                  |
| Registrar email duplicado       | 409 Conflict      | `test_register_duplicate_email`          |
| Registrar password < 8          | 422 Unprocessable | `test_register_weak_password`            |
| Registrar email inválido        | 422 Unprocessable | `test_register_invalid_email`            |
| Login con credenciales válidas  | 200 + tokens      | `test_login_success`                     |
| Login email no existe           | 401 Unauthorized  | `test_login_nonexistent_email`           |
| Login password incorrecto       | 401 Unauthorized  | `test_login_wrong_password`              |
| Login 5+ intentos fallidos      | 429 Too Many      | `test_login_rate_limit`                  |
| Refresh token válido            | 200 + new tokens  | `test_refresh_success`                   |
| Refresh token expirado          | 401 Unauthorized  | `test_refresh_expired`                   |
| Refresh token reusado (replay)  | 401 + revoke all  | `test_refresh_replay_attack`             |
| Logout                          | 204 No Content    | `test_logout_success`                    |
| Logout + try refresh            | 401 Unauthorized  | `test_logout_revokes_token`              |
| Acceso ruta sin token           | 401 Unauthorized  | `test_protected_route_no_token`          |
| Acceso ruta ADMIN siendo CLIENT | 403 Forbidden     | `test_protected_route_insufficient_role` |
| Acceso ruta ADMIN siendo ADMIN  | 200 OK            | `test_protected_route_with_role`         |

### Frontend

| Scenario                   | Expected                 | Test                                |
| -------------------------- | ------------------------ | ----------------------------------- |
| Render LoginForm           | Muestra campos           | `test_login_form_render`            |
| Validar email en LoginForm | Error si inválido        | `test_login_form_email_validation`  |
| Submit LoginForm           | Llama API + guarda token | `test_login_form_submit`            |
| Render RegisterForm        | Muestra campos           | `test_register_form_render`         |
| Validar password match     | Error si no coincide     | `test_register_form_password_match` |
| Submit RegisterForm        | Llama API + redirect     | `test_register_form_submit`         |
| ProtectedRoute sin token   | Redirect a /login        | `test_protected_route_redirect`     |
| ProtectedRoute con token   | Renderiza children       | `test_protected_route_render`       |
| Navigation CLIENT role     | Muestra menú CLIENT      | `test_navigation_client_menu`       |
| Navigation ADMIN role      | Muestra menú ADMIN       | `test_navigation_admin_menu`        |

---
