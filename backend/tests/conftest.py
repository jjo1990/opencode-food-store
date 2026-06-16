"""
Conftest for pytest configuration
"""

import os

os.environ["DATABASE_URL"] = "sqlite:///./test.db"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.auth.router import limiter

limiter.enabled = False

# Use in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """Create a test database session"""
    from app.models import Base

    # Create tables
    Base.metadata.create_all(bind=engine)

    db_session = TestingSessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()
        # Clean up
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db: Session):
    """Create a test client"""
    from app.core.database import get_db
    from app.main import app

    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def test_user_data():
    """Test user data"""
    return {
        "email": "testuser@example.com",
        "password": "SecurePassword123",
        "full_name": "Test User",
    }
