"""
UserRole model
"""
from uuid import uuid4
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models import Base


class UserRole(Base):
    """UserRole model for RBAC"""
    __tablename__ = "user_role"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False, index=True)
    role = Column(String(20), nullable=False, index=True)  # CLIENT, STOCK, PEDIDOS, ADMIN
    assigned_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="roles")

    # Constraints and indexes
    __table_args__ = (
        UniqueConstraint("user_id", "role", name="uq_user_role"),
        Index("idx_role", "role"),
    )

    def __repr__(self):
        return f"<UserRole(user_id={self.user_id}, role={self.role})>"
