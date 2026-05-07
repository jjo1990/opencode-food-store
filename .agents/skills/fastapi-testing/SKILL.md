# FastAPI Testing Skill

**Patterns and best practices for testing FastAPI applications**

## Overview

This skill provides comprehensive guidance for writing unit, integration, and E2E tests for FastAPI backends using pytest, fixtures, and mocking.

## Testing Framework Setup

### Dependencies (already in `requirements.txt`)

```txt
pytest==7.4.0
pytest-asyncio==0.21.1
pytest-cov==4.1.0
httpx==0.24.1
sqlalchemy-utils==0.41.1
faker==19.0.0
```

### Configuration (`conftest.py`)

**File**: `backend/tests/conftest.py`

```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.base import Base
from app.db.session import get_db

# Use in-memory SQLite for tests
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"

@pytest.fixture(scope="session")
def db_engine():
    engine = create_engine(
        SQLALCHEMY_TEST_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session(db_engine):
    TestingSessionLocal = sessionmaker(bind=db_engine)
    session = TestingSessionLocal()
    yield session
    session.rollback()
    session.close()

@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()

@pytest.fixture
def auth_headers(client):
    """Create authenticated user and return headers"""
    # Register user
    response = client.post("/api/auth/register", json={
        "email": "test@example.com",
        "password": "securepassword123"
    })
    assert response.status_code == 201
    
    # Login
    response = client.post("/api/auth/login", json={
        "email": "test@example.com",
        "password": "securepassword123"
    })
    assert response.status_code == 200
    token = response.json()["access_token"]
    
    return {"Authorization": f"Bearer {token}"}
```

## Test Patterns

### 1. Route Testing

**Pattern**: Test endpoint with different inputs and status codes

```python
# File: backend/tests/unit/test_auth_routes.py

import pytest
from fastapi import status

def test_register_user(client):
    """Test successful user registration"""
    response = client.post("/api/auth/register", json={
        "email": "newuser@example.com",
        "password": "securepassword123"
    })
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["email"] == "newuser@example.com"

def test_register_user_invalid_email(client):
    """Test registration with invalid email"""
    response = client.post("/api/auth/register", json={
        "email": "invalid-email",
        "password": "securepassword123"
    })
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_register_user_duplicate(client):
    """Test registration with existing email"""
    # Create first user
    client.post("/api/auth/register", json={
        "email": "test@example.com",
        "password": "password123"
    })
    
    # Try to register same email
    response = client.post("/api/auth/register", json={
        "email": "test@example.com",
        "password": "password456"
    })
    assert response.status_code == status.HTTP_409_CONFLICT

def test_login_success(client):
    """Test successful login"""
    # Register user first
    client.post("/api/auth/register", json={
        "email": "test@example.com",
        "password": "password123"
    })
    
    # Login
    response = client.post("/api/auth/login", json={
        "email": "test@example.com",
        "password": "password123"
    })
    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()
    assert "refresh_token" in response.json()

def test_login_invalid_credentials(client):
    """Test login with wrong password"""
    response = client.post("/api/auth/login", json={
        "email": "nonexistent@example.com",
        "password": "wrongpassword"
    })
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
```

### 2. Authentication Testing

**Pattern**: Test protected routes and authorization

```python
# File: backend/tests/unit/test_auth_protected.py

def test_protected_route_without_auth(client):
    """Test accessing protected route without token"""
    response = client.get("/api/users/profile")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_protected_route_with_valid_token(client, auth_headers):
    """Test accessing protected route with valid token"""
    response = client.get("/api/users/profile", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK

def test_protected_route_with_invalid_token(client):
    """Test with malformed token"""
    headers = {"Authorization": "Bearer invalid.token.here"}
    response = client.get("/api/users/profile", headers=headers)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_role_based_access(client, auth_headers):
    """Test endpoint that requires specific role"""
    # Try to access admin endpoint as regular user
    response = client.get("/api/admin/dashboard", headers=auth_headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN
```

### 3. Database Query Testing

**Pattern**: Test service layer with mocked/real database

```python
# File: backend/tests/unit/test_user_service.py

from unittest.mock import Mock, patch
from app.services.user_service import UserService
from app.schemas.user import UserCreate

def test_create_user(db_session):
    """Test user creation through service"""
    service = UserService(db_session)
    user_data = UserCreate(
        email="test@example.com",
        password="password123"
    )
    
    user = service.create_user(user_data)
    
    assert user.email == "test@example.com"
    assert user.password_hash != "password123"  # Should be hashed
    assert user.id is not None

def test_get_user_by_email(db_session):
    """Test fetching user by email"""
    service = UserService(db_session)
    
    # Create user
    service.create_user(UserCreate(
        email="test@example.com",
        password="password123"
    ))
    
    # Fetch user
    user = service.get_user_by_email("test@example.com")
    assert user is not None
    assert user.email == "test@example.com"

def test_user_not_found(db_session):
    """Test fetching non-existent user"""
    service = UserService(db_session)
    user = service.get_user_by_email("nonexistent@example.com")
    assert user is None
```

### 4. Async/Await Testing

**Pattern**: Test async endpoints with pytest-asyncio

