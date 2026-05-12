"""
Admin routes for role-based access control
"""
from uuid import UUID
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from app.admin.service import AdminService
from app.auth.schemas import UpdateRolesRequest, UserResponse
from app.core.database import get_db
from app.core.dependencies import get_current_user, require_role
from app.core.exceptions import ForbiddenException
from app.models import User


router = APIRouter(
    prefix="/admin",
    tags=["admin"]
)


@router.put("/users/{user_id}/roles", response_model=UserResponse)
async def update_user_roles(
    user_id: UUID,
    request: UpdateRolesRequest,
    current_user: User = Depends(require_role("ADMIN")),
    db: Session = Depends(get_db)
) -> UserResponse:
    """Update user roles (ADMIN only)"""
    service = AdminService(db)
    
    try:
        return service.assign_roles_to_user(user_id, request.roles)
    except ForbiddenException:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puedes quitarle el rol ADMIN al único administrador"
        )


@router.delete("/users/{user_id}/roles/{role}", status_code=status.HTTP_200_OK)
async def remove_user_role(
    user_id: UUID,
    role: str,
    current_user: User = Depends(require_role("ADMIN")),
    db: Session = Depends(get_db)
) -> UserResponse:
    """Remove a role from a user (ADMIN only)"""
    service = AdminService(db)
    
    try:
        return service.remove_role_from_user(user_id, role)
    except ForbiddenException:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puedes quitarle el rol ADMIN al único administrador"
        )
