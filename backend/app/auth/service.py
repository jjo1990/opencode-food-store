"""
Authentication service layer
"""
from uuid import UUID, uuid4
from datetime import datetime, timedelta, timezone
from typing import Optional, List
from sqlalchemy.orm import Session

from app.auth.repository import UserRepository, RefreshTokenRepository
from app.auth.schemas import TokenResponse, UserResponse
from app.core.security import (
    hash_password,
    verify_password,
    hash_refresh_token,
    create_access_token,
    create_refresh_token,
)
from app.core.exceptions import (
    InvalidCredentialsException,
    UserAlreadyExistsException,
    InvalidTokenException,
    UserNotFoundException,
)


class AuthService:
    """Service for authentication operations"""
    
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.token_repo = RefreshTokenRepository(db)
    
    def register(self, email: str, password: str, full_name: str) -> UserResponse:
        """Register a new user"""
        # Check if user already exists
        existing_user = self.user_repo.get_user_by_email(email)
        if existing_user:
            raise UserAlreadyExistsException()
        
        # Hash password
        hashed_password = hash_password(password)
        
        # Create user
        user = self.user_repo.create_user(
            email=email,
            hashed_password=hashed_password,
            full_name=full_name
        )
        
        # Assign CLIENT role by default
        self.user_repo.assign_role(user.id, "CLIENT")
        
        # Refresh to load roles
        self.db.refresh(user)
        
        return UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            roles=[role.role for role in user.roles]
        )
    
    def login(self, email: str, password: str) -> TokenResponse:
        """Authenticate user and return tokens"""
        # Find user
        user = self.user_repo.get_user_by_email(email)
        if not user:
            raise InvalidCredentialsException()
        
        # Verify password
        if not verify_password(password, user.hashed_password):
            raise InvalidCredentialsException()
        
        # Generate tokens
        user_roles = [role.role for role in user.roles]
        access_token = create_access_token(user.id, user_roles)
        
        # Create refresh token
        family_id = uuid4()
        refresh_token, token_hash = create_refresh_token(user.id, family_id)
        
        # Store refresh token in DB
        from app.core.config import REFRESH_TOKEN_EXPIRE_TIMEDELTA
        expires_at = datetime.now(timezone.utc) + REFRESH_TOKEN_EXPIRE_TIMEDELTA
        
        self.token_repo.create_refresh_token(
            user_id=user.id,
            token_hash=token_hash,
            family_id=family_id,
            expires_at=expires_at
        )
        
        from app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # in seconds
            token_type="Bearer"
        )
    
    def refresh_token(self, refresh_token: str) -> TokenResponse:
        """Refresh access token using refresh token"""
        # Hash the token to look up in DB
        token_hash = hash_refresh_token(refresh_token)
        
        # Find the token
        db_token = self.token_repo.get_refresh_token_by_hash(token_hash)
        if not db_token:
            raise InvalidTokenException("Token de refresco inválido o no existe")
        
        # Check if revoked
        if db_token.revoked_at is not None:
            # REPLAY ATTACK DETECTION
            # Someone is trying to use a revoked token
            # Revoke all tokens in the family
            if db_token.family_id:
                self.token_repo.revoke_all_by_family(db_token.family_id)
            raise InvalidTokenException("Posible acceso no autorizado. Vuelve a loguear.")
        
        # Check if expired
        now_aware = datetime.now(timezone.utc)
        if db_token.expires_at.tzinfo is None:
            expires_at_aware = db_token.expires_at.replace(tzinfo=timezone.utc)
        else:
            expires_at_aware = db_token.expires_at
        if expires_at_aware < now_aware:
            raise InvalidTokenException("Token de refresco expirado")
        
        # Get user
        user = self.user_repo.get_user_by_id(db_token.user_id)
        if not user:
            raise UserNotFoundException()
        
        # Revoke old token
        db_token.revoked_at = datetime.now(timezone.utc)
        self.db.commit()
        
        # Create new tokens with same family_id
        user_roles = [role.role for role in user.roles]
        access_token = create_access_token(user.id, user_roles)
        new_refresh_token, new_token_hash = create_refresh_token(user.id, db_token.family_id)
        
        # Store new refresh token
        from app.core.config import REFRESH_TOKEN_EXPIRE_TIMEDELTA
        expires_at = datetime.now(timezone.utc) + REFRESH_TOKEN_EXPIRE_TIMEDELTA
        
        self.token_repo.create_refresh_token(
            user_id=user.id,
            token_hash=new_token_hash,
            family_id=db_token.family_id,
            expires_at=expires_at
        )
        
        from app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES
        return TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            token_type="Bearer"
        )
    
    def logout(self, user_id: UUID, refresh_token: str) -> bool:
        """Logout user by revoking refresh token"""
        token_hash = hash_refresh_token(refresh_token)
        return self.token_repo.revoke_by_hash(token_hash)
