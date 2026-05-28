"""
Repository layer for admin user management
"""

from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Session

from app.models import User, UserRole


class AdminUserRepository:
    """Repository for admin user operations"""

    def __init__(self, db: Session):
        self.db = db

    def list_users(
        self,
        page: int = 1,
        size: int = 20,
        rol: str | None = None,
        search: str | None = None,
        estado: str = "activo",
    ) -> tuple[list[User], int]:
        """List users with pagination and filters"""
        query = self.db.query(User)

        if estado == "activo":
            query = query.filter(User.soft_deleted_at.is_(None))
        elif estado == "inactivo":
            query = query.filter(User.soft_deleted_at.isnot(None))

        if rol:
            query = query.join(UserRole).filter(UserRole.role == rol)

        if search:
            pattern = f"%{search}%"
            query = query.filter(User.email.ilike(pattern) | User.full_name.ilike(pattern))

        if rol:
            query = query.distinct()

        total = query.count()

        users = query.order_by(User.created_at.desc()).offset((page - 1) * size).limit(size).all()

        return users, total

    def get_user_by_id_including_deleted(self, user_id: UUID) -> User | None:
        """Get user by ID including soft-deleted"""
        return self.db.query(User).filter(User.id == user_id).first()

    def soft_delete_user(self, user_id: UUID) -> bool:
        """Mark user as soft-deleted. Returns True if affected."""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user or user.soft_deleted_at is not None:
            return False
        user.soft_deleted_at = datetime.utcnow()
        self.db.commit()
        return True

    def reactivate_user(self, user_id: UUID) -> bool:
        """Restore soft-deleted user. Returns True if affected."""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user or user.soft_deleted_at is None:
            return False
        user.soft_deleted_at = None
        self.db.commit()
        return True
