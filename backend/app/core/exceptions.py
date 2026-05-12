"""
HTTP Exceptions and error handling
"""
from fastapi import HTTPException, status


class AuthException(HTTPException):
    """Base authentication exception"""
    pass


class InvalidCredentialsException(AuthException):
    """Raised when email or password is invalid"""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas"
        )


class UserAlreadyExistsException(HTTPException):
    """Raised when user already exists"""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail="El email ya está registrado"
        )


class InvalidTokenException(AuthException):
    """Raised when token is invalid"""
    def __init__(self, detail: str = "Token inválido o expirado"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail
        )


class UserNotFoundException(HTTPException):
    """Raised when user is not found"""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )


class UnauthorizedException(HTTPException):
    """Raised when user is not authenticated"""
    def __init__(self, detail: str = "No autenticado"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail
        )


class ForbiddenException(HTTPException):
    """Raised when user doesn't have permission"""
    def __init__(self, detail: str = "No tienes permisos para esta acción"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )


class RateLimitException(HTTPException):
    """Raised when rate limit is exceeded"""
    def __init__(self, detail: str = "Demasiados intentos. Intenta más tarde."):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=detail
        )
