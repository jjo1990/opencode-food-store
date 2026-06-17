## Context

Food Store es una plataforma e-commerce full-stack (FastAPI + React) con arquitectura Feature-First en backend y FSD en frontend. Actualmente no existe ningún sistema de logging: cero `logging.getLogger()` en backend, solo 1 `console.error` en frontend. Los errores HTTP se devuelven como `{"detail": "..."}` sin estructura RFC 7807. Hay 2 `except Exception: pass` silenciosos. No hay request IDs, no hay trazas de requests, no hay tracking de performance.

**Restricciones existentes:**

- Backend: Router → Service → UoW → Repository → Model (imports unidireccionales)
- Frontend: Pages → Features → Entities → Shared (FSD estricto)
- TypeScript `strict: true`, Python con type hints
- `LOG_LEVEL` env var definida en `docker-compose.yml` pero nunca leída en código
- `echo=False` en SQLAlchemy engine (sin log de queries SQL)
- TanStack Query DevTools ya instalado con `initialIsOpen={false}`
- `react-hot-toast` para feedback de errores HTTP (axios interceptor)
- Rate limiting solo en endpoint login (slowapi decorator, no middleware app-level)

**Lo que NO existe:**

- `logging` configuration (basicConfig, getLogger, handlers, formatters)
- Request/response logging middleware
- Exception handlers personalizados registrados en la app
- RFC 7807 Problem Details responses
- Request ID generation o header `X-Request-ID`
- Redaction de datos sensibles en logs
- Dev logger utility en frontend
- Console logging de acciones de usuario (auth, cart, payment)
- Axios request/response logging
- Web vitals tracking (LCP, FID, CLS)
- Sentry o servicio de error tracking

## Goals / Non-Goals

**Goals:**

- Implementar logging estructurado JSON en backend con Python stdlib `logging`
- Crear middleware de request/response con request ID, duration, y redaction
- Registrar exception handlers RFC 7807 para HTTPException y unhandled Exception
- Eliminar silent exceptions — todo `except Exception: pass` debe loguear al menos WARNING
- Crear dev logger utility en frontend con guard `import.meta.env.DEV`
- Agregar logging estratégico en acciones clave: auth, cart, payment, orders
- Agregar logging de requests HTTP en axios interceptor
- Verificar TanStack Query DevTools condicionado a development mode

**Non-Goals:**

- No instalar dependencias externas de logging (python-json-logger, structlog, pino, winston)
- No integrar Sentry o servicio de error tracking externo en este change (es opcional/stretch)
- No implementar web vitals tracking (LCP, FID, CLS) en este change (es opcional/stretch)
- No loguear queries SQL (requiere cambio en `echo` del engine — fuera de scope)
- No implementar log rotation o file logging (solo stdout para Docker/cloud)
- No cambiar el comportamiento de rate limiting existente
- No loguear request/response bodies completos (riesgo de datos sensibles y verbosidad)
- No crear dashboards o visualización de logs (Kibana, Grafana)

## Decisions

### 1. JSON Formatter — stdlib puro

**Decision:** Implementar `JSONFormatter` extendiendo `logging.Formatter` con stdlib `json.dumps()`. Sin dependencias externas.

```python
import json
import logging
from datetime import datetime, timezone

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
        }
        if record.exc_info and record.exc_info[1]:
            log_entry["exception"] = str(record.exc_info[1])
            log_entry["traceback"] = self.formatException(record.exc_info)
        # Merge extra fields from record.__dict__ (set via extra={...})
        for key, value in record.__dict__.items():
            if key not in {"args", "asctime", "created", "exc_info", "exc_text",
                           "filename", "funcName", "levelname", "levelno",
                           "lineno", "module", "msecs", "message", "msg",
                           "name", "pathname", "process", "processName",
                           "relativeCreated", "stack_info", "thread", "threadName"}:
                log_entry[key] = value
        return json.dumps(log_entry, ensure_ascii=False, default=str)
```

**Rationale:** Python `logging` es stdlib y suficiente para structured logging con un formatter custom. Evita dependencias como `python-json-logger` (no instalada, requiere pip install). `json.dumps` con `default=str` maneja tipos no serializables. `ensure_ascii=False` para caracteres UTF-8 (español). Los campos `extra` del logger se mergean automáticamente para incluir `request_id`, `duration_ms`, etc.

**Alternativa considerada:** `structlog` — excelente pero requiere instalación, configuración adicional, y curva de aprendizaje. `python-json-logger` — simple pero es una dependencia externa para una necesidad que se resuelve con 30 líneas de código.

### 2. Logging Setup — Reemplazar handlers, no agregar

**Decision:** `setup_logging()` reemplaza TODOS los handlers del root logger con un único `StreamHandler(stdout)` + `JSONFormatter`. No se agrega file handler por ahora.

