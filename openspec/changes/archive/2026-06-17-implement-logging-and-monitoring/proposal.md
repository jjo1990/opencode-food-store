## Why

Food Store tiene **cero visibilidad del sistema**. No hay un solo `logging.getLogger()` en todo el backend — si algo falla en producción, no hay logs para diagnosticar. Los errores HTTP devuelven `{"detail": "..."}` sin estructura (sin RFC 7807), no hay trazabilidad de requests (sin request ID), y existen 2 `except Exception: pass` que tragan errores silenciosamente. Los handlers de excepción de FastAPI son los defaults — sin stack traces, sin request context, sin diferenciación por nivel.

En el frontend, solo hay 1 `console.error` en todo el código (ErrorBoundary). Las acciones clave del usuario (login, orden creada, pago confirmado) no dejan rastro. No hay tracking de web vitals (LCP, FID, CLS) para medir performance real. Si un usuario reporta "no pude pagar", no hay forma de reconstruir qué pasó.

Este change implementa la capa de observabilidad mínima para operar el sistema con confianza.

## What Changes

- **Backend — Logging estructurado JSON**: Nuevo módulo `core/logging.py` con `JSONFormatter` y `setup_logging()`. Todos los logs en formato JSON con timestamp, level, logger, message, module, function. Nivel controlado por `LOG_LEVEL` env var. Salida a stdout para compatibilidad con Docker/cloud.

- **Backend — Middleware de request/response**: Nuevo `core/middleware.py` con `LoggingMiddleware` (ASGI/http). Cada request loguea method, path, query params, status code, duration en ms. Genera request ID (UUID short) por request, lo incluye en logs y en response header `X-Request-ID`. Redacta headers sensibles (Authorization, Cookie). Omite health checks.

- **Backend — Exception handlers RFC 7807**: Handlers registrados en `main.py` para `HTTPException` y `Exception` (unhandled). Ambos devuelven Problem Details (RFC 7807): type, title, status, detail, instance. `HTTPException` → WARNING con status y detail. Unhandled → ERROR con traceback completo. En producción (DEBUG=false), el detail de 500 oculta detalles internos.

- **Backend — Eliminación de silent exceptions**: Los 2 `except Exception: pass` existentes (`dependencies.py:82`, `pedidos/service.py:181`) ahora loguean `logger.warning(..., exc_info=True)`. Los `print()` en `seed.py` migran a `logging`.

- **Frontend — Dev logger utility**: Nuevo `shared/utils/logger.ts` con guard `import.meta.env.DEV` — solo emite en desarrollo. Formato estructurado: timestamp, level, action, data. Métodos: debug, info, warn, error con mapeo a console methods.

- **Frontend — Logging estratégico**: `devLogger` calls en authStore (login, logout, refresh), cartStore (add, remove, clear), CheckoutPage (payment flow), AdminOrdersPage (state changes). ErrorBoundary mejorado con datos estructurados.

- **Frontend — Axios logging**: Response interceptor en `shared/api/client.ts` loguea method, URL, status code en dev mode.

- **Frontend — TanStack Query DevTools**: Verificar que solo renderiza en desarrollo. Mantener `initialIsOpen={false}`.

## Capabilities

### New Capabilities

- `logging-backend`: Logging estructurado JSON en backend con Python logging, middleware de request/response con request ID, exception handlers RFC 7807, eliminación de silent exceptions, y respeto de LOG_LEVEL env var.
- `logging-frontend`: Dev logger condicional con formato estructurado, logging de acciones clave (auth, cart, payment, orders), logging de requests HTTP en axios interceptor, y TanStack Query DevTools en modo desarrollo.

### Modified Capabilities

- `error-handling` (Change 8): Los exception handlers existentes ahora producen logs estructurados con request context y tracebacks en desarrollo. El formato de error HTTP migra de `{"detail": "..."}` a RFC 7807 Problem Details.

## Impact

- **Backend**: `core/logging.py` (nuevo), `core/middleware.py` (nuevo), `main.py` (modificado — setup_logging, middleware, exception handlers), `core/dependencies.py` (modificado — fix bare except), `pedidos/service.py` (modificado — fix bare except), `db/seed.py` (modificado — print → logging)
- **Frontend**: `shared/utils/logger.ts` (nuevo), `shared/api/client.ts` (modificado — axios logging), `stores/authStore.ts` (modificado — devLogger calls), `stores/cartStore.ts` (modificado — devLogger calls), pages de checkout y admin orders (modificado — devLogger calls), `shared/components/ErrorBoundary.tsx` (modificado — structured error logging)
- **Base de datos**: Sin cambios
- **Dependencias**: Ninguna nueva. Python `logging`, `json`, `uuid`, `time` son stdlib. Frontend solo usa `import.meta.env.DEV` (built-in Vite).
- **Seguridad**: Los logs NUNCA contienen datos de tarjeta, contraseñas, ni tokens completos. Headers sensibles (Authorization, Cookie) se redactan como `[REDACTED]`. En producción, los 500 no exponen stack traces al cliente.
