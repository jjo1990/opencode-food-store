from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models import Base


class HistorialEstadoPedido(Base):
    __tablename__ = "historial_estado_pedido"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    pedido_id = Column(UUID(as_uuid=True), ForeignKey("pedido.id"), nullable=False, index=True)
    estado_desde = Column(String(20), nullable=True)
    estado_nuevo = Column(String(20), nullable=False)
    actor_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=True)
    motivo = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    pedido = relationship("Pedido", back_populates="historial")

    def __repr__(self):
        return f"<HistorialEstadoPedido(id={self.id}, {self.estado_desde}->{self.estado_nuevo})>"
