"""
Ingredientes routes
"""

from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_role
from app.ingredientes.schemas import (
    IngredienteCreate,
    IngredienteResponse,
    IngredienteUpdate,
    PaginatedIngredientes,
)
from app.ingredientes.service import IngredienteService

router = APIRouter(
    prefix="/ingredientes",
    tags=["ingredientes"],
)


@router.post("", response_model=IngredienteResponse, status_code=status.HTTP_201_CREATED)
async def create_ingrediente(
    data: IngredienteCreate,
    current_user=Depends(require_role("ADMIN", "STOCK")),
    db: Session = Depends(get_db),
) -> IngredienteResponse:
    """Create a new ingrediente (ADMIN, STOCK only)"""
    service = IngredienteService(db)
    return service.create_ingrediente(data)


@router.get("", response_model=PaginatedIngredientes)
async def list_ingredientes(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    es_alergeno: bool | None = Query(None),
    db: Session = Depends(get_db),
) -> PaginatedIngredientes:
    """List ingredientes with pagination (public)"""
    service = IngredienteService(db)
    return service.list_ingredientes(skip=skip, limit=limit, es_alergeno=es_alergeno)


@router.get("/{id}", response_model=IngredienteResponse)
async def get_ingrediente(
    id: UUID,
    db: Session = Depends(get_db),
) -> IngredienteResponse:
    """Get a single ingrediente by ID (public)"""
    service = IngredienteService(db)
    return service.get_ingrediente(id)


@router.put("/{id}", response_model=IngredienteResponse)
async def update_ingrediente(
    id: UUID,
    data: IngredienteUpdate,
    current_user=Depends(require_role("ADMIN", "STOCK")),
    db: Session = Depends(get_db),
) -> IngredienteResponse:
    """Update an ingrediente (ADMIN, STOCK only)"""
    service = IngredienteService(db)
    return service.update_ingrediente(id, data)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ingrediente(
    id: UUID,
    current_user=Depends(require_role("ADMIN", "STOCK")),
    db: Session = Depends(get_db),
) -> None:
    """Soft delete an ingrediente (ADMIN, STOCK only)"""
    service = IngredienteService(db)
    service.delete_ingrediente(id)
