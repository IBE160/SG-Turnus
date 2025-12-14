import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.orm import Session
from backend.app.core.auth_service import AuthService, IncorrectLoginCredentialsException
from backend.app.models.user import User
import os
import httpx
from fastapi import HTTPException # Added HTTPException import

# Fixture to mock environment variables for AuthService initialization
@pytest.fixture(autouse=True)
def mock_env_vars():
    original_env = os.environ.copy()
    os.environ["AUTH0_DOMAIN"] = "mock_domain"
    os.environ["AUTH0_MANAGEMENT_CLIENT_ID"] = "mock_client_id"
    os.environ["AUTH0_MANAGEMENT_CLIENT_SECRET"] = "mock_client_secret"
    os.environ["AUTH0_CLIENT_ID"] = "mock_auth_client_id"
    os.environ["AUTH0_CLIENT_SECRET"] = "mock_auth_client_secret"
    os.environ["AUTH0_API_AUDIENCE"] = "https://mockapi.example.com"
    os.environ["RESEND_API_KEY"] = "mock_resend_key" # Required by EmailService
    os.environ["NEXT_PUBLIC_EMAIL_VERIFICATION_URL"] = "http://localhost:3000"
    yield
    os.environ.clear()
    os.environ.update(original_env)

# Fixture to mock the Auth0 management client
@pytest.fixture
def mock_auth0_management_client():
    with patch('backend.app.core.auth_service.Auth0') as MockAuth0Class:
        mock_instance = MagicMock()
        mock_instance.users.create.return_value = {"user_id": "auth0|mock_user_id"}
        MockAuth0Class.return_value = mock_instance
        yield mock_instance

# Fixture to mock httpx.AsyncClient.post
@pytest.fixture
def mock_httpx_post():
    with patch('httpx.AsyncClient.post', new_callable=AsyncMock) as mock_post:
        yield mock_post

# Fixture for a mock database session
@pytest.fixture
def mock_db_session():
    mock_session = MagicMock(spec=Session)
    # Mock the query method and its filter/first calls
    mock_session.query.return_value.filter.return_value.first.return_value = None
    yield mock_session

@pytest.mark.asyncio
async def test_login_success_existing_local_user(mock_env_vars, mock_auth0_management_client, mock_httpx_post, mock_db_session):
    auth_service_instance = AuthService()
    # Mock Auth0 response for successful login
    mock_response = MagicMock(status_code=200)
    mock_response.json = AsyncMock(return_value={"access_token": "auth0_token_xyz", "token_type": "Bearer"})
    mock_response.raise_for_status.side_effect = None
    mock_httpx_post.return_value = mock_response

    email = "existing_user@example.com"
    password = "SecurePassword123!"
    # Mock local DB to return an existing user
    mock_db_session.query.return_value.filter.return_value.first.return_value = User(
        auth_provider_id="auth0|existing_id", email=email, is_verified=True
    )

    result = await auth_service_instance.login(email, password, mock_db_session)

    mock_httpx_post.assert_awaited_once_with(
        f"https://{os.getenv('AUTH0_DOMAIN')}/oauth/token",
        json={
            "grant_type": "password",
            "username": email,
            "password": password,
            "audience": os.getenv("AUTH0_API_AUDIENCE"),
            "client_id": os.getenv("AUTH0_CLIENT_ID"),
            "client_secret": os.getenv("AUTH0_CLIENT_SECRET")
        },
        headers={"Content-Type": "application/json"}
    )
    assert result == {"access_token": "auth0_token_xyz", "token_type": "Bearer"}
    # Ensure no new user was added to DB if already exists
    mock_db_session.add.assert_not_called()
    mock_db_session.commit.assert_not_called()

