from datetime import datetime
from uuid import uuid4

from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models import Base


class DetallePedido(Base):
    __tablename__ = "detalle_pedido"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    pedido_id = Column(UUID(as_uuid=True), ForeignKey("pedido.id"), nullable=False, index=True)
    producto_id = Column(UUID(as_uuid=True), ForeignKey("producto.id"), nullable=False)
    cantidad = Column(Integer, nullable=False)
    precio_snapshot = Column(Numeric(10, 2), nullable=False)
    nombre_snapshot = Column(String(200), nullable=False)
    subtotal = Column(Numeric(10, 2), nullable=False)
    personalizacion = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    pedido = relationship("Pedido", back_populates="detalles")

    def __repr__(self):
        return f"<DetallePedido(id={self.id}, producto={self.nombre_snapshot})>"
