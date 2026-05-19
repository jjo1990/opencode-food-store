"""
Request/Response schemas for categorias
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class CategoriaCreate(BaseModel):
    """Create categoria request schema"""

    nombre: str = Field(..., min_length=1, max_length=100)
    parent_id: UUID | None = None


class CategoriaUpdate(BaseModel):
    """Update categoria request schema"""

    nombre: str | None = Field(None, max_length=100)
    parent_id: UUID | None = None


class CategoriaResponse(BaseModel):
    """Categoria response schema"""

    id: UUID
    nombre: str
    parent_id: UUID | None = None
    created_at: datetime

    class Config:
        from_attributes = True


class CategoriaTreeNode(BaseModel):
    """Categoria tree node with children"""

    id: UUID
    nombre: str
    parent_id: UUID | None = None
    children: list["CategoriaTreeNode"] = []
