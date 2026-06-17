# logging-backend Specification

## Purpose

Especifica el sistema de logging estructurado y observabilidad para el backend de Food Store. Cubre el formato JSON de logs, middleware de request/response con request ID, exception handlers RFC 7807, redacción de datos sensibles, eliminación de excepciones silenciosas, y respeto de la variable de entorno LOG_LEVEL.

## ADDED Requirements

### Requirement: Logs MUST be valid JSON with required fields

El sistema DEBE emitir todos los logs en formato JSON con los campos obligatorios: timestamp, level, logger, message.

#### Scenario: Info log contains required fields

- **WHEN** se llama a `logger.info("Producto creado", extra={"product_id": 42})`
- **THEN** la salida es una línea JSON válida que contiene `"timestamp"`, `"level": "INFO"`, `"logger"`, `"message": "Producto creado"`, `"product_id": 42`

#### Scenario: Warning log contains module and function

- **WHEN** se llama a `logger.warning("Stock bajo")` desde el módulo `productos/service.py` en la función `validar_stock`
- **THEN** el log JSON contiene `"module": "service"` y `"function": "validar_stock"`

#### Scenario: Error log contains exception and traceback

- **WHEN** se llama a `logger.error("Falló el pago", exc_info=True)` dentro de un bloque `except ValueError as e`
- **THEN** el log JSON contiene `"exception": "<mensaje de ValueError>"` y `"traceback"` con el stack trace completo

---

### Requirement: Logger level MUST respect LOG_LEVEL environment variable

El sistema DEBE configurar el nivel del root logger según la variable de entorno `LOG_LEVEL`.

#### Scenario: LOG_LEVEL is DEBUG

- **WHEN** la variable de entorno `LOG_LEVEL` es `"DEBUG"`
- **THEN** los logs con nivel `DEBUG`, `INFO`, `WARNING`, `ERROR` son emitidos

#### Scenario: LOG_LEVEL is WARNING

- **WHEN** la variable de entorno `LOG_LEVEL` es `"WARNING"`
- **THEN** los logs con nivel `DEBUG` e `INFO` NO son emitidos
- **AND** los logs con nivel `WARNING`, `ERROR` son emitidos

#### Scenario: LOG_LEVEL is not set

- **WHEN** la variable de entorno `LOG_LEVEL` no está definida
- **THEN** el nivel del logger es `INFO` (default)

#### Scenario: LOG_LEVEL is invalid

- **WHEN** la variable de entorno `LOG_LEVEL` es `"INVALIDO"`
- **THEN** el nivel del logger es `INFO` (fallback seguro)

---

### Requirement: Every HTTP request MUST be logged with method, path, status, and duration

El sistema DEBE loguear cada request HTTP con el método, path, query params, status code, y duración en milisegundos.

#### Scenario: Successful GET request is logged at INFO

- **WHEN** se hace un request `GET /api/v1/productos?categoria=1` que retorna `200 OK` en 45ms
- **THEN** se emite un log con `"level": "INFO"`, `"method": "GET"`, `"path": "/api/v1/productos"`, `"query": "categoria=1"`, `"status": 200`, `"duration_ms"` ≈ 45

#### Scenario: 404 request is logged at WARNING

- **WHEN** se hace un request `GET /api/v1/productos/999` que retorna `404 Not Found`
- **THEN** se emite un log con `"level": "WARNING"`, `"status": 404`

#### Scenario: 500 error is logged at ERROR

- **WHEN** se hace un request que causa una excepción no manejada y retorna `500 Internal Server Error`
- **THEN** se emite un log con `"level": "ERROR"`, `"status": 500`

---

### Requirement: Response MUST include X-Request-ID header

El sistema DEBE generar un request ID único por cada request y devolverlo en el header `X-Request-ID` de la response.

#### Scenario: Response contains X-Request-ID

- **WHEN** se hace cualquier request HTTP al backend (excepto health checks)
- **THEN** la response incluye el header `X-Request-ID` con un valor no vacío

#### Scenario: Request ID is included in log entries

- **WHEN** se loguea un request
- **THEN** el log JSON contiene el campo `"request_id"` con el mismo valor que el header `X-Request-ID` de la response

#### Scenario: Request ID is available in exception handlers

- **WHEN** ocurre una excepción durante el procesamiento de un request
- **THEN** el log de la excepción contiene `"request_id"` con el mismo valor del request

---

### Requirement: Health check endpoints MUST NOT be logged

El sistema NO DEBE loguear requests a los endpoints de health check para evitar ruido en los logs.

