"""
Checkout routes — pre-purchase validation
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.checkout.schemas import ValidarRequest, ValidarResponse
from app.checkout.service import CheckoutService
from app.core.database import get_db

router = APIRouter(
    prefix="/checkout",
    tags=["Checkout"],
)


@router.post("/validar", response_model=ValidarResponse)
def validar_checkout(
    request: ValidarRequest,
    db: Session = Depends(get_db),
) -> ValidarResponse:
    """Validate checkout items before purchase"""
    service = CheckoutService(db)
    return service.validar(request)
