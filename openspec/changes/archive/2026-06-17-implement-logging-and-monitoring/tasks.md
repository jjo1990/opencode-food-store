# Tasks: implement-logging-and-monitoring

## 1. Backend Logging Setup

- [ ] 1.1 Create `backend/app/core/logging.py` with `JSONFormatter` class (extends `logging.Formatter`)
- [ ] 1.2 `JSONFormatter.format()` outputs JSON with: timestamp (ISO 8601 UTC), level, logger, message, module, function
- [ ] 1.3 `JSONFormatter.format()` includes `exception` and `traceback` fields when `exc_info` is present
- [ ] 1.4 `JSONFormatter.format()` merges custom `extra` fields (request_id, duration_ms, etc.) into the JSON output
- [ ] 1.5 Implement `setup_logging()` function — reads `LOG_LEVEL` from env (default `"INFO"`)
- [ ] 1.6 `setup_logging()` creates a `StreamHandler(sys.stdout)` with `JSONFormatter` and replaces root logger handlers
- [ ] 1.7 Call `setup_logging()` in `backend/app/main.py` BEFORE `app = FastAPI(...)`

## 2. Backend Request Logging Middleware

- [ ] 2.1 Create `backend/app/core/middleware.py` with `logging_middleware` async function
- [ ] 2.2 Generate request ID (`str(uuid.uuid4())[:8]`) and store in `request.state.request_id`
- [ ] 2.3 Skip logging for health check paths (`/health`, `/`)
- [ ] 2.4 Log method, path, query params, status code, and duration_ms on request completion
- [ ] 2.5 Use log level based on status code: INFO (2xx/3xx), WARNING (4xx), ERROR (5xx)
- [ ] 2.6 Add `X-Request-ID` header to response with the generated request ID
- [ ] 2.7 Redact sensitive headers (Authorization, Cookie) if headers are included in log context
- [ ] 2.8 Register middleware in `backend/app/main.py` using `@app.middleware("http")` after `setup_logging()`

## 3. Backend Exception Handlers

- [ ] 3.1 Add `DEBUG` resolution in `main.py`: read `ENVIRONMENT` env var, `DEBUG = ENVIRONMENT == "development"`
- [ ] 3.2 Register `HTTPException` handler — returns RFC 7807 (type, title, status, detail, instance)
- [ ] 3.3 `HTTPException` handler logs at WARNING level with request_id, path, and status
- [ ] 3.4 Register unhandled `Exception` handler — returns RFC 7807 with 500 status
- [ ] 3.5 Unhandled `Exception` handler logs at ERROR level with `exc_info=True` (includes traceback)
- [ ] 3.6 Unhandled handler hides internal details (detail = `"Error interno del servidor"`) unless `DEBUG=true`
- [ ] 3.7 Both handlers use `getattr(request.state, "request_id", "unknown")` for safe access

## 4. Fix Silent Exception Swallowing

- [ ] 4.1 In `backend/app/core/dependencies.py`, fix `except Exception: pass` → add `logger.warning("Token decode failed in get_current_user", exc_info=True)` before re-raising
- [ ] 4.2 In `backend/app/pedidos/service.py`, fix `except Exception: pass` → add `logger.warning("Failed to restore stock on order cancel", exc_info=True)`
- [ ] 4.3 In `backend/app/db/seed.py`, replace all `print()` calls with `logging.getLogger(__name__).info()` (ensure `setup_logging` is called or imported before logging)

## 5. Frontend Dev Logger Utility

- [ ] 5.1 Create `frontend/src/shared/utils/logger.ts` with `LogLevel`, `LogEntry` interfaces, and `log()` function
- [ ] 5.2 `log()` function checks `import.meta.env.DEV` — silently returns if not in development mode
- [ ] 5.3 `LogEntry` includes: `timestamp` (ISO string), `level` (LogLevel), `action` (string), `data?` (unknown)
- [ ] 5.4 Map levels to console methods: `error` → `console.error`, `warn` → `console.warn`, `info`/`debug` → `console.log`
- [ ] 5.5 Prefix all log messages with `[FoodStore]`
- [ ] 5.6 Export `devLogger` object with methods: `debug()`, `info()`, `warn()`, `error()`

