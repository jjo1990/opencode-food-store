"""
Authentication routes
"""

from fastapi import APIRouter, Depends, HTTPException, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session

from app.auth.schemas import (
    LoginRequest,
    RefreshTokenRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from app.auth.service import AuthService
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.exceptions import InvalidTokenException
from app.models import User

router = APIRouter(prefix="/auth", tags=["auth"])

# Rate limiter
limiter = Limiter(key_func=get_remote_address)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest, db: Session = Depends(get_db)) -> UserResponse:
    """Register a new user"""
    service = AuthService(db)
    return service.register(
        email=request.email, password=request.password, full_name=request.full_name
    )


@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/15minutes")
async def login(request: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    """Login with email and password"""
    service = AuthService(db)
    return service.login(email=request.email, password=request.password)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(request: RefreshTokenRequest, db: Session = Depends(get_db)) -> TokenResponse:
    """Refresh access token using refresh token"""
    service = AuthService(db)
    try:
        return service.refresh_token(request.refresh_token)
    except InvalidTokenException as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=e.detail)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    request: RefreshTokenRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    """Logout user and revoke refresh token"""
    service = AuthService(db)
    service.logout(current_user.id, request.refresh_token)
