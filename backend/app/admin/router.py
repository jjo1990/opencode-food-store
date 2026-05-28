"""
Admin routes for role-based access control and user management
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.admin.schemas import AdminUserListResponse, AdminUserResponse, AdminUserUpdateRequest
from app.admin.service import AdminService
from app.auth.schemas import UpdateRolesRequest, UserResponse
from app.core.database import get_db
from app.core.dependencies import require_role
from app.core.exceptions import ForbiddenException, UserNotFoundException
from app.models import User

router = APIRouter(prefix="/admin", tags=["admin"])


# ─── Existing endpoints (role management) ────────────────────────────────────


@router.put("/users/{user_id}/roles", response_model=UserResponse)
async def update_user_roles(
    user_id: UUID,
    request: UpdateRolesRequest,
    current_user: User = Depends(require_role("ADMIN")),
    db: Session = Depends(get_db),
) -> UserResponse:
    """Update user roles (ADMIN only)"""
    service = AdminService(db)

    try:
        return service.assign_roles_to_user(user_id, request.roles)
    except ForbiddenException:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puedes quitarle el rol ADMIN al único administrador",
        )


@router.delete("/users/{user_id}/roles/{role}", status_code=status.HTTP_200_OK)
async def remove_user_role(
    user_id: UUID,
    role: str,
    current_user: User = Depends(require_role("ADMIN")),
    db: Session = Depends(get_db),
) -> UserResponse:
    """Remove a role from a user (ADMIN only)"""
    service = AdminService(db)

    try:
        return service.remove_role_from_user(user_id, role)
    except ForbiddenException:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puedes quitarle el rol ADMIN al único administrador",
        )


# ─── New endpoints (user management) ─────────────────────────────────────────


@router.get("/usuarios", response_model=AdminUserListResponse)
async def list_usuarios(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    rol: str | None = Query(None, description="Filtrar por rol (ADMIN, CLIENT, STOCK, PEDIDOS)"),
    search: str | None = Query(None, description="Buscar por email o nombre"),
    estado: str = Query("activo", description="Filtrar por estado: activo, inactivo, todos"),
    current_user: User = Depends(require_role("ADMIN")),
    db: Session = Depends(get_db),
) -> AdminUserListResponse:
    """Listar usuarios con paginación y filtros"""
    service = AdminService(db)
    return service.list_users(page, size, rol, search, estado)


@router.get("/usuarios/{user_id}", response_model=AdminUserResponse)
async def get_usuario(
    user_id: UUID,
    current_user: User = Depends(require_role("ADMIN")),
    db: Session = Depends(get_db),
) -> AdminUserResponse:
    """Obtener detalle de un usuario"""
    service = AdminService(db)
    try:
        return service.get_user_detail(user_id)
    except UserNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )


@router.put("/usuarios/{user_id}", response_model=AdminUserResponse)
async def update_usuario(
    user_id: UUID,
    request: AdminUserUpdateRequest,
    current_user: User = Depends(require_role("ADMIN")),
    db: Session = Depends(get_db),
) -> AdminUserResponse:
    """Actualizar datos y/o roles de un usuario"""
    service = AdminService(db)
    try:
        return service.update_user(user_id, request)
    except UserNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )
    except ForbiddenException as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=e.detail,
        )


@router.delete("/usuarios/{user_id}", response_model=dict)
async def deactivate_usuario(
    user_id: UUID,
    current_user: User = Depends(require_role("ADMIN")),
    db: Session = Depends(get_db),
) -> dict:
    """Desactivar un usuario (soft delete)"""
    service = AdminService(db)
    try:
        return service.deactivate_user(user_id)
    except UserNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )
    except ForbiddenException as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=e.detail,
        )


@router.patch("/usuarios/{user_id}/reactivar", response_model=AdminUserResponse)
async def reactivate_usuario(
    user_id: UUID,
    current_user: User = Depends(require_role("ADMIN")),
    db: Session = Depends(get_db),
) -> AdminUserResponse:
    """Reactivar un usuario desactivado"""
    service = AdminService(db)
    try:
        return service.reactivate_user(user_id)
    except UserNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )
