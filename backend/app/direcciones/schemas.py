from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class DireccionCreate(BaseModel):
    alias: str | None = None
    calle: str
    numero: str
    piso: str | None = None
    departamento: str | None = None
    ciudad: str
    codigo_postal: str
    referencia: str | None = None
    es_principal: bool = False


class DireccionUpdate(BaseModel):
    alias: str | None = None
    calle: str | None = None
    numero: str | None = None
    piso: str | None = None
    departamento: str | None = None
    ciudad: str | None = None
    codigo_postal: str | None = None
    referencia: str | None = None
    es_principal: bool | None = None


class DireccionResponse(BaseModel):
    id: UUID
    usuario_id: UUID
    alias: str | None = None
    calle: str
    numero: str
    piso: str | None = None
    departamento: str | None = None
    ciudad: str
    codigo_postal: str
    referencia: str | None = None
    es_principal: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
