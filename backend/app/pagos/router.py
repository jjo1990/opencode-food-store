from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_role
from app.models import User
from app.pagos.schemas import CrearPagoRequest, PagoResponse
from app.pagos.service import PagoService

router = APIRouter(prefix="/pagos", tags=["Pagos"])


@router.post("/crear", response_model=PagoResponse, status_code=status.HTTP_201_CREATED)
def crear_pago(
    data: CrearPagoRequest,
    current_user: User = Depends(require_role("CLIENT")),
    db: Session = Depends(get_db),
) -> PagoResponse:
    return PagoService(db).crear_pago(current_user, data)