```python
# File: backend/tests/unit/test_async_routes.py

import pytest

@pytest.mark.asyncio
async def test_async_endpoint(client):
    """Test async route handler"""
    response = client.get("/api/async-operation")
    assert response.status_code == status.HTTP_200_OK

@pytest.mark.asyncio
async def test_async_with_timeout(client):
    """Test async endpoint that might timeout"""
    response = client.get("/api/long-operation?timeout=1")
    # Should handle timeout gracefully
    assert response.status_code in [status.HTTP_200_OK, status.HTTP_504_GATEWAY_TIMEOUT]
```

### 5. Error Handling Testing

**Pattern**: Test exception handling and error responses

```python
# File: backend/tests/unit/test_error_handling.py

def test_validation_error(client):
    """Test request validation error"""
    response = client.post("/api/auth/register", json={
        "email": "test@example.com"
        # Missing password field
    })
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert "password" in response.json()["detail"][0]["loc"]

def test_database_error(client, db_session, monkeypatch):
    """Test handling of database errors"""
    def mock_query(*args, **kwargs):
        raise Exception("Database connection failed")
    
    monkeypatch.setattr(db_session, "query", mock_query)
    
    response = client.get("/api/users")
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
```

## Test Organization

### Directory Structure

```
backend/tests/
├── conftest.py              # Shared fixtures
├── __init__.py
├── unit/                    # Unit tests (no DB)
│   ├── test_auth_routes.py
│   ├── test_auth_protected.py
│   ├── test_user_service.py
│   └── test_validators.py
├── integration/             # Integration tests (with DB)
│   ├── test_auth_flow.py
│   ├── test_product_crud.py
│   └── test_order_creation.py
└── e2e/                     # End-to-end tests
    └── test_complete_flow.py
```

## Running Tests

### All Tests
```bash
pytest backend/tests -v
```

### With Coverage
```bash
pytest backend/tests --cov=app --cov-report=html
```

### Specific Test File
```bash
pytest backend/tests/unit/test_auth_routes.py -v
```

### Specific Test
```bash
pytest backend/tests/unit/test_auth_routes.py::test_register_user -v
```

### Watch Mode
```bash
pytest-watch backend/tests
```

## Mocking Patterns

### Mock External Services

```python
from unittest.mock import patch, MagicMock

@patch('app.services.payment.MercadoPagoAPI')
def test_payment_processing(mock_mp_api, client):
    """Test payment flow with mocked API"""
    mock_mp_api.return_value.process_payment.return_value = {
        "id": "123456",
        "status": "approved"
    }
    
    response = client.post("/api/orders/pay", json={"order_id": 1})
    assert response.status_code == status.HTTP_200_OK
```

### Mock Time/Dates

```python
from unittest.mock import patch
from datetime import datetime, timedelta

@patch('app.utils.get_current_time')
def test_token_expiration(mock_time, client):
    """Test token expiration logic"""
    mock_time.return_value = datetime(2024, 1, 1, 12, 0, 0)
    
    # Token created
    token = create_token(user_id=1)
    
    # Move time forward
    mock_time.return_value = datetime(2024, 1, 2, 12, 0, 0)
    
    # Token should be expired
    assert not is_token_valid(token)
```

## Performance Metrics

### Coverage Goals (Phase 1 - Auth)
- Unit tests: **95%+** coverage
- Integration tests: **80%+** coverage
- Critical paths: **100%** coverage

### Running Coverage
```bash
pytest backend/tests --cov=app --cov-report=term-missing
```

## Best Practices

1. **Test Naming**: `test_<function>_<scenario>_<expected_result>`
   ```python
   ✅ test_register_user_with_valid_email_creates_user
   ✅ test_login_with_wrong_password_returns_401
   ❌ test_something
   ```

2. **Arrange-Act-Assert (AAA) Pattern**
   ```python
   def test_example():
       # Arrange: Set up test data
       user = create_user("test@example.com")
       
       # Act: Perform the action
       result = fetch_user("test@example.com")
       
       # Assert: Verify result
       assert result.id == user.id
   ```

3. **One Assertion Per Test** (when possible)
   - Makes tests focused and easier to debug

4. **Use Fixtures** instead of setup/teardown
   - More readable, reusable, and composable

5. **Isolate Tests** from external dependencies
   - Use mocks for APIs, emails, external services

## Integration with Food Store Phase 1

### Critical Test Cases (Authentication)

- ✅ User registration with valid/invalid email
- ✅ Password hashing and verification
- ✅ JWT token generation and validation
- ✅ Refresh token rotation
- ✅ Role-based access control
- ✅ Token expiration handling
- ✅ Login/logout flow
- ✅ Protected route access
- ✅ Audit logging of auth events

### Test Execution in CI/CD

In `.github/workflows/test.yml`:
```yaml
- name: Run FastAPI Tests
  run: |
    cd backend
    pytest tests --cov=app --cov-report=xml
```

## See Also

- `backend/requirements.txt` — Dependencies
- `backend/tests/conftest.py` — Test configuration
- `backend/app/main.py` — FastAPI app structure
- `docs/Historias_de_usuario.txt` — User stories for acceptance criteria
