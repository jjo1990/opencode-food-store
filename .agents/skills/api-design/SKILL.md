# API Design Skill

**Patterns and best practices for designing clean, consistent REST APIs with FastAPI**

## Overview

This skill provides guidance for designing REST APIs that are intuitive, scalable, and well-documented using FastAPI conventions.

## HTTP Methods & Status Codes

### CRUD Operations

| Operation | Method | Path | Status Code | Response |
|-----------|--------|------|-------------|----------|
| Create | POST | `/users` | 201 | Created resource |
| Read | GET | `/users/{id}` | 200 | Resource |
| Update | PUT | `/users/{id}` | 200 | Updated resource |
| Patch | PATCH | `/users/{id}` | 200 | Partially updated |
| Delete | DELETE | `/users/{id}` | 204 | No content |
| List | GET | `/users` | 200 | Array of resources |

### Status Codes Guide

```
2xx - Success
  200 OK              - Request successful, body has data
  201 Created         - Resource created successfully
  204 No Content      - Request successful, no body

4xx - Client Error
  400 Bad Request     - Invalid request body
  401 Unauthorized    - Missing/invalid authentication
  403 Forbidden       - Insufficient permissions
  404 Not Found       - Resource not found
  409 Conflict        - Resource already exists
  422 Unprocessable   - Validation error

5xx - Server Error
  500 Internal Server Error
  503 Service Unavailable
```

## API Endpoint Design

### Resource-Based URLs

**Good** ✅
```
GET    /api/v1/users
POST   /api/v1/users
GET    /api/v1/users/{user_id}
PUT    /api/v1/users/{user_id}
DELETE /api/v1/users/{user_id}

GET    /api/v1/users/{user_id}/orders
GET    /api/v1/users/{user_id}/orders/{order_id}
```

**Bad** ❌
```
GET    /api/getUser?id=1
POST   /api/createUser
GET    /api/getUserOrders
GET    /api/getUserOrderById
```

### Nested Resources (Maximum 2 Levels)

```
/api/v1/users/{user_id}/addresses
/api/v1/users/{user_id}/addresses/{address_id}
```

## Food Store API Design

### Authentication Endpoints

```python
# File: backend/app/api/routes/auth.py

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from app.schemas.auth import (
    RegisterRequest, LoginRequest, TokenResponse, RefreshTokenRequest
)
from app.services.auth import AuthService

router = APIRouter(prefix="/api/v1/auth", tags=["authentication"])

@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account with email and password"
)
def register(request: RegisterRequest, service: AuthService = Depends()):
    """
    Register a new user.
    
    **Request Body**:
    - `email`: User email (unique)
    - `password`: User password (min 8 chars, uppercase, number, special char)
    
    **Responses**:
    - `201`: User created, returns access and refresh tokens
    - `400`: Validation error
    - `409`: Email already exists
    
    **Example**:
    ```json
    {
      "email": "user@example.com",
      "password": "SecurePassword123!"
    }
    ```
    """
    try:
        user, tokens = service.register(request)
        return TokenResponse(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_type="bearer",
            expires_in=1800
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )

@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="User login"
)
def login(request: LoginRequest, service: AuthService = Depends()):
    """
    User login.
    
    **Responses**:
    - `200`: Login successful, returns tokens
    - `401`: Invalid credentials
    - `422`: Validation error
    """
    user = service.authenticate(request.email, request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    tokens = service.create_tokens(user)
    return TokenResponse(
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
        token_type="bearer",
        expires_in=1800
    )

@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Refresh access token"
)
def refresh_token(request: RefreshTokenRequest, service: AuthService = Depends()):
    """
    Get new access token using refresh token.
    
    **Responses**:
    - `200`: New tokens generated
    - `401`: Invalid refresh token
    """
    tokens = service.refresh_access_token(request.refresh_token)
    if not tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )
    
    return TokenResponse(
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
        token_type="bearer",
        expires_in=1800
    )

@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="User logout"
)
def logout(token: str = Depends(get_token), service: AuthService = Depends()):
    """
    Invalidate refresh token.
    
    **Responses**:
    - `204`: Logged out successfully
    """
    service.revoke_refresh_token(token)
    return None
```

### Request/Response Schemas

```python
# File: backend/app/schemas/auth.py

from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional

class RegisterRequest(BaseModel):
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(
        ...,
        min_length=8,
        description="Password (min 8 chars, 1 uppercase, 1 number, 1 special char)"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "SecurePassword123!"
            }
        }

class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    
    class Config:
        schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "SecurePassword123!"
            }
        }

class TokenResponse(BaseModel):
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="Refresh token")
    token_type: str = Field(default="bearer")
    expires_in: int = Field(..., description="Token expiration in seconds")
    
    class Config:
        schema_extra = {
            "example": {
                "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
                "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
                "token_type": "bearer",
                "expires_in": 1800
            }
        }

class UserResponse(BaseModel):
    id: int
    email: str
    role: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
        schema_extra = {
            "example": {
                "id": 1,
                "email": "user@example.com",
                "role": "customer",
                "is_active": True,
                "created_at": "2024-01-01T12:00:00"
            }
        }

class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., description="Refresh token from login response")
```

