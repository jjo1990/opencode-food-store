"""
Request/Response schemas for ingredientes
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class IngredienteCreate(BaseModel):
    """Create ingrediente request schema"""

    nombre: str = Field(..., min_length=1, max_length=100)
    es_alergeno: bool = False


class IngredienteUpdate(BaseModel):
    """Update ingrediente request schema"""

    nombre: str | None = Field(None, max_length=100)
    es_alergeno: bool | None = None


class IngredienteResponse(BaseModel):
    """Ingrediente response schema"""

    id: UUID
    nombre: str
    es_alergeno: bool
    created_at: datetime

    class Config:
        from_attributes = True


class PaginatedIngredientes(BaseModel):
    """Paginated ingredientes response schema"""

    items: list[IngredienteResponse]
    total: int
    skip: int
    limit: int