#### Scenario: GET /health is not logged

- **WHEN** se hace un request `GET /health`
- **THEN** NO se emite un log de request

#### Scenario: GET / is not logged

- **WHEN** se hace un request `GET /`
- **THEN** NO se emite un log de request

---

### Requirement: Sensitive headers MUST be redacted in logs

El sistema DEBE redactar los valores de los headers `Authorization` y `Cookie` en cualquier log.

#### Scenario: Authorization header is redacted

- **WHEN** un request incluye el header `Authorization: Bearer eyJhbGciOi...`
- **THEN** si se loguean los headers, el valor de `Authorization` aparece como `[REDACTED]`

#### Scenario: Cookie header is redacted

- **WHEN** un request incluye el header `Cookie: session=abc123`
- **THEN** si se loguean los headers, el valor de `Cookie` aparece como `[REDACTED]`

---

### Requirement: HTTPException MUST be logged at WARNING with status and detail

El sistema DEBE loguear toda `HTTPException` lanzada por la aplicación con nivel WARNING, incluyendo el status code y el mensaje de error.

#### Scenario: 401 Unauthorized is logged

- **WHEN** un request no autenticado intenta acceder a un endpoint protegido y se lanza `HTTPException(401, "No autenticado")`
- **THEN** se emite un log con `"level": "WARNING"`, `"status": 401`, y el mensaje contiene `"No autenticado"`

#### Scenario: 404 Not Found is logged

- **WHEN** un request busca un recurso inexistente y se lanza `HTTPException(404, "Producto no encontrado")`
- **THEN** se emite un log con `"level": "WARNING"`, `"status": 404`

---

### Requirement: Unhandled exceptions MUST be logged at ERROR with traceback

El sistema DEBE loguear toda excepción no manejada con nivel ERROR, incluyendo el traceback completo.

#### Scenario: ValueError in handler is logged with traceback

- **WHEN** un endpoint lanza `ValueError("Dato inválido")` que no es capturado por el servicio
- **THEN** se emite un log con `"level": "ERROR"`, `"message": "Unhandled exception"`, y `"traceback"` con el stack trace completo

#### Scenario: Database connection error is logged with traceback

- **WHEN** ocurre un error de conexión a la base de datos durante un request
- **THEN** se emite un log con `"level": "ERROR"` y `"traceback"` con el stack trace

---

### Requirement: Error responses MUST follow RFC 7807 Problem Details format

El sistema DEBE devolver errores HTTP en formato RFC 7807 con los campos type, title, status, detail, instance.

#### Scenario: 404 error response is RFC 7807

- **WHEN** un request resulta en un error 404
- **THEN** el body de la response contiene `"type": "about:blank"`, `"title": "Not Found"`, `"status": 404`, `"detail"`, `"instance"`

#### Scenario: 401 error response is RFC 7807

- **WHEN** un request resulta en un error 401
- **THEN** el body de la response contiene `"type": "about:blank"`, `"title": "Unauthorized"`, `"status": 401`

#### Scenario: 500 error response hides internal details in production

- **WHEN** ocurre un error 500 y `ENVIRONMENT` no es `"development"`
- **THEN** el campo `"detail"` es `"Error interno del servidor"` y NO contiene el mensaje de la excepción original

#### Scenario: 500 error response shows details in development

- **WHEN** ocurre un error 500 y `ENVIRONMENT` es `"development"`
- **THEN** el campo `"detail"` contiene el mensaje de la excepción original

---

### Requirement: No bare except: pass without logging MUST exist

El sistema NO DEBE contener bloques `except Exception: pass` que traguen errores silenciosamente. Todo bloque de excepción DEBE al menos loguear un warning.

#### Scenario: Token decode failure logs warning

- **WHEN** falla el decode de un JWT token en `get_current_user` y se captura `except Exception`
- **THEN** se emite un log con `"level": "WARNING"` que incluye el traceback de la excepción original

#### Scenario: Stock restoration failure logs warning

- **WHEN** falla la restauración de stock al cancelar un pedido y se captura `except Exception`
- **THEN** se emite un log con `"level": "WARNING"` que incluye el traceback de la excepción original

---

### Requirement: Seed script MUST use logging instead of print

El sistema DEBE usar `logging` en lugar de `print()` para la salida del script de seed de la base de datos.

#### Scenario: Seed script outputs via logging

- **WHEN** se ejecuta el script de seed
- **THEN** los mensajes de progreso se emiten como logs con nivel `INFO` en formato JSON
- **AND** no hay llamadas a `print()` en el código de seed