```python
import os

def setup_logging():
    level = os.getenv("LOG_LEVEL", "INFO").upper()
    handler = logging.StreamHandler()
    handler.setFormatter(JSONFormatter())

    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level, logging.INFO))
    root_logger.handlers = [handler]  # Replace, don't append
```

**Rationale:** Reemplazar handlers (no `addHandler`) evita duplicación de logs si `setup_logging()` se llama múltiples veces o si uvicorn ya configuró handlers. `LOG_LEVEL` env var ya está definida en `docker-compose.yml` como `INFO`. `getattr(logging, level, logging.INFO)` da fallback seguro si el valor es inválido. Salida a stdout es el estándar para contenedores Docker (12-factor app).

### 3. Request Logging Middleware — FastAPI `@app.middleware("http")`

**Decision:** Usar el decorador `@app.middleware("http")` de FastAPI en lugar de ASGI middleware puro.

```python
import time
import uuid
import logging

logger = logging.getLogger(__name__)

async def logging_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())[:8]
    request.state.request_id = request_id

    # Skip health checks
    if request.url.path in ("/", "/health"):
        return await call_next(request)

    start = time.time()
    response = await call_next(request)
    duration = (time.time() - start) * 1000

    status_code = response.status_code
    log_level = logging.ERROR if status_code >= 500 else \
                logging.WARNING if status_code >= 400 else logging.INFO

    logger.log(
        log_level,
        "Request completed",
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "query": str(request.query_params) if request.query_params else None,
            "status": status_code,
            "duration_ms": round(duration, 2),
        },
    )
    response.headers["X-Request-ID"] = request_id
    return response
```

**Rationale:** `@app.middleware("http")` es la forma idiomática de FastAPI para middleware HTTP. Soporta `request.state` para pasar datos entre middleware y handlers. `request_id` de 8 caracteres es suficiente para unicidad en el contexto de una sesión de debugging y es legible. Skip de health checks evita ruido en logs (Docker health checks cada 30s). Log level depende del status code: ERROR para 5xx, WARNING para 4xx, INFO para 2xx/3xx.

### 4. Sensitive Data Redaction

**Decision:** Redactar headers `Authorization` y `Cookie` en logs. No loguear request/response bodies.

```python
# En el middleware, antes de loguear:
safe_headers = dict(request.headers)
for header in ("authorization", "cookie"):
    if header in safe_headers:
        safe_headers[header] = "[REDACTED]"
```

**Rationale:** `Authorization` contiene JWT tokens — exponerlos en logs es un riesgo de seguridad (token leakage en sistemas de agregación de logs). `Cookie` puede contener tokens de sesión. No loguear bodies evita exposición accidental de contraseñas, datos de tarjeta, o PII. Esto es estándar en aplicaciones que manejan datos sensibles (OWASP Logging Cheat Sheet).

**Alternativa considerada:** Redactar solo el valor del header (mostrar `Authorization: Bearer eyJ...` → `Authorization: Bearer [REDACTED]`). Rechazada — incluso el prefijo del token puede ser útil para un atacante.

### 5. Exception Handlers — RFC 7807 Problem Details

**Decision:** Registrar handlers en `main.py` para `HTTPException` y `Exception` que devuelven RFC 7807.

```python
from fastapi.responses import JSONResponse
from http import HTTPStatus

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    request_id = getattr(request.state, "request_id", "unknown")
    logger.warning(
        f"HTTP {exc.status_code}: {exc.detail}",
        extra={"request_id": request_id, "path": request.url.path, "status": exc.status_code},
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "type": "about:blank",
            "title": HTTPStatus(exc.status_code).phrase,
            "status": exc.status_code,
            "detail": exc.detail,
            "instance": request.url.path,
        },
    )

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    request_id = getattr(request.state, "request_id", "unknown")
    logger.error(
        "Unhandled exception",
        extra={"request_id": request_id, "path": request.url.path},
        exc_info=True,
    )
    return JSONResponse(
        status_code=500,
        content={
            "type": "about:blank",
            "title": "Internal Server Error",
            "status": 500,
            "detail": "Error interno del servidor" if not DEBUG else str(exc),
            "instance": request.url.path,
        },
    )
```

**Rationale:** RFC 7807 es el estándar para error responses en HTTP APIs. Los campos `type`, `title`, `status`, `detail`, `instance` permiten a los clientes manejar errores programáticamente. `exc_info=True` en el handler de `Exception` incluye el traceback completo en el log entry (campo `traceback` del JSONFormatter). En producción (`DEBUG=false`), el `detail` es genérico para no exponer información interna. FastAPI no expone `DEBUG` como variable global — usamos `app.debug` o una variable de entorno `ENVIRONMENT`.

### 6. DEBUG Flag for Error Detail

