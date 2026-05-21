from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_role
from app.direcciones.schemas import DireccionCreate, DireccionResponse, DireccionUpdate
from app.direcciones.service import DireccionService
from app.models import User

router = APIRouter(
    prefix="/direcciones",
    tags=["Direcciones"],
)


@router.post("", response_model=DireccionResponse, status_code=status.HTTP_201_CREATED)
def create_address(
    data: DireccionCreate,
    current_user: User = Depends(require_role("CLIENT")),
    db: Session = Depends(get_db),
) -> DireccionResponse:
    service = DireccionService(db)
    return service.create(current_user, data)


@router.get("", response_model=list[DireccionResponse])
def list_addresses(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[DireccionResponse]:
    service = DireccionService(db)
    return service.list_addresses(current_user)


@router.get("/{address_id}", response_model=DireccionResponse)
def get_address(
    address_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DireccionResponse:
    service = DireccionService(db)
    return service.get_address(current_user, address_id)


@router.put("/{address_id}", response_model=DireccionResponse)
def update_address(
    address_id: UUID,
    data: DireccionUpdate,
    current_user: User = Depends(require_role("CLIENT")),
    db: Session = Depends(get_db),
) -> DireccionResponse:
    service = DireccionService(db)
    return service.update(current_user, address_id, data)


@router.patch("/{address_id}/principal", response_model=DireccionResponse)
def set_principal_address(
    address_id: UUID,
    current_user: User = Depends(require_role("CLIENT")),
    db: Session = Depends(get_db),
) -> DireccionResponse:
    service = DireccionService(db)
    return service.set_principal(current_user, address_id)


@router.delete("/{address_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_address(
    address_id: UUID,
    current_user: User = Depends(require_role("CLIENT")),
    db: Session = Depends(get_db),
) -> None:
    service = DireccionService(db)
    service.delete(current_user, address_id)
