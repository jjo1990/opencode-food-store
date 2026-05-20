"""
Request/Response schemas for productos
"""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class ProductoCreate(BaseModel):
    """Create producto request schema"""

    nombre: str = Field(..., min_length=1, max_length=200)
    descripcion: str | None = None
    precio_base: Decimal = Field(..., gt=0)
    stock_cantidad: int = Field(0, ge=0)
    disponible: bool = True
    imagen_url: str | None = Field(None, max_length=500)
    categoria_ids: list[UUID] = []
    ingrediente_ids: list[UUID] = []


class ProductoUpdate(BaseModel):
    """Update producto request schema"""

    nombre: str | None = Field(None, min_length=1, max_length=200)
    descripcion: str | None = None
    precio_base: Decimal | None = Field(None, gt=0)
    stock_cantidad: int | None = Field(None, ge=0)
    disponible: bool | None = None
    imagen_url: str | None = Field(None, max_length=500)
    categoria_ids: list[UUID] | None = None
    ingrediente_ids: list[UUID] | None = None


class ProductoDisponibilidadUpdate(BaseModel):
    """Toggle producto disponibilidad request schema"""

    disponible: bool


class ProductoResponse(BaseModel):
    """Producto response schema"""

    id: UUID
    nombre: str
    descripcion: str | None = None
    precio_base: Decimal
    stock_cantidad: int
    disponible: bool
    imagen_url: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True


class IngredienteEnProducto(BaseModel):
    """Ingrediente within a producto context"""

    id: UUID
    nombre: str
    es_alergeno: bool
    es_removible: bool


class CategoriaEnProducto(BaseModel):
    """Categoria within a producto context"""

    id: UUID
    nombre: str


class ProductoDetail(ProductoResponse):
    """Detailed producto response with relations"""

    categorias: list[CategoriaEnProducto] = []
    ingredientes: list[IngredienteEnProducto] = []


class PaginatedProductos(BaseModel):
    """Paginated productos response schema"""

    items: list[ProductoResponse]
    total: int
    skip: int
    limit: int


class PublicProductoResponse(BaseModel):
    """Public producto response (no stock_cantidad)"""

    id: UUID
    nombre: str
    descripcion: str | None = None
    precio_base: Decimal
    disponible: bool
    imagen_url: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True


class PublicProductoDetail(PublicProductoResponse):
    """Public producto detail with relations"""

    categorias: list[CategoriaEnProducto] = []
    ingredientes: list[IngredienteEnProducto] = []


class PublicPaginatedProductos(BaseModel):
    """Public paginated productos response schema"""

    items: list[PublicProductoResponse]
    total: int
    skip: int
    limit: int