**Decision:** Usar variable de entorno `ENVIRONMENT` para controlar si se exponen detalles internos en errores 500.

```python
import os
DEBUG = os.getenv("ENVIRONMENT", "production") == "development"
```

**Rationale:** FastAPI no tiene un flag `DEBUG` global como Django. `app.debug` existe pero solo afecta el modo debug de Starlette (auto-reload, tracebacks en HTML). Usar `ENVIRONMENT` env var es más explícito y ya está definida en `docker-compose.yml`. En desarrollo, los errores 500 muestran el mensaje de la excepción para debugging rápido.

### 7. Fix Silent Exceptions

**Decision:** Agregar `logger.warning()` con `exc_info=True` en los 2 `except Exception: pass`.

```python
# backend/app/core/dependencies.py — get_current_user dependency
except Exception:
    logger.warning("Token decode failed in get_current_user", exc_info=True)
    raise credentials_exception  # Already raises, just needs logging

# backend/app/pedidos/service.py — cancelar_pedido
except Exception:
    logger.warning("Failed to restore stock on order cancel", exc_info=True)
    # Keep behavior: stock restoration failure doesn't block cancellation
```

**Rationale:** `except Exception: pass` es un antipatrón — oculta bugs. En `dependencies.py`, el token decode failure ya lanza `HTTPException(401)` pero no deja rastro del error real (token malformado, expirado, etc.). En `pedidos/service.py`, el stock restoration falla silenciosamente — el pedido se cancela pero el stock no se restaura, causando discrepancia de inventario. El log permite detectar y corregir.

### 8. Frontend Dev Logger — Conditional Compilation

**Decision:** `devLogger` usa `import.meta.env.DEV` como guard, no como conditional runtime. Vite elimina el código en producción (tree-shaking).

```typescript
// frontend/src/shared/utils/logger.ts
const isDev = import.meta.env.DEV;

function log(level: LogLevel, action: string, data?: unknown) {
  if (!isDev) return;

  const entry: LogEntry = {
    timestamp: new Date().toISOString(),
    level,
    action,
    data,
  };

  const method = level === 'error' ? console.error
    : level === 'warn' ? console.warn
    : console.log;

  method(`[FoodStore] ${action}`, data ? entry : undefined);
}
```

**Rationale:** `import.meta.env.DEV` es una constante en tiempo de compilación (Vite). El código dentro de `if (!isDev)` es eliminado por el bundler en producción — cero overhead. El prefijo `[FoodStore]` permite filtrar logs de la app vs logs de librerías. `data ? entry : undefined` evita loguear `undefined` cuando no hay data. El mapeo de niveles a `console` methods sigue el estándar: error → console.error, warn → console.warn, info/debug → console.log.

### 9. Strategic Logging Points

**Decision:** Agregar `devLogger` en puntos específicos de acciones del usuario — no en todos los eventos.

| Archivo | Acción | Nivel | Mensaje |
|---------|--------|-------|---------|
| `authStore.ts` | Login success | info | "User logged in" |
| `authStore.ts` | Logout | info | "User logged out" |
| `authStore.ts` | Token refresh | debug | "Token refreshed" |
| `cartStore.ts` | Add to cart | info | "Item added to cart" |
| `cartStore.ts` | Remove from cart | info | "Item removed from cart" |
| `cartStore.ts` | Clear cart | info | "Cart cleared" |
| `CheckoutPage.tsx` | Payment initiated | info | "Payment initiated" |
| `CheckoutPage.tsx` | Payment success | info | "Payment succeeded" |
| `CheckoutPage.tsx` | Payment failure | error | "Payment failed" |
| `AdminOrdersPage.tsx` | Order state change | info | "Order state changed to {newState}" |
| `ErrorBoundary.tsx` | Error caught | error | Existing, enhanced with structured data |

**Rationale:** No se loguea cada interacción — solo acciones con impacto en el estado del negocio (auth, cart, payment, order FSM). Demasiado logging genera ruido y hace que los logs importantes sean difíciles de encontrar. El nivel `debug` para token refresh evita spam (los refresh ocurren automáticamente cada ~14 min). Los stores de Zustand son el lugar natural porque centralizan el estado — una sola llamada a `devLogger` cubre todos los dispatchers.

### 10. Axios Logging — Response Interceptor

**Decision:** Agregar `devLogger.debug()` en el interceptor de respuesta de axios.

```typescript
// En shared/api/client.ts, success handler del interceptor:
if (import.meta.env.DEV) {
  const method = response.config.method?.toUpperCase() ?? 'UNKNOWN';
  const url = response.config.url ?? 'UNKNOWN';
  devLogger.debug(`API ${method} ${url}`, {
    status: response.status,
    // Duration not available without request interceptor timestamp
  });
}
```

