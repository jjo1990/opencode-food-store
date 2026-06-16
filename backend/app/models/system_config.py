"""
SystemConfig model — key-value configuration store
"""

from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models import Base


class SystemConfig(Base):
    __tablename__ = "system_config"

    clave = Column(String(100), primary_key=True)
    valor = Column(String(500), nullable=False)
    updated_by = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    admin_user = relationship("User", foreign_keys=[updated_by])

    def __repr__(self):
        return f"<SystemConfig(clave={self.clave})>"
