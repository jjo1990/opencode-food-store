"""
ProductoCategoria junction model — many-to-many between producto and categoria
"""

from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from app.models import Base


class ProductoCategoria(Base):
    """Junction table for producto ↔ categoria many-to-many"""

    __tablename__ = "producto_categoria"

    producto_id = Column(UUID(as_uuid=True), ForeignKey("producto.id"), primary_key=True)
    categoria_id = Column(UUID(as_uuid=True), ForeignKey("categoria.id"), primary_key=True)

    def __repr__(self):
        return (
            f"<ProductoCategoria(producto_id={self.producto_id}, categoria_id={self.categoria_id})>"
        )
