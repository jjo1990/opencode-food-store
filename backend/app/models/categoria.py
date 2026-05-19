"""
Categoria model with self-referential hierarchy
"""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models import Base


class Categoria(Base):
    """Categoria model for hierarchical product categories"""

    __tablename__ = "categoria"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    nombre = Column(String(100), unique=True, nullable=False, index=True)
    parent_id = Column(UUID(as_uuid=True), ForeignKey("categoria.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    soft_deleted_at = Column(DateTime, nullable=True, index=True)

    # Relationships
    children = relationship(
        "Categoria", backref="parent", remote_side=[id], cascade="all, delete-orphan"
    )

    __table_args__ = (Index("idx_categoria_parent", "parent_id"),)

    def __repr__(self):
        return f"<Categoria(id={self.id}, nombre={self.nombre})>"
