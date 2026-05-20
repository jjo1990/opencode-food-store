from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Session

from app.auth.repository import RefreshTokenRepository
from app.models import User


class UserProfileRepository:
    def __init__(self, db: Session):
        self.db = db
        self.token_repo = RefreshTokenRepository(db)

    def update_profile(self, user: User, data: dict) -> User:
        for key, value in data.items():
            setattr(user, key, value)
        self.db.commit()
        self.db.refresh(user)
        return user

    def soft_delete_user(self, user: User) -> User:
        user.soft_deleted_at = datetime.utcnow()
        self.db.commit()
        return user

    def invalidate_refresh_tokens(self, user_id: UUID) -> None:
        self.token_repo.revoke_all_user_tokens(user_id)
