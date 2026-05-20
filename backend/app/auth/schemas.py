"""
Request/Response schemas for authentication
"""

from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator


class RegisterRequest(BaseModel):
    """Registration request schema"""

    email: EmailStr
    password: str = Field(..., min_length=8, max_length=255)
    full_name: str = Field(..., max_length=255)

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password requirements"""
        if len(v) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres")
        return v


class LoginRequest(BaseModel):
    """Login request schema"""

    email: EmailStr
    password: str


class RefreshTokenRequest(BaseModel):
    """Refresh token request schema"""

    refresh_token: str


class TokenResponse(BaseModel):
    """Token response schema"""

    access_token: str
    refresh_token: str
    expires_in: int
    token_type: str = "Bearer"


class UserResponse(BaseModel):
    """User response schema"""

    id: UUID
    email: str
    full_name: str | None = None
    telefono: str | None = None
    roles: list[str] = []

    class Config:
        from_attributes = True


class UpdateRolesRequest(BaseModel):
    """Update user roles request schema"""

    roles: list[str]

    @field_validator("roles")
    @classmethod
    def validate_roles(cls, v: list[str]) -> list[str]:
        """Validate roles"""
        valid_roles = {"CLIENT", "STOCK", "PEDIDOS", "ADMIN"}
        for role in v:
            if role not in valid_roles:
                raise ValueError(
                    f"Rol inválido: {role}. Roles permitidos: {', '.join(valid_roles)}"
                )
        return v
