"""
Categorias routes
"""

from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.categorias.schemas import (
    CategoriaCreate,
    CategoriaResponse,
    CategoriaTreeNode,
    CategoriaUpdate,
)
from app.categorias.service import CategoriaService
from app.core.database import get_db
from app.core.dependencies import require_role

router = APIRouter(
    prefix="/categorias",
    tags=["categorias"],
)


@router.post("", response_model=CategoriaResponse, status_code=status.HTTP_201_CREATED)
async def create_categoria(
    data: CategoriaCreate,
    current_user=Depends(require_role("ADMIN", "STOCK")),
    db: Session = Depends(get_db),
) -> CategoriaResponse:
    """Create a new categoria (ADMIN, STOCK only)"""
    service = CategoriaService(db)
    return service.create_categoria(data)


@router.get("", response_model=list[CategoriaTreeNode])
async def get_categorias_tree(
    db: Session = Depends(get_db),
) -> list[CategoriaTreeNode]:
    """Get full hierarchical category tree (public)"""
    service = CategoriaService(db)
    return service.get_tree()


@router.get("/{id}", response_model=CategoriaResponse)
async def get_categoria(
    id: UUID,
    db: Session = Depends(get_db),
) -> CategoriaResponse:
    """Get a single categoria by ID (public)"""
    service = CategoriaService(db)
    return service.get_categoria(id)


@router.put("/{id}", response_model=CategoriaResponse)
async def update_categoria(
    id: UUID,
    data: CategoriaUpdate,
    current_user=Depends(require_role("ADMIN", "STOCK")),
    db: Session = Depends(get_db),
) -> CategoriaResponse:
    """Update a categoria (ADMIN, STOCK only)"""
    service = CategoriaService(db)
    return service.update_categoria(id, data)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_categoria(
    id: UUID,
    current_user=Depends(require_role("ADMIN", "STOCK")),
    db: Session = Depends(get_db),
) -> None:
    """Soft delete a categoria (ADMIN, STOCK only)"""
    service = CategoriaService(db)
    service.delete_categoria(id)
