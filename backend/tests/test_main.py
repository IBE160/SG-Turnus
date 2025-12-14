from fastapi.testclient import TestClient
from backend.main import app
from backend.app.core import auth_service
from backend.app.database import get_db
import backend.app.models.user # Import the module to get its Base and User
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
import os
import re
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# ----------------------------------------------------
# Test Database Setup
# ----------------------------------------------------

# Create a separate test engine and sessionmaker
TEST_SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db" # Or :memory: for purely in-memory
test_engine = create_engine(TEST_SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

@pytest.fixture(scope="function")
def db_session():
    """
    Provides a clean, independent database session for each test function.
    Tables are created before the test and dropped after.
    """
    backend.app.models.user.Base.metadata.create_all(bind=test_engine) # Create tables for this test
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        backend.app.models.user.Base.metadata.drop_all(bind=test_engine) # Drop tables after test

# Override the get_db dependency for FastAPI app during testing
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Apply the dependency override to the app
app.dependency_overrides[get_db] = override_get_db

# Create a TestClient instance
client = TestClient(app)

# ----------------------------------------------------
# Fixtures and Test Functions
# ----------------------------------------------------

@pytest.fixture(autouse=True)
def clear_auth_service_mocks():
    """
    Pytest autouse fixture, now empty as mock_db is removed.
    """
    pass # No longer needed as mock_db is removed

def test_health_check():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

@patch('backend.app.core.auth_service.email_service.send_verification_email', new_callable=AsyncMock)
def test_register_user_success(mock_send_email, db_session: Session):
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "test@example.com", "password": "Password123!"}
    )
    assert response.status_code == 201
    assert "user_id" in response.json()
    assert response.json()["email"] == "test@example.com"
    
    user = db_session.query(backend.app.models.user.User).filter(backend.app.models.user.User.email == "test@example.com").first()
    assert user is not None
    assert user.is_verified == False
    mock_send_email.assert_called_once()
    assert mock_send_email.call_args.args[0] == "test@example.com"
    assert "http://localhost:3000/verify-email" in mock_send_email.call_args.args[1]

def test_register_user_duplicate_email(db_session: Session):
    # Register the first user
    client.post(
        "/api/v1/auth/register",
        json={"email": "test@example.com", "password": "Password123!"}
    )
    # Attempt to register with duplicate email
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "test@example.com", "password": "AnotherPassword!"}
    )
    assert response.status_code == 409
    assert response.json() == {"detail": "User with this email already exists"}

@patch('backend.app.core.auth_service.email_service.send_verification_email', new_callable=AsyncMock)
def test_verify_email_success(mock_send_email, db_session: Session):
    # First, register a user
    register_response = client.post(
        "/api/v1/auth/register",
        json={"email": "verify@example.com", "password": "Password123!"}
    )
    assert register_response.status_code == 201
    mock_send_email.assert_called_once() # Email sent during registration

    # In a real scenario, the verification token would be stored and retrieved.
    # For this mock, we assume the token sent matches a temporary token.
    # The actual token would have been sent in the email by auth_service.
    # For the purpose of this test, we just need a non-empty token.
    token = "mock_verification_token"

    # Now, verify the email
    verify_response = client.post(
        "/api/v1/auth/verify-email",
        json={"email": "verify@example.com", "token": token}
    )
    assert verify_response.status_code == 200
    assert verify_response.json() == {"message": "Email verified successfully."}
    
    user = db_session.query(backend.app.models.user.User).filter(backend.app.models.user.User.email == "verify@example.com").first()
    assert user is not None
    assert user.is_verified == True

def test_verify_email_invalid_token(db_session: Session):
    # First, register a user
    client.post(
        "/api/v1/auth/register",
        json={"email": "invalidtoken@example.com", "password": "Password123!"}
    )
    # Attempt to verify with an invalid token (AuthService expects any non-empty token for now)
    response = client.post(
        "/api/v1/auth/verify-email",
        json={"email": "invalidtoken@example.com", "token": ""} # Empty token will fail based on current AuthService logic
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Verification token is missing"}

def test_verify_email_user_not_found(db_session: Session):
    response = client.post(
        "/api/v1/auth/verify-email",
        json={"email": "nonexistent@example.com", "token": "any_token"}
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}

@patch('backend.app.core.auth_service.email_service.send_verification_email', new_callable=AsyncMock)
def test_verify_email_already_verified(mock_send_email, db_session: Session):
    # First, register and verify a user
    client.post(
        "/api/v1/auth/register",
        json={"email": "alreadyverified@example.com", "password": "Password123!"}
    )

    token = "mock_verification_token" # Placeholder token
    client.post(
        "/api/v1/auth/verify-email",
        json={"email": "alreadyverified@example.com", "token": token}
    )
    
    user = db_session.query(backend.app.models.user.User).filter(backend.app.models.user.User.email == "alreadyverified@example.com").first()
    assert user is not None
    assert user.is_verified == True

    # Try to verify again
    reverify_response = client.post(
        "/api/v1/auth/verify-email",
        json={"email": "alreadyverified@example.com", "token": token}
    )
    assert reverify_response.status_code == 200
    assert reverify_response.json() == {"message": "Email verified successfully."}

@patch.dict(os.environ, {"AUTH0_DOMAIN": "", "AUTH0_MANAGEMENT_CLIENT_ID": "", "AUTH0_MANAGEMENT_CLIENT_SECRET": ""}, clear=True) # Ensure Auth0 env vars are empty
@patch('backend.app.core.auth_service.email_service.send_verification_email', new_callable=AsyncMock)
def test_register_user_auth0_success(mock_send_email, db_session: Session):
    # Auth0 env vars are empty, so AuthService should fall back to mock Auth0 user creation.
    # The AuthService is a singleton initialized at module load. Its _auth0 will be None
    # because os.getenv was not patched at that time.
    # This test verifies the behavior when Auth0 is NOT configured.

    # Ensure the auth_service singleton is re-instantiated to pick up the patched os.environ
    # or that it uses the default behavior based on currently empty env vars.
    auth_service.auth_service = auth_service.AuthService()

    response = client.post(
        "/api/v1/auth/register",
        json={"email": "auth0test@example.com", "password": "Password123!"}
    )

    assert response.status_code == 201
    assert "user_id" in response.json()
    
    # Assert that the returned user_id matches the mock_auth_id_UUID pattern
    assert re.match(r"^mock_auth_id_[a-f0-9\-]+$", response.json()["user_id"])
    
    # Ensure the returned user_id matches the created DB user's auth_provider_id
    user = db_session.query(backend.app.models.user.User).filter(backend.app.models.user.User.email == "auth0test@example.com").first()
    assert user is not None
    assert response.json()["user_id"] == user.auth_provider_id
    
    assert response.json()["email"] == "auth0test@example.com"
    
    # Assert that email was sent (as it's part of the register_user flow)
    mock_send_email.assert_called_once()
    
    # Assert that our local db_session was updated correctly with the generated mock ID
    assert re.match(r"^mock_auth_id_[a-f0-9\-]+$", user.auth_provider_id)
    assert user.is_verified == False