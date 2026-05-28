"""
Admin schemas for user management
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, field_validator


class AdminUserResponse(BaseModel):
    """Response schema for a user in admin context"""

    id: UUID
    email: str
    full_name: str | None = None
    telefono: str | None = None
    roles: list[str]
    activo: bool
    created_at: datetime
    soft_deleted_at: datetime | None = None

    class Config:
        from_attributes = True


class AdminUserListResponse(BaseModel):
    """Paginated list response"""

    items: list[AdminUserResponse]
    total: int
    page: int
    size: int
    pages: int


class AdminUserUpdateRequest(BaseModel):
    """Update user request - all fields optional"""

    full_name: str | None = None
    email: EmailStr | None = None
    telefono: str | None = None
    roles: list[str] | None = None

    @field_validator("email")
    @classmethod
    def validate_email(cls, v):
        if v is not None:
            pass
        return v

    @field_validator("roles")
    @classmethod
    def validate_roles(cls, v):
        if v is not None:
            valid_roles = {"CLIENT", "STOCK", "PEDIDOS", "ADMIN"}
            for role in v:
                if role not in valid_roles:
                    raise ValueError(f"Rol inválido: {role}")
        return v
