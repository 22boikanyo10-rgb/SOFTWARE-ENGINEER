"""Test configuration and fixtures."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from wealthmind.main import app
from wealthmind.database import get_db
from wealthmind.models import Base
from wealthmind.security import SecurityManager

# Create in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLAALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def db():
    """Create a fresh database for each test."""
    Base.metadata.create_all(bind=engine)
    yield TestingSessionLocal()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db: Session):
    """Create a test client with overridden database."""
    app.dependency_overrides[get_db] = override_get_db
    
    # Re-create tables
    Base.metadata.create_all(bind=engine)
    
    client = TestClient(app)
    yield client
    
    # Cleanup
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()


@pytest.fixture
def test_user_data():
    """Sample user data for testing."""
    return {
        "email": "test@example.com",
        "username": "testuser",
        "password": "TestPassword123!",
        "full_name": "Test User"
    }


@pytest.fixture
def test_user_data_2():
    """Second sample user data for testing."""
    return {
        "email": "test2@example.com",
        "username": "testuser2",
        "password": "TestPassword456!",
        "full_name": "Test User 2"
    }


@pytest.fixture
def registered_user(client: TestClient, test_user_data: dict):
    """Register a user and return user data with token."""
    response = client.post("/api/v1/auth/register", json=test_user_data)
    assert response.status_code == 201
    user = response.json()
    
    # Login to get token
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": test_user_data["email"], "password": test_user_data["password"]}
    )
    assert login_response.status_code == 200
    tokens = login_response.json()
    
    return {
        "user": user,
        "access_token": tokens["access_token"],
        "refresh_token": tokens["refresh_token"]
    }


@pytest.fixture
def bank_account_data():
    """Sample bank account data for testing."""
    return {
        "account_name": "Checking Account",
        "account_type": "checking",
        "account_number": "1234567890",
        "bank_name": "Test Bank",
        "balance": 5000.00,
        "currency": "USD"
    }


@pytest.fixture
def transaction_data():
    """Sample transaction data for testing."""
    from datetime import datetime
    return {
        "transaction_type": "expense",
        "amount": 50.00,
        "category": "food",
        "description": "Grocery shopping",
        "merchant_name": "Whole Foods",
        "transaction_date": datetime.utcnow().isoformat(),
        "is_recurring": False,
        "tags": "groceries,weekly"
    }
