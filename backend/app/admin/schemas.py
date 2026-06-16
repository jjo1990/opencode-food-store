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


# ─── Order Management Schemas ─────────────────────────────────────────


class AdminOrderListItem(BaseModel):
    """Order item for admin list response"""

    id: UUID
    cliente_nombre: str | None = None
    usuario_id: UUID
    estado_codigo: str
    total: float
    created_at: datetime
    direccion_calle: str | None = None

    class Config:
        from_attributes = True


class AdminOrderListResponse(BaseModel):
    """Paginated order list response for admin"""

    items: list[AdminOrderListItem]
    total: int
    page: int
    size: int
    pages: int


class AdminChangeStateRequest(BaseModel):
    """Request to change order state in admin panel"""

    nuevo_estado: str
    motivo: str | None = None

    @field_validator("nuevo_estado")
    @classmethod
    def validate_nuevo_estado(cls, v):
        if not v or len(v) < 1 or len(v) > 20:
            raise ValueError("Estado debe tener entre 1 y 20 caracteres")
        return v

    @field_validator("motivo")
    @classmethod
    def validate_motivo(cls, v):
        if v is not None and len(v) > 500:
            raise ValueError("Motivo no puede exceder 500 caracteres")
        return v


# ─── Catalog Management Schemas ─────────────────────────────────────────


class AdminProductoListItem(BaseModel):
    """Producto item for admin list response"""

    id: UUID
    nombre: str
    precio_base: float
    stock_cantidad: int
    disponible: bool
    eliminado: bool
    soft_deleted_at: datetime | None = None
    created_at: datetime
    categorias: list[str] = []

    model_config = {"from_attributes": True}


class AdminProductoListResponse(BaseModel):
    """Paginated producto list response for admin"""

    items: list[AdminProductoListItem]
    total: int
    page: int
    size: int
    pages: int


class AdminCategoriaListItem(BaseModel):
    """Categoria item for admin list response"""

    id: UUID
    nombre: str
    parent_id: UUID | None = None
    eliminado: bool
    soft_deleted_at: datetime | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class AdminCategoriaListResponse(BaseModel):
    """Categoria list response for admin (no pagination)"""

    items: list[AdminCategoriaListItem]
    total: int


class AdminIngredienteListItem(BaseModel):
    """Ingrediente item for admin list response"""

    id: UUID
    nombre: str
    es_alergeno: bool
    eliminado: bool
    soft_deleted_at: datetime | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class AdminIngredienteListResponse(BaseModel):
    """Paginated ingrediente list response for admin"""

    items: list[AdminIngredienteListItem]
    total: int
    page: int
    size: int
    pages: int
