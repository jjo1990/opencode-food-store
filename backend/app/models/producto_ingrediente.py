"""
ProductoIngrediente junction model — many-to-many between producto and ingrediente
"""

from sqlalchemy import Boolean, Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from app.models import Base


class ProductoIngrediente(Base):
    """Junction table for producto ↔ ingrediente many-to-many"""

    __tablename__ = "producto_ingrediente"

    producto_id = Column(UUID(as_uuid=True), ForeignKey("producto.id"), primary_key=True)
    ingrediente_id = Column(UUID(as_uuid=True), ForeignKey("ingrediente.id"), primary_key=True)
    es_removible = Column(Boolean, nullable=False, default=True)

    def __repr__(self):
        return f"<ProductoIngrediente(producto_id={self.producto_id}, ingrediente_id={self.ingrediente_id})>"
