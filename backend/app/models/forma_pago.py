from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, String

from app.models import Base


class FormaPago(Base):
    __tablename__ = "forma_pago"

    codigo = Column(String(20), primary_key=True)
    descripcion = Column(String(100), nullable=False)
    habilitado = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<FormaPago(codigo={self.codigo})>"
