from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String

from app.models import Base


class EstadoPedido(Base):
    __tablename__ = "estado_pedido"

    codigo = Column(String(20), primary_key=True)
    descripcion = Column(String(100), nullable=False)
    orden = Column(Integer, nullable=False)
    es_terminal = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<EstadoPedido(codigo={self.codigo})>"
