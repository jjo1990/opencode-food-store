"""
Productos routes
"""

from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_optional_current_user, require_role
from app.models import User
from app.productos.schemas import (
    IngredienteEnProducto,
    PaginatedProductos,
    ProductoCreate,
    ProductoDetail,
    ProductoDisponibilidadUpdate,
    ProductoResponse,
    ProductoUpdate,
    PublicPaginatedProductos,
    PublicProductoDetail,
)
from app.productos.service import ProductoService

router = APIRouter(
    prefix="/productos",
    tags=["productos"],
)


@router.post("", response_model=ProductoDetail, status_code=status.HTTP_201_CREATED)
async def create_producto(
    data: ProductoCreate,
    current_user=Depends(require_role("ADMIN", "STOCK")),
    db: Session = Depends(get_db),
) -> ProductoDetail:
    """Create a new producto (ADMIN, STOCK only)"""
    service = ProductoService(db)
    return service.create_producto(data)


@router.get("", response_model=PaginatedProductos | PublicPaginatedProductos)
async def list_productos(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    categoria_id: UUID | None = Query(None),
    nombre: str | None = Query(None),
    disponible: bool | None = Query(None),
    precio_min: Decimal | None = Query(None, ge=0),
    precio_max: Decimal | None = Query(None, ge=0),
    incluir_eliminados: bool = Query(
        False, description="Incluir productos soft-deleted (solo ADMIN/STOCK)"
    ),
    current_user: User | None = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
) -> PaginatedProductos | PublicPaginatedProductos:
    """List productos with pagination and filters"""
    service = ProductoService(db)
    is_admin = current_user and any(r.role in ("ADMIN", "STOCK") for r in current_user.roles)
    is_public = not is_admin
    include_deleted = incluir_eliminados and is_admin
    return service.list_productos(
        skip=skip,
        limit=limit,
        categoria_id=categoria_id,
        nombre=nombre,
        disponible=disponible,
        precio_min=precio_min,
        precio_max=precio_max,
        is_public=is_public,
        include_deleted=include_deleted,
    )


@router.get("/{id}", response_model=ProductoDetail | PublicProductoDetail)
async def get_producto(
    id: UUID,
    current_user: User | None = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
) -> ProductoDetail | PublicProductoDetail:
    """Get a single producto by ID with relations"""
    service = ProductoService(db)
    is_admin = current_user and any(r.role in ("ADMIN", "STOCK") for r in current_user.roles)
    if is_admin:
        return service.get_producto(id)
    return service.get_producto_public(id)


@router.put("/{id}", response_model=ProductoDetail)
async def update_producto(
    id: UUID,
    data: ProductoUpdate,
    current_user=Depends(require_role("ADMIN", "STOCK")),
    db: Session = Depends(get_db),
) -> ProductoDetail:
    """Update a producto (ADMIN, STOCK only)"""
    service = ProductoService(db)
    return service.update_producto(id, data)


@router.patch("/{id}/disponibilidad", response_model=ProductoResponse)
async def toggle_disponibilidad(
    id: UUID,
    data: ProductoDisponibilidadUpdate,
    current_user=Depends(require_role("ADMIN", "STOCK")),
    db: Session = Depends(get_db),
) -> ProductoResponse:
    """Toggle producto disponibilidad (ADMIN, STOCK only)"""
    service = ProductoService(db)
    return service.toggle_disponibilidad(id, data)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_producto(
    id: UUID,
    current_user=Depends(require_role("ADMIN", "STOCK")),
    db: Session = Depends(get_db),
) -> None:
    """Soft delete a producto (ADMIN, STOCK only)"""
    service = ProductoService(db)
    service.delete_producto(id)


@router.get("/{id}/ingredientes", response_model=list[IngredienteEnProducto])
async def get_ingredientes(
    id: UUID,
    db: Session = Depends(get_db),
) -> list[IngredienteEnProducto]:
    """Get ingredientes for a producto (public)"""
    service = ProductoService(db)
    return service.get_ingredientes(id)