@pytest.mark.asyncio
async def test_login_success_new_local_user(mock_env_vars, mock_auth0_management_client, mock_httpx_post, mock_db_session):
    auth_service_instance = AuthService()
    email = "new_user@example.com"
    password = "SecurePassword123!"

    # Mock Auth0 response for successful login
    mock_response = MagicMock(status_code=200)
    mock_response.json = AsyncMock(return_value={"access_token": "auth0_token_xyz", "token_type": "Bearer"})
    mock_response.raise_for_status.side_effect = None
    mock_httpx_post.return_value = mock_response

    # Mock local DB to NOT return an existing user
    mock_db_session.query.return_value.filter.return_value.first.return_value = None
    # Mock add and commit methods
    mock_db_session.add.return_value = None
    mock_db_session.commit.return_value = None
    mock_db_session.refresh.return_value = None


    result = await auth_service_instance.login(email, password, mock_db_session)

    mock_httpx_post.assert_awaited_once()
    assert result == {"access_token": "auth0_token_xyz", "token_type": "Bearer"}
    # Ensure new user was added to DB
    mock_db_session.add.assert_called_once()
    mock_db_session.commit.assert_called_once()
    mock_db_session.refresh.assert_called_once()


@pytest.mark.asyncio
async def test_login_incorrect_credentials(mock_env_vars, mock_auth0_management_client, mock_httpx_post, mock_db_session):
    auth_service_instance = AuthService()
    email = "invalid@example.com"
    password = "WrongPassword!"

    # Set mock_httpx_post to raise HTTPStatusError directly
    mock_response = MagicMock(status_code=403, text='{"error": "access_denied", "error_description": "Wrong email or password."}')
    mock_response.json = AsyncMock(return_value={"error": "access_denied", "error_description": "Wrong email or password."})
    mock_httpx_post.side_effect = httpx.HTTPStatusError(
        "Client error '403 Forbidden'",
        request=httpx.Request("POST", "http://test.com"),
        response=mock_response
    )

    with pytest.raises(IncorrectLoginCredentialsException, match="Incorrect email or password."):
        await auth_service_instance.login(email, password, mock_db_session)

    mock_httpx_post.assert_awaited_once()

@pytest.mark.asyncio
async def test_login_auth0_internal_error(mock_env_vars, mock_auth0_management_client, mock_httpx_post, mock_db_session):
    auth_service_instance = AuthService()
    email = "error@example.com"
    password = "Password123!"

    # Set mock_httpx_post to raise HTTPStatusError directly
    mock_response = MagicMock(status_code=500, text='{"error": "internal_error", "error_description": "Something went wrong."}')
    mock_response.json = AsyncMock(return_value={"error": "internal_error", "error_description": "Something went wrong."})
    mock_httpx_post.side_effect = httpx.HTTPStatusError(
        "Server error '500 Internal Server Error'",
        request=httpx.Request("POST", "http://test.com"),
        response=mock_response
    )

    with pytest.raises(HTTPException) as excinfo:
        await auth_service_instance.login(email, password, mock_db_session)
    assert excinfo.value.status_code == 500
    assert "Auth0 login error" in excinfo.value.detail
    
    mock_httpx_post.assert_awaited_once()

@pytest.mark.asyncio
async def test_login_missing_access_token_in_response(mock_env_vars, mock_auth0_management_client, mock_httpx_post, mock_db_session):
    auth_service_instance = AuthService()
    email = "no_token@example.com"
    password = "Password123!"

    # Setup mock response for httpx.post that doesn't include access_token
    mock_response = MagicMock(status_code=200)
    mock_response.json = AsyncMock(return_value={"expires_in": 3600, "token_type": "Bearer"})
    mock_response.raise_for_status.side_effect = None
    mock_httpx_post.return_value = mock_response

    from fastapi import HTTPException
    with pytest.raises(HTTPException) as excinfo:
        await auth_service_instance.login(email, password, mock_db_session)
    assert excinfo.value.status_code == 401
    assert "Auth0 did not return an access token." in excinfo.value.detail
    
    mock_httpx_post.assert_awaited_once()