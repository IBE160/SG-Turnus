import httpx # Import httpx for httpx.HTTPStatusError
import os
import re
from unittest.mock import patch, AsyncMock, MagicMock
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from backend.main import app
from backend.app.core import auth_service
import backend.app.models.user
import backend.app.services.email_service # Import the module to access EmailService class

# ----------------------------------------------------
# Test Database Setup
# ----------------------------------------------------

TEST_SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
test_engine = create_engine(TEST_SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

@pytest.fixture(scope="function")
def db_session():
    backend.app.models.user.Base.metadata.create_all(bind=test_engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        backend.app.models.user.Base.metadata.drop_all(bind=test_engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[backend.app.database.get_db] = override_get_db

client = TestClient(app)

# ----------------------------------------------------
# Fixtures and Test Functions
# ----------------------------------------------------

@pytest.fixture(autouse=True)
def mock_external_services_and_singletons():
    """
    Mocks Auth0 and Resend clients by patching specific attributes of the singletons.
    """
    # Store original environment variables for restoration
    original_env = os.environ.copy()

    # Set dummy environment variables to allow singletons to initialize without ValueError
    os.environ["AUTH0_DOMAIN"] = "mock_domain"
    os.environ["AUTH0_MANAGEMENT_CLIENT_ID"] = "mock_client_id"
    os.environ["AUTH0_MANAGEMENT_CLIENT_SECRET"] = "mock_client_secret"
    os.environ["RESEND_API_KEY"] = "mock_resend_key"
    os.environ["NEXT_PUBLIC_EMAIL_VERIFICATION_URL"] = "http://localhost:3000"
    os.environ["AUTH0_CLIENT_ID"] = "mock_auth_client_id"
    os.environ["AUTH0_CLIENT_SECRET"] = "mock_auth_client_secret"
    os.environ["AUTH0_API_AUDIENCE"] = "https://mockapi.example.com"

    with patch('backend.app.core.auth_service.Auth0') as MockAuth0Class, \
         patch('resend.Emails.send', new_callable=AsyncMock) as MockResendEmailsSend: # PATCH THIS LINE
        
        # Configure MockAuth0Class to return a MagicMock instance when instantiated
        mock_auth0_instance = MagicMock()
        mock_users_object = MagicMock() # Mock the 'users' attribute
        mock_auth0_instance.users = mock_users_object 

        mock_create_method = MagicMock() # Mock the 'create' method
        mock_create_method.return_value = {"user_id": f"auth0|mock_id_{os.urandom(8).hex()}"}
        mock_users_object.create = mock_create_method

        MockAuth0Class.return_value = mock_auth0_instance # When Auth0() is called, return this mock instance

        # Manually set the _auth0 attribute of the *existing* auth_service singleton to our mock
        auth_service.auth_service._auth0 = mock_auth0_instance
        
        # We also need to configure the return value of MockResendEmailsSend
        MockResendEmailsSend.return_value = MagicMock(id="resend_mock_id_123") # Mock the return value of send
        
        yield mock_create_method, MockResendEmailsSend # Yield the mock create method, and the patched send method
        
    # Restore original environment variables after the test
    os.environ.clear()
    os.environ.update(original_env)

# Test login endpoint
@pytest.fixture(autouse=True)
def mock_httpx_async_client_post():
    with patch('httpx.AsyncClient.post', new_callable=AsyncMock) as mock_post:
        yield mock_post

# Test successful login
@pytest.mark.asyncio
async def test_login_success(mock_external_services_and_singletons, db_session: Session, mock_httpx_async_client_post):
    mock_auth0_create_method, mock_resend_emails_send = mock_external_services_and_singletons

    # Setup mock_httpx_async_client_post for successful login
    mock_response = MagicMock(status_code=200)
    mock_response.json = AsyncMock(return_value={
        "access_token": "mock_jwt_token",
        "expires_in": 3600,
        "token_type": "Bearer"
    })
    mock_response.raise_for_status.return_value = None # Ensure no HTTP error
    mock_httpx_async_client_post.return_value = mock_response

    # Register a user first in our DB to ensure local user exists or simulate creation
    client.post(
        "/api/v1/auth/register",
        json={"email": "login_test@example.com", "password": "Password123!"}
    )

    response = client.post(
        "/api/v1/auth/login",
        json={"email": "login_test@example.com", "password": "Password123!"}
    )

    assert response.status_code == 200
    assert response.json()["access_token"] == "mock_jwt_token"
    assert response.json()["token_type"] == "Bearer"
    mock_httpx_async_client_post.assert_called_once()
    
    user = db_session.query(backend.app.models.user.User).filter(backend.app.models.user.User.email == "login_test@example.com").first()
    assert user is not None # Ensure user exists in our DB after login

# Test login with incorrect credentials
@pytest.mark.asyncio
async def test_login_incorrect_credentials(mock_external_services_and_singletons, mock_httpx_async_client_post):
    mock_auth0_create_method, mock_resend_emails_send = mock_external_services_and_singletons

    # Setup mock_httpx_async_client_post for incorrect credentials (Auth0 returns 403 Forbidden)
    mock_httpx_async_client_post.return_value = MagicMock(status_code=403)
    mock_httpx_async_client_post.return_value.json.return_value = {"error": "access_denied", "error_description": "Wrong email or password."}
    mock_httpx_async_client_post.return_value.raise_for_status.side_effect = httpx.HTTPStatusError(
        "Client error '403 Forbidden' for url 'https://mock_domain/oauth/token'",
        request=httpx.Request("POST", "https://mock_domain/oauth/token"),
        response=mock_httpx_async_client_post.return_value
    )

    response = client.post(
        "/api/v1/auth/login",
        json={"email": "wrong@example.com", "password": "WrongPassword!"}
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password."
    mock_httpx_async_client_post.assert_called_once()

# Test login with an internal Auth0 error (e.g., misconfiguration, 500 status)
@pytest.mark.asyncio
async def test_login_auth0_internal_error(mock_external_services_and_singletons, mock_httpx_async_client_post):
    mock_auth0_create_method, mock_resend_emails_send = mock_external_services_and_singletons

    # Setup mock_httpx_async_client_post for an internal server error from Auth0
    mock_httpx_async_client_post.return_value = MagicMock(status_code=500)
    mock_httpx_async_client_post.return_value.json.return_value = {"error": "internal_error", "error_description": "Something went wrong at Auth0."}
    mock_httpx_async_client_post.return_value.raise_for_status.side_effect = httpx.HTTPStatusError(
        "Server error '500 Internal Server Error' for url 'https://mock_domain/oauth/token'",
        request=httpx.Request("POST", "https://mock_domain/oauth/token"),
        response=mock_httpx_async_client_post.return_value
    )

    response = client.post(
        "/api/v1/auth/login",
        json={"email": "internal@example.com", "password": "Password123!"}
    )

    assert response.status_code == 500
    assert "Auth0 login error" in response.json()["detail"]
    mock_httpx_async_client_post.assert_called_once()
# Helper to re-instantiate AuthService for tests needing specific envs
# This helper is now simpler as it only sets env and returns
# This helper is used by specific tests to setup env vars
def _reinstantiate_auth_service_with_env(env_vars):
    # Store original env vars
    original_env = os.environ.copy()

    # Set new env vars
    os.environ.clear()
    os.environ.update(env_vars)
    # Ensure all Auth0 env vars are present, even if dummy
    os.environ.setdefault("AUTH0_DOMAIN", "dummy_domain")
    os.environ.setdefault("AUTH0_MANAGEMENT_CLIENT_ID", "dummy_client_id")
    os.environ.setdefault("AUTH0_MANAGEMENT_CLIENT_SECRET", "dummy_client_secret")
    os.environ.setdefault("AUTH0_CLIENT_ID", "dummy_client_id")
    os.environ.setdefault("AUTH0_CLIENT_SECRET", "dummy_client_secret")
    os.environ.setdefault("AUTH0_API_AUDIENCE", "dummy_audience")

    # Re-initialize singletons for this specific test with the desired envs
    # Note: Their __init__ will run and potentially raise ValueError
    # if env_vars don't meet their requirements.
    auth_service.auth_service = auth_service.AuthService()
    backend.app.services.email_service.email_service = backend.app.services.email_service.EmailService()

    # Restore original env vars
    os.environ.clear()
    os.environ.update(original_env)


def test_health_check():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

# Test successful registration
def test_register_user_success(mock_external_services_and_singletons, db_session: Session):
    mock_auth0_create_method, mock_resend_emails_send = mock_external_services_and_singletons
    
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
    
    mock_auth0_create_method.assert_called_once()
    mock_resend_emails_send.assert_called_once()
    assert mock_resend_emails_send.call_args.args[0]["to"] == "test@example.com"
    assert "http://localhost:3000/verify-email" in mock_resend_emails_send.call_args.args[0]["html"]

# Test duplicate email registration
def test_register_user_duplicate_email(mock_external_services_and_singletons, db_session: Session):
    mock_auth0_create_method, mock_resend_emails_send = mock_external_services_and_singletons
    
    # First successful registration
    client.post(
        "/api/v1/auth/register",
        json={"email": "test_duplicate@example.com", "password": "Password123!"}
    )
    mock_auth0_create_method.assert_called_once() 
    mock_auth0_create_method.reset_mock()
    
    # Mock Auth0 to raise "user already exists" for the second attempt
    mock_auth0_create_method.side_effect = Exception("The user already exists.")

    # Attempt to register with duplicate email
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "test_duplicate@example.com", "password": "AnotherPassword!"}
    )
    assert response.status_code == 409
    assert response.json()["detail"] == "User with this email already exists" 
    mock_auth0_create_method.assert_not_called() # Correct assertion: should not be called for duplicate


# Test successful email verification
def test_verify_email_success(mock_external_services_and_singletons, db_session: Session):
    mock_auth0_create_method, mock_resend_emails_send = mock_external_services_and_singletons

    # First, register a user
    register_response = client.post(
        "/api/v1/auth/register",
        json={"email": "verify@example.com", "password": "Password123!"}
    )
    assert register_response.status_code == 201
    mock_resend_emails_send.assert_called_once() 

    # Now, verify the email
    verify_response = client.post(
        "/api/v1/auth/verify-email",
        json={"email": "verify@example.com", "token": "mock_verification_token"}
    )
    assert verify_response.status_code == 200
    assert verify_response.json() == {"message": "Email verified successfully."}
    
    user = db_session.query(backend.app.models.user.User).filter(backend.app.models.user.User.email == "verify@example.com").first()
    assert user is not None
    assert user.is_verified == True

# Test verification with invalid token
def test_verify_email_invalid_token(db_session: Session):
    # This test directly creates the user in the database
    _reinstantiate_auth_service_with_env({ # Need to ensure singletons are properly initialized for this test
        "AUTH0_DOMAIN": "mock_domain",
        "AUTH0_MANAGEMENT_CLIENT_ID": "mock_client_id",
        "AUTH0_MANAGEMENT_CLIENT_SECRET": "mock_client_secret",
        "RESEND_API_KEY": "mock_resend_key",
        "NEXT_PUBLIC_EMAIL_VERIFICATION_URL": "http://localhost:3000"
    })
    
    user = backend.app.models.user.User(auth_provider_id="auth0|test", email="invalidtoken@example.com", is_verified=False)
    db_session.add(user)
    db_session.commit()

    response = client.post(
        "/api/v1/auth/verify-email",
        json={"email": "invalidtoken@example.com", "token": ""} # Empty token should fail
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Verification token is missing"


# Test user not found during verification
def test_verify_email_user_not_found(db_session: Session):
    response = client.post(
        "/api/v1/auth/verify-email",
        json={"email": "nonexistent@example.com", "token": "any_token"}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"

# Test re-verification of already verified email
def test_verify_email_already_verified(mock_external_services_and_singletons, db_session: Session):
    mock_auth0_create_method, mock_resend_emails_send = mock_external_services_and_singletons
    
    # First, register and verify a user
    client.post(
        "/api/v1/auth/register",
        json={"email": "alreadyverified@example.com", "password": "Password123!"}
    )

    token = "mock_verification_token"
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

# Test accessing protected route without token
def test_protected_route_unauthenticated():
    response = client.get("/api/v1/protected")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

# Test successful login and access to protected route
@pytest.mark.asyncio
async def test_login_and_access_protected_route(mock_external_services_and_singletons, db_session: Session, mock_httpx_async_client_post):
    mock_auth0_create_method, mock_resend_emails_send = mock_external_services_and_singletons

    # Setup mock_httpx_async_client_post for successful login
    mock_response = MagicMock(status_code=200)
    mock_response.json = AsyncMock(return_value={
        "access_token": "mock_jwt_token_for_protected_route",
        "expires_in": 3600,
        "token_type": "Bearer"
    })
    mock_response.raise_for_status.return_value = None
    mock_httpx_async_client_post.return_value = mock_response

    # Register a user first to ensure local user exists or simulate creation
    client.post(
        "/api/v1/auth/register",
        json={"email": "protected_test@example.com", "password": "Password123!"}
    )

    # Perform login
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "protected_test@example.com", "password": "Password123!"}
    )
    assert login_response.status_code == 200
    access_token = login_response.json()["access_token"]

    # Access protected route with the obtained token
    protected_response = client.get(
        "/api/v1/protected",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert protected_response.status_code == 200
    assert "Hello" in protected_response.json()["message"]
    assert "mock_jwt_token_for_protected_route" in protected_response.json()["message"]

# Test Auth0 initialization failure scenario (due to missing env vars)
def test_auth_service_init_missing_env_vars():
    # Store original env vars
    original_env = os.environ.copy()
    
    # Clear Auth0 env vars
    for key in ["AUTH0_DOMAIN", "AUTH0_MANAGEMENT_CLIENT_ID", "AUTH0_MANAGEMENT_CLIENT_SECRET"]:
        os.environ.pop(key, None)
    
    # Set dummy for RESEND and NEXT_PUBLIC_EMAIL_VERIFICATION_URL to allow EmailService to initialize
    os.environ["RESEND_API_KEY"] = "dummy_key"
    os.environ["NEXT_PUBLIC_EMAIL_VERIFICATION_URL"] = "http://localhost:3000"


    # Assert that AuthService initialization raises a ValueError
    with pytest.raises(ValueError, match="CRITICAL: All required Auth0 environment variables"):
        # Create a fresh instance of AuthService for this test
        auth_service.AuthService() # Call the constructor directly

    # Restore original env vars
    os.environ.clear()
    os.environ.update(original_env)

# Test EmailService initialization failure scenario (due to missing env vars)
def test_email_service_init_missing_env_vars():
    # Store original env var
    original_env = os.environ.copy()

    # Clear Resend env var
    os.environ.pop("RESEND_API_KEY", None)

    # Set dummy for Auth0 env vars to allow AuthService to initialize
    os.environ["AUTH0_DOMAIN"] = "dummy_domain"
    os.environ["AUTH0_MANAGEMENT_CLIENT_ID"] = "dummy_client_id"
    os.environ["AUTH0_MANAGEMENT_CLIENT_SECRET"] = "dummy_client_secret"
    os.environ["NEXT_PUBLIC_EMAIL_VERIFICATION_URL"] = "http://localhost:3000"


    # Assert that EmailService initialization raises a ValueError
    with pytest.raises(ValueError, match="CRITICAL: RESEND_API_KEY environment variable"):
        # Create a fresh instance of EmailService for this test
        backend.app.services.email_service.EmailService() # Call the constructor directly

    # Restore original env var
    os.environ.clear()
    os.environ.update(original_env)
