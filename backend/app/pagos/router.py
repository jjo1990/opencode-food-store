from uuid import UUID

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_role
from app.models import User
from app.pagos.schemas import (
    CrearPagoRequest,
    PagoHistoryResponse,
    PagoResponse,
    ReintentarPagoRequest,
    WebhookNotification,
)
from app.pagos.service import PagoService

router = APIRouter(prefix="/pagos", tags=["Pagos"])


@router.post("/crear", response_model=PagoResponse, status_code=status.HTTP_201_CREATED)
def crear_pago(
    data: CrearPagoRequest,
    current_user: User = Depends(require_role("CLIENT")),
    db: Session = Depends(get_db),
) -> PagoResponse:
    return PagoService(db).crear_pago(current_user, data)


@router.get("/{pedido_id}", response_model=PagoHistoryResponse)
def consultar_pagos(
    pedido_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PagoHistoryResponse:
    """Obtiene el historial de pagos de un pedido"""
    return PagoService(db).consultar_pagos(pedido_id, current_user)


@router.post("/reintentar", response_model=PagoResponse, status_code=status.HTTP_201_CREATED)
def reintentar_pago(
    data: ReintentarPagoRequest,
    current_user: User = Depends(require_role("CLIENT")),
    db: Session = Depends(get_db),
) -> PagoResponse:
    """Reintenta un pago rechazado"""
    return PagoService(db).reintentar_pago(current_user, data)


@router.post("/webhook", status_code=status.HTTP_200_OK)
async def webhook_pago(
    request: Request,
    db: Session = Depends(get_db),
):
    raw_body = await request.body()
    body_data = await request.json()
    data = WebhookNotification(**body_data)
    x_signature = request.headers.get("x-signature", "")
    x_request_id = request.headers.get("x-request-id", "")
    return PagoService(db).procesar_webhook(data, x_signature, x_request_id, raw_body)
