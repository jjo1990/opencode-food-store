"""
Food Store FastAPI Backend
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.admin.router import router as admin_router
from app.auth.router import router as auth_router
from app.categorias.router import router as categorias_router
from app.checkout.router import router as checkout_router
from app.core.config import CORS_ORIGINS
from app.direcciones.router import router as direcciones_router
from app.ingredientes.router import router as ingredientes_router
from app.productos.router import router as productos_router
from app.usuarios.router import router as usuarios_router

app = FastAPI(title="Food Store API", version="0.0.1")

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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
