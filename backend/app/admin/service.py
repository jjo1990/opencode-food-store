"""
Admin service layer
"""

from uuid import UUID

from sqlalchemy.orm import Session

from app.admin.repository import AdminUserRepository
from app.admin.schemas import AdminUserListResponse, AdminUserResponse, AdminUserUpdateRequest
from app.auth.repository import RefreshTokenRepository, UserRepository
from app.auth.schemas import UserResponse
from app.core.exceptions import (
    ForbiddenException,
    UserAlreadyExistsException,
    UserNotFoundException,
)
from app.models import User


class AdminService:
    """Service for admin operations"""

    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)

    def assign_roles_to_user(self, user_id: UUID, roles: list[str]) -> UserResponse:
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
            roles=[role.role for role in user.roles],
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
            roles=[role.role for role in user.roles],
        )

    def list_users(
        self,
        page: int = 1,
        size: int = 20,
        rol: str | None = None,
        search: str | None = None,
        estado: str = "activo",
    ) -> AdminUserListResponse:
        """List users with pagination and filters"""
        if estado not in ("activo", "inactivo", "todos"):
            estado = "activo"

        repo = AdminUserRepository(self.db)
        users, total = repo.list_users(page, size, rol, search, estado)
        items = [self._user_to_response(u) for u in users]
        pages = max(1, (total + size - 1) // size)
        return AdminUserListResponse(items=items, total=total, page=page, size=size, pages=pages)

    def get_user_detail(self, user_id: UUID) -> AdminUserResponse:
        """Get user detail by ID (including soft-deleted)"""
        repo = AdminUserRepository(self.db)
        user = repo.get_user_by_id_including_deleted(user_id)
        if not user:
            raise UserNotFoundException()
        return self._user_to_response(user)

    def update_user(self, user_id: UUID, data: AdminUserUpdateRequest) -> AdminUserResponse:
        """Update user fields and/or roles"""
        admin_repo = AdminUserRepository(self.db)
        user = admin_repo.get_user_by_id_including_deleted(user_id)
        if not user:
            raise UserNotFoundException()

        roles_changed = False

        # Update email with uniqueness check
        if data.email is not None and data.email != user.email:
            existing = self.user_repo.get_user_by_email(data.email)
            if existing:
                raise UserAlreadyExistsException()
            user.email = data.email

        # Update scalar fields
        if data.full_name is not None:
            user.full_name = data.full_name
        if data.telefono is not None:
            user.telefono = data.telefono

        # Update roles if provided
        if data.roles is not None:
            current_roles = {role.role for role in user.roles}
            new_roles = set(data.roles)

            if current_roles != new_roles:
                # Check last ADMIN protection
                if "ADMIN" in current_roles and "ADMIN" not in new_roles:
                    admin_count = self.user_repo.count_admin_users()
                    if admin_count == 1:
                        raise ForbiddenException(
                            "No puedes quitarle el rol ADMIN al único administrador del sistema"
                        )

                # Replace roles
                for role in user.roles:
                    self.user_repo.remove_role(user_id, role.role)
                for role in data.roles:
                    self.user_repo.assign_role(user_id, role)

                roles_changed = True

        self.db.commit()

        if roles_changed:
            refresh_token_repo = RefreshTokenRepository(self.db)
            refresh_token_repo.revoke_all_user_tokens(user_id)

        self.db.refresh(user)
        return self._user_to_response(user)

    def deactivate_user(self, user_id: UUID) -> dict:
        """Soft delete user. Protect last ADMIN."""
        admin_repo = AdminUserRepository(self.db)
        user = admin_repo.get_user_by_id_including_deleted(user_id)
        if not user:
            raise UserNotFoundException()

        if user.soft_deleted_at is not None:
            raise UserNotFoundException()

        # Check last ADMIN protection
        has_admin = any(role.role == "ADMIN" for role in user.roles)
        if has_admin:
            admin_count = self.user_repo.count_admin_users()
            if admin_count == 1:
                raise ForbiddenException("No puedes desactivar al único administrador del sistema")

        admin_repo.soft_delete_user(user_id)

        # Revoke all tokens
        refresh_token_repo = RefreshTokenRepository(self.db)
        refresh_token_repo.revoke_all_user_tokens(user_id)

        return {"message": "Usuario desactivado correctamente"}

    def reactivate_user(self, user_id: UUID) -> AdminUserResponse:
        """Restore soft-deleted user."""
        admin_repo = AdminUserRepository(self.db)
        user = admin_repo.get_user_by_id_including_deleted(user_id)
        if not user:
            raise UserNotFoundException()

        if user.soft_deleted_at is None:
            raise UserNotFoundException()

        admin_repo.reactivate_user(user_id)
        self.db.refresh(user)
        return self._user_to_response(user)

    def _user_to_response(self, user: User) -> AdminUserResponse:
        """Convert User model to AdminUserResponse"""
        return AdminUserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            telefono=user.telefono,
            roles=[role.role for role in user.roles],
            activo=user.soft_deleted_at is None,
            created_at=user.created_at,
            soft_deleted_at=user.soft_deleted_at,
        )
