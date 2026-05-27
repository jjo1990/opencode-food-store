from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models import Base


class Pedido(Base):
    __tablename__ = "pedido"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False, index=True)
    estado_codigo = Column(String(20), ForeignKey("estado_pedido.codigo"), nullable=False)
    direccion_id = Column(
        UUID(as_uuid=True), ForeignKey("direccion_entrega.id", ondelete="SET NULL"), nullable=True
    )
    forma_pago_codigo = Column(String(20), ForeignKey("forma_pago.codigo"), nullable=False)
    direccion_snapshot = Column(Text, nullable=True)
    subtotal = Column(Numeric(10, 2), nullable=False, default=0)
    costo_envio = Column(Numeric(10, 2), nullable=False, default=50.00)
    total = Column(Numeric(10, 2), nullable=False, default=0)
    notas = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    soft_deleted_at = Column(DateTime, nullable=True, index=True)

    usuario = relationship("User", back_populates="pedidos")
    detalles = relationship("DetallePedido", back_populates="pedido", cascade="all, delete-orphan")
    historial = relationship(
        "HistorialEstadoPedido", back_populates="pedido", cascade="all, delete-orphan"
    )
    pagos = relationship("Pago", back_populates="pedido", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Pedido(id={self.id}, estado={self.estado_codigo})>"
