from uuid import UUID

from pydantic import BaseModel, Field


class CrearPagoRequest(BaseModel):
    pedido_id: UUID
    card_token: str = Field(..., min_length=1)


class PagoResponse(BaseModel):
    mp_payment_id: str | None = None
    status: str
    status_detail: str | None = None
