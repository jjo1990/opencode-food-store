"""
Producto model
"""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Boolean, Column, DateTime, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models import Base


class Producto(Base):
    """Producto model for food products catalog"""

    __tablename__ = "producto"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    nombre = Column(String(200), nullable=False)
    descripcion = Column(Text, nullable=True)
    precio_base = Column(Numeric(10, 2), nullable=False)
    stock_cantidad = Column(Integer, nullable=False, default=0)
    disponible = Column(Boolean, nullable=False, default=True)
    imagen_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    soft_deleted_at = Column(DateTime, nullable=True, index=True)

    # Relationships via junction tables
    categorias = relationship("Categoria", secondary="producto_categoria", backref="productos")
    ingredientes = relationship(
        "Ingrediente", secondary="producto_ingrediente", backref="productos"
    )

    def __repr__(self):
        return f"<Producto(id={self.id}, nombre={self.nombre})>"
