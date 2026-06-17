import logging
import time
import uuid

from fastapi import Request, Response

logger = logging.getLogger(__name__)

SKIP_PATHS = {"/health", "/", "/docs", "/redoc", "/openapi.json"}


async def logging_middleware(request: Request, call_next):
    """Log every HTTP request with method, path, status, and duration."""
    request_id = str(uuid.uuid4())[:8]
    request.state.request_id = request_id

    if request.url.path in SKIP_PATHS or request.url.path.startswith("/docs"):
        response: Response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response

    start = time.perf_counter()
    response: Response = await call_next(request)
    duration_ms = (time.perf_counter() - start) * 1000

    log_level = (
        logging.ERROR if response.status_code >= 500
        else logging.WARNING if response.status_code >= 400
        else logging.INFO
    )

    logger.log(
        log_level,
        "Request completed",
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "query": str(request.query_params) if request.query_params else "",
            "status": response.status_code,
            "duration_ms": round(duration_ms, 2),
        },
    )

    response.headers["X-Request-ID"] = request_id
    return response
