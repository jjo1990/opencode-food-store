"""
Admin service layer
"""
from uuid import UUID
from typing import List
from sqlalchemy.orm import Session

from app.auth.repository import UserRepository
from app.auth.schemas import UserResponse
from app.core.exceptions import ForbiddenException, UserNotFoundException


class AdminService:
    """Service for admin operations"""
    
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
    
    def assign_roles_to_user(self, user_id: UUID, roles: List[str]) -> UserResponse:
        """Assign roles to a user"""
        user = self.user_repo.get_user_by_id(user_id)
        if not user:
            raise UserNotFoundException()
        
        # Check if trying to remove ADMIN from last ADMIN
        admin_count = self.user_repo.count_admin_users()
        if admin_count == 1 and "ADMIN" not in roles:
            current_admin = self.user_repo.get_user_with_roles(user_id)
            has_admin = any(role.role == "ADMIN" for role in current_admin.roles)
            if has_admin:
                raise ForbiddenException(
                    "No puedes quitarle el rol ADMIN al único administrador del sistema"
                )
        
        # Remove existing roles and assign new ones
        for role in user.roles:
            self.user_repo.remove_role(user_id, role.role)
        
        for role in roles:
            self.user_repo.assign_role(user_id, role)
        
        # Refresh user to get updated roles
        self.db.refresh(user)
        
        return UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            roles=[role.role for role in user.roles]
        )
    
    def remove_role_from_user(self, user_id: UUID, role: str) -> UserResponse:
        """Remove a specific role from a user"""
        user = self.user_repo.get_user_by_id(user_id)
        if not user:
            raise UserNotFoundException()
        
        # Check if trying to remove ADMIN from last ADMIN
        if role == "ADMIN":
            admin_count = self.user_repo.count_admin_users()
            if admin_count == 1:
                current_admin = self.user_repo.get_user_with_roles(user_id)
                has_admin = any(r.role == "ADMIN" for r in current_admin.roles)
                if has_admin:
                    raise ForbiddenException(
                        "No puedes quitarle el rol ADMIN al único administrador del sistema"
                    )
        
        self.user_repo.remove_role(user_id, role)
        
        # Refresh user to get updated roles
        self.db.refresh(user)
        
        return UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            roles=[role.role for role in user.roles]
        )