## 6. Frontend Strategic Logging — Auth & Cart

- [ ] 6.1 Import `devLogger` in `stores/authStore.ts`
- [ ] 6.2 Add `devLogger.info("User logged in", { email })` after successful login
- [ ] 6.3 Add `devLogger.info("User logged out")` in logout action
- [ ] 6.4 Add `devLogger.debug("Token refreshed")` in token refresh action
- [ ] 6.5 Import `devLogger` in `stores/cartStore.ts`
- [ ] 6.6 Add `devLogger.info("Item added to cart", { productId, name })` in addToCart action
- [ ] 6.7 Add `devLogger.info("Item removed from cart", { productId })` in removeFromCart action
- [ ] 6.8 Add `devLogger.info("Cart cleared")` in clearCart action

## 7. Frontend Strategic Logging — Payment & Orders

- [ ] 7.1 Add `devLogger.info("Payment initiated", { orderId })` when user clicks pay button in CheckoutPage
- [ ] 7.2 Add `devLogger.info("Payment succeeded", { orderId, paymentId })` on payment success callback
- [ ] 7.3 Add `devLogger.error("Payment failed", { orderId, error })` on payment failure
- [ ] 7.4 Add `devLogger.info("Order state changed", { orderId, newState })` on admin order state change action

## 8. Axios Logging & ErrorBoundary

- [ ] 8.1 Import `devLogger` in `frontend/src/shared/api/client.ts`
- [ ] 8.2 In axios response success interceptor, add `devLogger.debug()` with method, URL, and status (guarded by `import.meta.env.DEV`)
- [ ] 8.3 In `frontend/src/shared/components/ErrorBoundary.tsx`, enhance existing `console.error` with structured data (component name, error message, stack)
- [ ] 8.4 Log error info alongside the existing error log in ErrorBoundary

## 9. TanStack Query DevTools

- [ ] 9.1 In `frontend/src/app/providers.tsx`, wrap `ReactQueryDevtools` in conditional: `{import.meta.env.DEV && <ReactQueryDevtools initialIsOpen={false} />}`
- [ ] 9.2 Verify current `initialIsOpen={false}` is preserved

## 10. Verification

- [ ] 10.1 Run backend tests: `pytest` in `backend/`
- [ ] 10.2 Run frontend type check: `npx tsc --noEmit` in `frontend/`
- [ ] 10.3 Start backend and verify JSON log lines appear in stdout (check valid JSON: parse with `jq` or python)
- [ ] 10.4 Make a request and verify `X-Request-ID` header is present in response
- [ ] 10.5 Verify request log entry includes method, path, status, duration_ms, and request_id
- [ ] 10.6 Trigger a 404 error and verify log level is WARNING
- [ ] 10.7 Trigger a 500 error and verify log level is ERROR with traceback
- [ ] 10.8 Verify health check requests (`GET /health`) do NOT produce log entries
- [ ] 10.9 Verify RFC 7807 format in error responses: check for `type`, `title`, `status`, `detail`, `instance` fields
- [ ] 10.10 Verify 500 error detail is generic in non-development mode
- [ ] 10.11 Verify `LOG_LEVEL=DEBUG` makes debug logs appear; `LOG_LEVEL=WARNING` suppresses info logs
- [ ] 10.12 Verify no bare `except Exception: pass` remains (grep for the pattern in backend)
- [ ] 10.13 Run frontend in dev mode (`vite dev`) and verify auth/cart/payment actions produce `[FoodStore]` console logs
- [ ] 10.14 Run frontend in preview mode (`vite preview`) and verify NO `[FoodStore]` logs appear
- [ ] 10.15 Verify `ReactQueryDevtools` logo appears in dev mode, NOT in production mode
- [ ] 10.16 Verify axios requests are logged in dev console with method, URL, and status
