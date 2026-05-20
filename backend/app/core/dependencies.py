"""
Dependency injection and middleware
"""

from uuid import UUID

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import ForbiddenException, UnauthorizedException
from app.core.security import decode_access_token
from app.models import User

# HTTP Bearer security scheme
http_bearer = HTTPBearer()
http_bearer_optional = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer), db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get the current authenticated user from JWT token
    """
    token = credentials.credentials

    payload = decode_access_token(token)
    if not payload:
        raise UnauthorizedException("Token inválido o expirado")

    user_id = payload.get("sub")
    if not user_id:
        raise UnauthorizedException("Token inválido")

    try:
        user_id_uuid = UUID(user_id)
    except (ValueError, TypeError):
        raise UnauthorizedException("Token inválido")

    user = db.query(User).filter(User.id == user_id_uuid, User.soft_deleted_at.is_(None)).first()

    if not user:
        raise UnauthorizedException("Usuario no encontrado")

    return user


async def get_current_user_with_roles(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get current user with their roles loaded
    """
    # Refresh the user object to ensure roles are loaded
    db.refresh(current_user)
    return current_user


async def get_optional_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(http_bearer_optional),
    db: Session = Depends(get_db),
) -> User | None:
    """
    Dependency to optionally get current user from JWT token.
    Returns None if no token provided or token is invalid.
    """
    if not credentials:
        return None
    try:
        payload = decode_access_token(credentials.credentials)
        if not payload:
            return None
        user_id = payload.get("sub")
        if not user_id:
            return None
        user = (
            db.query(User).filter(User.id == UUID(user_id), User.soft_deleted_at.is_(None)).first()
        )
        return user
    except Exception:
        return None


def require_role(*allowed_roles: str):
    """
    Dependency factory that checks if user has one of the allowed roles.

    Usage:
        @router.get("/admin")
        async def admin_endpoint(current_user = Depends(require_role("ADMIN"))):
            pass
    """

    async def check_role(current_user: User = Depends(get_current_user_with_roles)) -> User:
        user_roles = [role.role for role in current_user.roles]

        if not any(role in allowed_roles for role in user_roles):
            raise ForbiddenException(f"Se requiere uno de estos roles: {', '.join(allowed_roles)}")

        return current_user

    return check_role
