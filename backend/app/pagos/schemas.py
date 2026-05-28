from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class CrearPagoRequest(BaseModel):
    pedido_id: UUID
    card_token: str = Field(..., min_length=1)


class PagoResponse(BaseModel):
    mp_payment_id: str | None = None
    status: str
    status_detail: str | None = None


class WebhookNotification(BaseModel):
    type: str | None = None
    action: str | None = None
    data: dict | None = None


class PagoHistoryItem(BaseModel):
    mp_payment_id: str | None = None
    mp_status: str
    status_detail: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True


class PagoHistoryResponse(BaseModel):
    pagos: list[PagoHistoryItem]


class ReintentarPagoRequest(BaseModel):
    pedido_id: UUID
    card_token: str = Field(..., min_length=1)
