from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ProfileUpdateRequest(BaseModel):
    full_name: str | None = Field(None, min_length=2, max_length=255)
    telefono: str | None = Field(None, max_length=20)


class PasswordChangeRequest(BaseModel):
    current_password: str = Field(..., min_length=8, max_length=255)
    new_password: str = Field(..., min_length=8, max_length=255)


class UserProfileResponse(BaseModel):
    id: UUID
    email: str
    full_name: str | None = None
    telefono: str | None = None
    roles: list[str] = []
    created_at: datetime

    class Config:
        from_attributes = True
