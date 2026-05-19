"""
Ingrediente model for allergens and ingredients catalog
"""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Boolean, Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID

from app.models import Base


class Ingrediente(Base):
    """Ingrediente model for ingredients and allergens"""

    __tablename__ = "ingrediente"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    nombre = Column(String(100), unique=True, nullable=False, index=True)
    es_alergeno = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    soft_deleted_at = Column(DateTime, nullable=True, index=True)

    def __repr__(self):
        return f"<Ingrediente(id={self.id}, nombre={self.nombre})>"
