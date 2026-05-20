from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_role
from app.models import User
from app.usuarios.schemas import PasswordChangeRequest, ProfileUpdateRequest, UserProfileResponse
from app.usuarios.service import UserProfileService

router = APIRouter(
    prefix="/usuarios",
    tags=["Usuarios"],
)


@router.get("/me", response_model=UserProfileResponse)
def get_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserProfileResponse:
    service = UserProfileService(db)
    return service.get_profile(current_user)


@router.put("/me", response_model=UserProfileResponse)
def update_profile(
    data: ProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserProfileResponse:
    service = UserProfileService(db)
    return service.update_profile(current_user, data)


@router.put("/me/contrasena", status_code=status.HTTP_200_OK)
def change_password(
    data: PasswordChangeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    service = UserProfileService(db)
    service.change_password(current_user, data.current_password, data.new_password)
    return {"message": "Contraseña actualizada correctamente"}


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_account(
    current_user: User = Depends(require_role("CLIENT")),
    db: Session = Depends(get_db),
) -> None:
    service = UserProfileService(db)
    service.delete_account(current_user)