### Error Response Format

```python
# File: backend/app/schemas/error.py

from pydantic import BaseModel
from typing import Any, List, Optional

class ErrorDetail(BaseModel):
    loc: List[str]  # Location of error (e.g., ["body", "email"])
    msg: str        # Error message
    type: str       # Error type (e.g., "value_error")

class ErrorResponse(BaseModel):
    detail: str | List[ErrorDetail]
    
    class Config:
        schema_extra = {
            "example": {
                "detail": "Invalid email format"
            }
        }
```

### Exception Handlers

```python
# File: backend/app/api/exception_handlers.py

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

def register_exception_handlers(app: FastAPI):
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=422,
            content={
                "detail": exc.errors(),
                "body": exc.body
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )
```

## API Documentation

### OpenAPI/Swagger

All endpoints automatically documented at `/docs`

```python
# File: backend/app/main.py

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

app = FastAPI(
    title="Food Store API",
    description="E-commerce API for food products",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="Food Store API",
        version="1.0.0",
        description="Complete e-commerce API",
        routes=app.routes,
    )
    
    openapi_schema["info"]["x-logo"] = {
        "url": "https://example.com/logo.png"
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
```

## Pagination & Filtering

### List Endpoints with Pagination

```python
@router.get(
    "/users",
    response_model=PaginatedResponse[UserResponse],
    summary="List users"
)
def list_users(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of items to return"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    service: UserService = Depends()
):
    """
    List all users with pagination.
    
    **Query Parameters**:
    - `skip`: Offset (default 0)
    - `limit`: Items per page (max 100)
    - `is_active`: Filter by active status
    
    **Example**: `/api/v1/users?skip=0&limit=20&is_active=true`
    """
    users, total = service.list_users(skip=skip, limit=limit, filters={"is_active": is_active})
    return PaginatedResponse(
        items=users,
        total=total,
        skip=skip,
        limit=limit
    )

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    skip: int
    limit: int
    
    @property
    def pages(self) -> int:
        return (self.total + self.limit - 1) // self.limit
```

## Versioning Strategy

### URL-Based Versioning (Recommended)

```python
app = FastAPI()

# v1 routes
auth_v1 = APIRouter(prefix="/api/v1/auth", tags=["authentication"])
users_v1 = APIRouter(prefix="/api/v1/users", tags=["users"])

# v2 routes (future)
# auth_v2 = APIRouter(prefix="/api/v2/auth", tags=["authentication"])

app.include_router(auth_v1)
app.include_router(users_v1)
```

## Best Practices

### 1. Consistent Naming
```python
✅ /api/v1/users/{user_id}/orders
✅ /api/v1/products/{product_id}/reviews
❌ /api/v1/user/{userId}/orders
❌ /api/v1/products/{id}/review
```

### 2. Use Query Parameters for Filtering
```python
✅ GET /api/v1/orders?status=shipped&user_id=1
❌ GET /api/v1/orders/shipped/1
```

### 3. Use Path Parameters for Resource Identity
```python
✅ GET /api/v1/orders/{order_id}
❌ GET /api/v1/orders?id=1
```

### 4. HTTP Methods Match Operations
```python
✅ POST /api/v1/users (create)
✅ GET /api/v1/users/{id} (read)
✅ PUT /api/v1/users/{id} (update)
✅ DELETE /api/v1/users/{id} (delete)
❌ GET /api/v1/users/create
❌ GET /api/v1/users/delete
```

### 5. Document All Status Codes
```python
@router.post("/users", status_code=201, responses={
    201: {"description": "User created"},
    400: {"description": "Invalid request"},
    409: {"description": "Email already exists"}
})
```

## Phase 1 API Routes

### Authentication API

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/auth/register` | Register new user |
| POST | `/api/v1/auth/login` | User login |
| POST | `/api/v1/auth/refresh` | Refresh access token |
| POST | `/api/v1/auth/logout` | User logout |

### User API

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/users/profile` | Get current user |
| PUT | `/api/v1/users/profile` | Update profile |
| POST | `/api/v1/users/{user_id}/change-password` | Change password |

## See Also

- `backend/app/api/routes/` — Route definitions
- `backend/app/schemas/` — Request/response models
- `backend/app/main.py` — FastAPI app configuration
- `docs/Historias_de_usuario.txt` — API requirements from user stories
