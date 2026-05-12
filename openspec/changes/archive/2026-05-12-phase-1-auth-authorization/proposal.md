# PHASE 1: Autenticación y Autorización

## Resumen Ejecutivo

Implementar un sistema completo de autenticación con JWT, refresh tokens y autorización basada en roles (RBAC) con 4 roles: CLIENT, STOCK, PEDIDOS, ADMIN. Incluye protección contra rate limiting, detección de replay attacks y navegación adaptada por rol en frontend.

## Problema

Sin autenticación:

- No hay forma de identificar quién es el usuario
- No hay protección de datos sensibles (pedidos, direcciones, historial)
- No hay diferenciación de permisos (un cliente no debe ver stock real, admin no debería ver precio de costo)
- Vulnerabilidad a ataques de fuerza bruta (infinite login attempts)

## Valor

- ✅ Usuarios pueden registrarse y loguear de forma segura
- ✅ Sistema de roles permite control granular de acceso
- ✅ JWT + refresh token permite escalabilidad (sin sesiones en servidor)
- ✅ Detección de replay attacks protege contra token hijacking
- ✅ Frontend adaptado por rol mejora UX y previene acceso no autorizado

## Alcance

### Backend (6 changes)

1. **Change #8**: Registro de usuario (`auth-user-registration`)
2. **Change #9**: Login con rate limiting (`auth-user-login-rate-limiting`)
3. **Change #10**: Refresh token con rotación (`auth-token-refresh-rotation`)
4. **Change #11**: Logout (`auth-logout`)
5. **Change #12**: RBAC y protección de rutas (`auth-rbac-roles`)
6. (Infraestructura base de patrones ya hecha en Phase 0)

### Frontend (3 changes)

7. **Change #13**: Formularios de auth (`frontend-auth-ui-forms`)
8. **Change #14**: Navegación adaptada por rol (`frontend-navigation-rbac`)
9. **Change #15**: Error handling global (`frontend-error-handling-global`)

## Dependencias

- ✅ Phase 0 completada (monorepo, FastAPI, React, BD)
- `Change #5` (Backend patterns - infraestructura base) es prerequisito
- `Change #6` (Frontend patterns) es prerequisito para cambios frontend

## Historias de Usuario Cubiertas

| Historia                           | Change |
| ---------------------------------- | ------ |
| US-001: Registrarse                | #8     |
| US-002: Loguear                    | #9     |
| US-003: Refresh token              | #10    |
| US-004: Logout                     | #11    |
| US-005: Asignar roles              | #12    |
| US-006: RBAC                       | #12    |
| US-067: Error handling             | #15    |
| US-073: Rate limiting              | #9     |
| US-075, US-076: Navegación por rol | #14    |

## Validaciones de Negocio (RN)

- **RN-AU01**: Email único en el sistema
- **RN-AU02**: Contraseña >= 8 caracteres, hasheada con Argon2
- **RN-AU04**: Tokens revocables
- **RN-AU05**: Detección de replay attacks (revocar todos si detecta reuso)
- **RN-AU06**: Refresh token expira en 7 días
- **RN-AU07**: Email válido (RFC 5322)
- **RN-AU08**: Tasa máxima de 5 intentos fallidos / 15 min
- **RN-RB01-RB10**: RBAC con 4 roles, protección de rutas

## Criterios de Aceptación

✅ Usuario se registra y recibe JWT + refresh token
✅ Login protegido con rate limiting (5 intentos / 15 min)
✅ Refresh token rotativo con detección de replay attacks
✅ Logout revoca refresh token
✅ ADMIN puede asignar/revocar roles
✅ Rutas protegidas devuelven 401/403 según token/roles
✅ Frontend tiene formularios de login/registro validados
✅ UI adaptada según rol del usuario
✅ Errores mapeados a mensajes legibles en frontend

## Timeline Estimado

- **Change #8**: 2-3 horas
- **Change #9**: 3-4 horas
- **Change #10**: 2-3 horas
- **Change #11**: 1 hora
- **Change #12**: 3-4 horas
- **Change #13**: 4-5 horas
- **Change #14**: 2-3 horas
- **Change #15**: 2 horas

**Total**: ~20-25 horas (3 días de desarrollo)

## Riesgos

- Refresh token rotation puede ser complicado si no hay persistencia en BD
- Detección de replay attacks requiere logging transaccional
- RBAC puede requesar revisión de todas las rutas para aplicar decoradores

## Notas

- Usar JWT con algoritmo HS256 (secreto en `.env`)
- Refresh tokens almacenar en tabla `RefreshToken` con `revoked_at`
- Rate limiting con `slowapi` (ya está en Change #2)
- Frontend guardar access token en memory, no en localStorage (seguridad)
