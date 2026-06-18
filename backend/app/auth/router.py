"""
Authentication routes
"""

from fastapi import APIRouter, Depends, HTTPException, Request, status
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
from app.core.limiter import limiter
from app.models import User

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: Request,
    register_data: RegisterRequest,
    db: Session = Depends(get_db),
) -> UserResponse:
    """Register a new user"""
    service = AuthService(db)
    return service.register(
        email=register_data.email,
        password=register_data.password,
        full_name=register_data.full_name,
    )


@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/15minutes")
async def login(
    request: Request,
    login_data: LoginRequest,
    db: Session = Depends(get_db),
) -> TokenResponse:
    """Login with email and password"""
    service = AuthService(db)
    return service.login(email=login_data.email, password=login_data.password)


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
