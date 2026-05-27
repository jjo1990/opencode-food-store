from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models import Base


class Pago(Base):
    __tablename__ = "pago"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    pedido_id = Column(UUID(as_uuid=True), ForeignKey("pedido.id"), nullable=False, index=True)
    mp_payment_id = Column(String(50), nullable=True, unique=True, index=True)
    mp_status = Column(String(30), nullable=False)
    external_reference = Column(String(100), nullable=False, unique=True, index=True)
    idempotency_key = Column(String(100), nullable=False, unique=True, index=True)
    status_detail = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    pedido = relationship("Pedido", back_populates="pagos")

    def __repr__(self):
        return f"<Pago(id={self.id}, mp_status={self.mp_status})>"
