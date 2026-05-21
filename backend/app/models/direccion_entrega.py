"""
DireccionEntrega model for delivery addresses
"""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Index, String, Text, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models import Base


class DireccionEntrega(Base):
    """Delivery address model"""

    __tablename__ = "direccion_entrega"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    usuario_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False, index=True)
    alias = Column(String(100), nullable=True)
    calle = Column(String(255), nullable=False)
    numero = Column(String(20), nullable=False)
    piso = Column(String(10), nullable=True)
    departamento = Column(String(10), nullable=True)
    ciudad = Column(String(100), nullable=False)
    codigo_postal = Column(String(20), nullable=False)
    referencia = Column(Text, nullable=True)
    es_principal = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    soft_deleted_at = Column(DateTime, nullable=True, index=True)

    # Relationships
    usuario = relationship("User", back_populates="direcciones")

    __table_args__ = (
        Index(
            "ix_direccion_principal_unica",
            "usuario_id",
            "es_principal",
            unique=True,
            postgresql_where=text("es_principal = true"),
        ),
    )

    def __repr__(self):
        return f"<DireccionEntrega(id={self.id}, alias={self.alias}, calle={self.calle})>"
