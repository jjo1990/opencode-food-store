"""
Repository layer for authentication
"""
from uuid import UUID
from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models import User, UserRole, RefreshToken


class UserRepository:
    """Repository for user operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_user(self, email: str, hashed_password: str, full_name: str, telefono: str | None = None) -> User:
        """Create a new user"""
        user = User(
            email=email,
            hashed_password=hashed_password,
            full_name=full_name,
            telefono=telefono
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.db.query(User).filter(
            User.email == email,
            User.soft_deleted_at.is_(None)
        ).first()
    
    def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by ID"""
        return self.db.query(User).filter(
            User.id == user_id,
            User.soft_deleted_at.is_(None)
        ).first()
    
    def assign_role(self, user_id: UUID, role: str) -> UserRole:
        """Assign a role to a user"""
        # Check if role already exists
        existing = self.db.query(UserRole).filter(
            UserRole.user_id == user_id,
            UserRole.role == role
        ).first()
        
        if existing:
            return existing
        
        user_role = UserRole(user_id=user_id, role=role)
        self.db.add(user_role)
        self.db.commit()
        self.db.refresh(user_role)
        return user_role
    
    def remove_role(self, user_id: UUID, role: str) -> bool:
        """Remove a role from a user"""
        user_role = self.db.query(UserRole).filter(
            UserRole.user_id == user_id,
            UserRole.role == role
        ).first()
        
        if not user_role:
            return False
        
        self.db.delete(user_role)
        self.db.commit()
        return True
    
    def get_user_with_roles(self, user_id: UUID) -> Optional[User]:
        """Get user with roles loaded"""
        user = self.get_user_by_id(user_id)
        if user:
            # Force load roles
            _ = user.roles
        return user
    
    def count_admin_users(self) -> int:
        """Count users with ADMIN role"""
        return self.db.query(User).join(UserRole).filter(
            UserRole.role == "ADMIN",
            User.soft_deleted_at.is_(None)
        ).distinct().count()


class RefreshTokenRepository:
    """Repository for refresh token operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_refresh_token(
        self,
        user_id: UUID,
        token_hash: str,
        family_id: UUID,
        expires_at: datetime
    ) -> RefreshToken:
        """Create a new refresh token"""
        token = RefreshToken(
            user_id=user_id,
            token_hash=token_hash,
            family_id=family_id,
            expires_at=expires_at
        )
        self.db.add(token)
        self.db.commit()
        self.db.refresh(token)
        return token
    
    def get_refresh_token_by_hash(self, token_hash: str) -> Optional[RefreshToken]:
        """Get refresh token by hash"""
        return self.db.query(RefreshToken).filter(
            RefreshToken.token_hash == token_hash
        ).first()
    
    def revoke_refresh_token(self, token_id: UUID) -> bool:
        """Revoke a refresh token"""
        token = self.db.query(RefreshToken).filter(
            RefreshToken.id == token_id
        ).first()
        
        if not token:
            return False
        
        token.revoked_at = datetime.utcnow()
        self.db.commit()
        return True
    
    def revoke_by_hash(self, token_hash: str) -> bool:
        """Revoke a refresh token by hash"""
        token = self.get_refresh_token_by_hash(token_hash)
        if not token:
            return False
        
        token.revoked_at = datetime.utcnow()
        self.db.commit()
        return True
    
    def get_active_refresh_tokens_by_family(self, family_id: UUID) -> List[RefreshToken]:
        """Get all active refresh tokens for a family"""
        return self.db.query(RefreshToken).filter(
            RefreshToken.family_id == family_id,
            RefreshToken.revoked_at.is_(None)
        ).all()
    
    def revoke_all_by_family(self, family_id: UUID) -> int:
        """Revoke all refresh tokens for a family (replay detection)"""
        tokens = self.db.query(RefreshToken).filter(
            RefreshToken.family_id == family_id
        ).all()
        
        count = 0
        for token in tokens:
            token.revoked_at = datetime.utcnow()
            count += 1
        
        self.db.commit()
        return count
    
    def revoke_all_user_tokens(self, user_id: UUID) -> int:
        """Revoke all active tokens for a user"""
        tokens = self.db.query(RefreshToken).filter(
            RefreshToken.user_id == user_id,
            RefreshToken.revoked_at.is_(None)
        ).all()
        
        count = 0
        for token in tokens:
            token.revoked_at = datetime.utcnow()
            count += 1
        
        self.db.commit()
        return count
