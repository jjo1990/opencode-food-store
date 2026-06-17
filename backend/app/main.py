"""
Food Store FastAPI Backend
"""

import logging
import os

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.admin.router import router as admin_router
from app.auth.router import router as auth_router
from app.categorias.router import router as categorias_router
from app.checkout.router import router as checkout_router
from app.core.config import CORS_ORIGINS
from app.core.logging import setup_logging
from app.core.middleware import logging_middleware
from app.direcciones.router import router as direcciones_router
from app.ingredientes.router import router as ingredientes_router
from app.pagos.router import router as pagos_router
from app.pedidos.router import router as pedidos_router
from app.productos.router import router as productos_router
from app.usuarios.router import router as usuarios_router

logger = logging.getLogger(__name__)

DEBUG = os.getenv("ENVIRONMENT", "production") == "development"

setup_logging()

app = FastAPI(
    title="Food Store API",
    version="0.0.1",
    description="API REST para gestión de pedidos de comida. Plataforma e-commerce full-stack.",
    contact={"name": "Food Store Team"},
    license_info={"name": "MIT"},
)

app.middleware("http")(logging_middleware)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(admin_router, prefix="/api/v1")
app.include_router(checkout_router, prefix="/api/v1")
app.include_router(categorias_router, prefix="/api/v1")
app.include_router(ingredientes_router, prefix="/api/v1")
app.include_router(pagos_router, prefix="/api/v1")
app.include_router(pedidos_router, prefix="/api/v1")
app.include_router(productos_router, prefix="/api/v1")
app.include_router(direcciones_router, prefix="/api/v1")
app.include_router(usuarios_router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Food Store API v0.0.1"}


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "ok"}


def _get_request_id(request: Request) -> str:
    return getattr(request.state, "request_id", "unknown")


def _status_phrase(code: int) -> str:
    phrases = {
        400: "Bad Request",
        401: "Unauthorized",
        403: "Forbidden",
        404: "Not Found",
        409: "Conflict",
        422: "Unprocessable Entity",
        429: "Too Many Requests",
        500: "Internal Server Error",
    }
    return phrases.get(code, "Unknown")


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.warning(
        f"HTTP {exc.status_code}: {exc.detail}",
        extra={
            "request_id": _get_request_id(request),
            "path": request.url.path,
            "status": exc.status_code,
        },
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "type": "about:blank",
            "title": _status_phrase(exc.status_code),
            "status": exc.status_code,
            "detail": exc.detail,
            "instance": request.url.path,
        },
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.error(
        "Unhandled exception",
        extra={
            "request_id": _get_request_id(request),
            "path": request.url.path,
        },
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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
