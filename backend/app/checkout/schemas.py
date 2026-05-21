"""
Request/Response schemas for checkout validation
"""

from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class ItemValidarRequest(BaseModel):
    """Single item in checkout validation request"""

    producto_id: UUID
    cantidad: int = Field(..., ge=1)
    precio_snapshot: Decimal = Field(..., ge=0)
    personalizacion: list[UUID] = []


class ValidarRequest(BaseModel):
    """Checkout validation request"""

    items: list[ItemValidarRequest]


class ItemValidado(BaseModel):
    """Single item validation result"""

    producto_id: UUID
    nombre: str
    valido: bool
    errores: list[str] = []
    advertencias: list[str] = []


class ValidarResponse(BaseModel):
    """Checkout validation response"""

    valido: bool
    errores: list[str] = []
    advertencias: list[str] = []
    detalles: list[ItemValidado] = []
