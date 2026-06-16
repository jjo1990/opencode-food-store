"""
RefreshToken model
"""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models import Base


class RefreshToken(Base):
    """RefreshToken model for token refresh and rotation"""

    __tablename__ = "refresh_token"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False, index=True)
    token_hash = Column(String(255), nullable=False)
    family_id = Column(UUID(as_uuid=True), nullable=True, index=True)  # For replay attack detection
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    revoked_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="refresh_tokens")

    # Constraints and indexes
    __table_args__ = (
        Index("idx_user_revoked", "user_id", "revoked_at"),
        Index("idx_family_id", "family_id"),
        Index("idx_expires_at", "expires_at"),
    )

    def __repr__(self):
        return f"<RefreshToken(id={self.id}, user_id={self.user_id}, revoked={self.revoked_at is not None})>"
