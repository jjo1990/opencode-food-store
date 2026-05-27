from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class ItemPedidoRequest(BaseModel):
    producto_id: UUID
    cantidad: int = Field(..., ge=1)
    personalizacion: list[UUID] = []


class CrearPedidoRequest(BaseModel):
    items: list[ItemPedidoRequest] = Field(..., min_length=1)
    direccion_id: UUID
    forma_pago_codigo: str
    notas: str | None = None


class DetallePedidoRead(BaseModel):
    id: UUID
    producto_id: UUID
    nombre_snapshot: str
    precio_snapshot: Decimal
    cantidad: int
    subtotal: Decimal
    personalizacion: list[UUID] | None = None

    class Config:
        from_attributes = True


class PedidoRead(BaseModel):
    id: UUID
    estado_codigo: str
    subtotal: Decimal
    costo_envio: Decimal
    total: Decimal
    created_at: datetime

    class Config:
        from_attributes = True


class HistorialRead(BaseModel):
    estado_desde: str | None = None
    estado_nuevo: str
    actor_id: UUID | None = None
    motivo: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True


class PedidoListRead(BaseModel):
    id: UUID
    estado_codigo: str
    subtotal: Decimal
    costo_envio: Decimal
    total: Decimal
    created_at: datetime

    class Config:
        from_attributes = True


class PedidoDetail(PedidoRead):
    items: list[DetallePedidoRead] = []
    historial: list[HistorialRead] = []
