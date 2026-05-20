from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.models import User
from app.usuarios.repository import UserProfileRepository
from app.usuarios.schemas import ProfileUpdateRequest, UserProfileResponse


class UserProfileService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = UserProfileRepository(db)

    def get_profile(self, user: User) -> UserProfileResponse:
        return UserProfileResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            telefono=user.telefono,
            roles=[role.role for role in user.roles],
            created_at=user.created_at,
        )

    def update_profile(self, user: User, data: ProfileUpdateRequest) -> UserProfileResponse:
        update_data = data.model_dump(exclude_none=True)
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No hay datos para actualizar",
            )

        updated_user = self.repo.update_profile(user, update_data)
        return UserProfileResponse(
            id=updated_user.id,
            email=updated_user.email,
            full_name=updated_user.full_name,
            telefono=updated_user.telefono,
            roles=[role.role for role in updated_user.roles],
            created_at=updated_user.created_at,
        )

    def change_password(self, user: User, current_password: str, new_password: str) -> None:
        if not verify_password(current_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Contraseña actual incorrecta",
            )

        user.hashed_password = hash_password(new_password)
        self.db.commit()
        self.repo.invalidate_refresh_tokens(user.id)

    def delete_account(self, user: User) -> None:
        self.repo.soft_delete_user(user)
        self.repo.invalidate_refresh_tokens(user.id)
