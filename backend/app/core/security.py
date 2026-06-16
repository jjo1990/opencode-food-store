"""
Security utilities for hashing, tokens, and password management
"""

import hashlib
import secrets
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID, uuid4

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHash

from app.core.config import (
    ACCESS_TOKEN_EXPIRE_TIMEDELTA,
    JWT_ALGORITHM,
    JWT_SECRET_KEY,
    REFRESH_TOKEN_EXPIRE_TIMEDELTA,
)

# Initialize password hasher
pwd_context = PasswordHasher()


def hash_password(password: str) -> str:
    """Hash a password using Argon2"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its hash"""
    try:
        pwd_context.verify(hashed_password, plain_password)
        return True
    except (InvalidHash, Exception):
        return False


def hash_refresh_token(token: str) -> str:
    """Hash a refresh token using SHA256"""
    return hashlib.sha256(token.encode()).hexdigest()


def create_access_token(
    user_id: UUID, roles: list[str], expires_delta: timedelta | None = None
) -> str:
    """Create a JWT access token"""
    if expires_delta is None:
        expires_delta = ACCESS_TOKEN_EXPIRE_TIMEDELTA

    expire = datetime.now(UTC) + expires_delta
    payload = {
        "sub": str(user_id),
        "roles": roles,
        "exp": expire,
        "iat": datetime.now(UTC),
        "type": "access",
    }

    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def create_refresh_token(user_id: UUID, family_id: UUID | None = None) -> tuple[str, str]:
    """
    Create a refresh token and return the token and its hash.

    Returns:
        tuple: (token, token_hash)
    """
    if family_id is None:
        family_id = UUID(
            "00000000-0000-0000-0000-000000000000"
        )  # Default, will be set on first login

    expire = datetime.now(UTC) + REFRESH_TOKEN_EXPIRE_TIMEDELTA

    # Generate random token
    secrets.token_urlsafe(48)

    payload = {
        "sub": str(user_id),
        "family_id": str(family_id),
        "exp": expire,
        "iat": datetime.now(UTC),
        "jti": str(uuid4()),
        "type": "refresh",
    }

    # Encode the payload to JWT
    jwt_token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

    # Hash it for storage
    token_hash = hash_refresh_token(jwt_token)

    return jwt_token, token_hash


def decode_token(token: str) -> dict[str, Any]:
    """
    Decode and verify a JWT token.

    Raises:
        jwt.ExpiredSignatureError: If token is expired
        jwt.InvalidTokenError: If token is invalid
    """
    return jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])


def decode_access_token(token: str) -> dict[str, Any] | None:
    """Decode an access token, return None if invalid/expired"""
    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            return None
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def decode_refresh_token(token: str) -> dict[str, Any] | None:
    """Decode a refresh token, return None if invalid/expired"""
    try:
        payload = decode_token(token)
        if payload.get("type") != "refresh":
            return None
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