**Rationale:** Loggear todas las requests HTTP en dev mode ayuda a debuggear problemas de API (requests duplicadas, 404, timeouts). El interceptor de respuesta es el punto correcto porque tiene acceso a method, URL, y status code. No se calcula duration porque requeriría un interceptor de request para guardar el timestamp — complejidad innecesaria para dev logging.

### 11. TanStack Query DevTools — Condicional

**Decision:** Envolver `<ReactQueryDevtools>` en un conditional render: solo si `import.meta.env.DEV`.

```tsx
{import.meta.env.DEV && <ReactQueryDevtools initialIsOpen={false} />}
```

**Rationale:** Actualmente los DevTools están en el bundle de producción (aunque `initialIsOpen={false}`). Render condicional con `import.meta.env.DEV` garantiza que el código es tree-shaken en producción, reduciendo el bundle size. Alternativamente, Vite ya tree-shakea `initialIsOpen={false}`? No — el componente entero se incluye en el bundle aunque esté cerrado.

## Architecture

```
backend/app/
├── core/
│   ├── logging.py           (NEW — JSONFormatter + setup_logging())
│   ├── middleware.py         (NEW — logging_middleware with request ID, duration, redaction)
│   ├── config.py             (MOD — add ENVIRONMENT/DEBUG resolution if needed)
│   ├── dependencies.py       (MOD — fix bare except, add logger.warning)
│   └── exceptions.py         (UNCHANGED — existing HTTPException subclasses)
├── main.py                   (MOD — call setup_logging(), register middleware, register exception handlers)
├── pedidos/
│   └── service.py            (MOD — fix bare except, add logger.warning)
└── db/
    └── seed.py               (MOD — replace print() with logging.info())

frontend/src/
├── shared/
│   ├── utils/
│   │   └── logger.ts         (NEW — devLogger with isDev guard, structured format)
│   ├── api/
│   │   └── client.ts         (MOD — add devLogger to response interceptor)
│   └── components/
│       └── ErrorBoundary.tsx  (MOD — enhance console.error with structured data)
├── stores/
│   ├── authStore.ts          (MOD — devLogger calls on login/logout/refresh)
│   └── cartStore.ts          (MOD — devLogger calls on add/remove/clear)
├── pages/
│   └── (checkout, admin orders pages — devLogger calls)
└── app/
    └── providers.tsx          (MOD — conditional ReactQueryDevtools render)
```

## Risks / Trade-offs

| Risk | Mitigation |
|------|-----------|
| JSON logs en stdout pueden ser difíciles de leer en desarrollo local | En desarrollo, se puede agregar un handler con formato human-readable condicionado a `ENVIRONMENT=development`. Fuera de scope para este change. |
| Redacción de headers puede romper debugging de auth issues | Solo se redacta en logs, no en la request real. Para debuggear auth, usar las herramientas del navegador o logs de aplicación con `logger.debug`. |
| `getattr(request.state, "request_id", "unknown")` falla si el middleware no se ejecutó antes | El orden de middleware en FastAPI es LIFO — el middleware http se registra primero (se ejecuta último en el stack). Pero como es el único middleware además de CORS, siempre se ejecuta antes de los handlers. |
| `print()` en `seed.py` — migrar a logging puede requerir configurar logging antes de la app | `setup_logging()` se llama antes de `app = FastAPI(...)`, por lo que el logger está disponible para seed.py si se importa después. Seed.py debe importar `setup_logging()` y llamarlo, o usar `logging.getLogger(__name__)` (hereda config del root). |
| Axios logging puede ser verboso en páginas con muchas requests (ej: admin tables con paginación) | Usar nivel `debug` para axios — no interfiere con logs `info` de acciones de usuario. En dev tools del navegador, se puede filtrar por level. |
| ReactQueryDevtools condicional puede causar hydration mismatch en SSR | No aplica — Food Store es SPA client-side rendering con Vite. |

## Open Questions

1. ¿Deberían los logs de excepciones incluir el request body para facilitar reproducción? (No — riesgo de exponer contraseñas, tokens, datos de tarjeta. Además el body solo está disponible como stream en ASGI, consumirlo afecta los handlers downstream.)
2. ¿Debería `LOG_LEVEL` tener un default diferente en desarrollo (`DEBUG`) vs producción (`INFO`)? (Por ahora `INFO` para ambos. Se puede ajustar en docker-compose por entorno sin cambiar código.)
3. ¿Debería agregarse un file handler para logs en desarrollo local (más fácil de leer que stdout JSON)? (Nice to have. Se puede agregar como handler adicional en `setup_logging()` condicionado a `ENVIRONMENT=development`.)
4. ¿Debería incluirse `SQLAlchemy` query logging (`echo=True`) condicionado a `LOG_LEVEL=DEBUG`? (Fuera de scope para este change — requiere cambios en `database.py` y puede generar muchísimo output. Evaluar en change separado de performance.)
