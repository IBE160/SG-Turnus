import httpx # Import httpx for httpx.HTTPStatusError
import os
import re
import importlib # Added for module reloading
from unittest.mock import patch, AsyncMock, MagicMock
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from backend.main import app
from backend.app.core import auth_service
import backend.app.models.user
import backend.app.services.email_service # Import the module to access EmailService class
from backend.app.core import jwt_utils # Import jwt_utils

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

@pytest.fixture(scope="function")
def test_client(db_session):
    # Patch the application's database engine, session, and create_db_and_tables for testing
    with patch('backend.app.database.engine', new=test_engine), \
         patch('backend.app.database.SessionLocal', new=TestingSessionLocal), \
         patch('backend.app.database.create_db_and_tables', new=MagicMock()): # Mock create_db_and_tables to do nothing
        # Use the db_session fixture to ensure clean tables for each test
        # and override the get_db dependency for the FastAPI app
        app.dependency_overrides[backend.app.database.get_db] = override_get_db
        with TestClient(app) as client:
            yield client
        # Clean up dependency override after the test
        app.dependency_overrides.clear()

# ----------------------------------------------------
# Fixtures and Test Functions
# ----------------------------------------------------

@pytest.fixture(autouse=True)
def mock_external_services_and_singletons():
    """
    Mocks Auth0 and Resend clients and sets up dummy environment variables for tests.
    It patches the global singleton instances of AuthService and EmailService directly.
    """
    original_env = os.environ.copy() # Store original env vars

    # Set dummy environment variables for jwt_utils and general config
    os.environ["AUTH0_DOMAIN"] = "mock_domain"
    os.environ["AUTH0_AUDIENCE"] = "mock_audience"
    os.environ["AUTH0_ISSUER"] = "https://mock_domain/"
    os.environ["AUTH0_MANAGEMENT_CLIENT_ID"] = "mock_client_id"
    os.environ["AUTH0_MANAGEMENT_CLIENT_SECRET"] = "mock_client_secret"
    os.environ["RESEND_API_KEY"] = "mock_resend_key"
    os.environ["NEXT_PUBLIC_EMAIL_VERIFICATION_URL"] = "http://localhost:3000"
    os.environ["AUTH0_CLIENT_ID"] = "mock_auth_client_id"
    os.environ["AUTH0_CLIENT_SECRET"] = "mock_auth_client_secret"
    os.environ["AUTH0_API_AUDIENCE"] = "https://mockapi.example.com"
    os.environ["E2E_TEST_MODE"] = "true"
    # S3 Environment Variables
    os.environ["S3_BUCKET_NAME"] = "test-bucket"
    os.environ["AWS_ACCESS_KEY_ID"] = "test-access-key"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "test-secret-key"
    os.environ["AWS_REGION"] = "us-east-1"


    # Reload modules to pick up new environment variables
    importlib.reload(backend.app.core.auth_service)
    importlib.reload(backend.app.services.email_service)
    importlib.reload(backend.app.services.storage_service) # Reload storage_service
    importlib.reload(backend.app.database)

    mock_auth_service_instance = MagicMock()
    mock_auth_service_instance._auth0_configured = True # Crucial: Indicate configured
    mock_email_service_instance = MagicMock()
    mock_email_service_instance._resend_configured = True # Crucial: Indicate configured
    mock_storage_service_instance = MagicMock()
    mock_storage_service_instance.s3_client = MagicMock() # Ensure s3_client is mocked by default

    # Reload modules to pick up new environment variables again, after setting mocks if needed
    importlib.reload(backend.app.core.auth_service)
    importlib.reload(backend.app.services.email_service)
    importlib.reload(backend.app.services.storage_service) # Reload storage_service


    with patch('backend.app.core.auth_service.auth_service', new=mock_auth_service_instance), \
         patch('backend.app.services.email_service.email_service', new=mock_email_service_instance), \
         patch('backend.app.services.storage_service.storage_service', new=mock_storage_service_instance), \
         patch('backend.app.dependencies.validate_token', new_callable=AsyncMock) as mock_validate_token, \
         patch('backend.app.core.jwt_utils.get_jwks', new_callable=AsyncMock) as mock_get_jwks:

        # Configure mock_auth_service_instance methods
        mock_auth_service_instance.register_user.return_value = {"user_id": f"auth0|mock_id_{os.urandom(8).hex()}", "email": "test@example.com"}
        mock_auth_service_instance.login.return_value = {"access_token": "mock_jwt_token", "token_type": "Bearer"}
        mock_auth_service_instance.verify_email.return_value = True

        # Configure mock_auth_service_instance's internal Auth0 client
        mock_auth0_internal_client = MagicMock()
        mock_auth_service_instance._auth0 = mock_auth0_internal_client # Set the internal Auth0 mock
        mock_auth0_internal_client.users.create.return_value = {"user_id": f"auth0|mock_id_{os.urandom(8).hex()}"}
        
        # Configure mock_email_service_instance's send_verification_email
        mock_email_service_instance.send_verification_email.return_value = {"id": "resend_mock_id_123"}
        
        # Configure mock_validate_token to return a valid payload by default
        mock_validate_token.return_value = {"sub": "auth0|mockuser123", "email": "test@example.example.com", "is_verified": True} # Ensure is_verified is True for authenticated calls

        # Configure mock_get_jwks to return a dummy JWKS structure
        mock_get_jwks.return_value = {
            "keys": [
                {"alg": "RS256", "kty": "RSA", "use": "sig", "x5c": ["mock_cert"], "n": "mock_n", "e": "mock_e", "kid": "mock_kid"}
            ]
        }
        
        # Configure mock_storage_service_instance methods
        mock_storage_service_instance.upload_file.return_value = True
        mock_storage_service_instance.download_file.return_value = b"mock file content"
        mock_storage_service_instance.delete_file.return_value = True
        mock_storage_service_instance.s3_client = MagicMock() # Ensure s3_client is set up

        # Yield the mocks needed by tests
        yield mock_auth_service_instance, mock_email_service_instance, mock_validate_token, mock_get_jwks, mock_storage_service_instance
        
    os.environ.clear() # Clear all environment variables set during test
    os.environ.update(original_env)


# Test login endpoint
@pytest.fixture(autouse=True)
def mock_httpx_async_client_post():
    with patch('httpx.AsyncClient.post', new_callable=AsyncMock) as mock_post:
        yield mock_post

# Test successful login
@pytest.mark.asyncio
async def test_login_success(mock_external_services_and_singletons, db_session: Session, mock_httpx_async_client_post, test_client):
    mock_auth0_create_method, mock_resend_emails_send, mock_validate_token, mock_get_jwks = mock_external_services_and_singletons

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
    test_client.post(
        "/api/v1/auth/register",
        json={"email": "login_test@example.com", "password": "Password123!"}
    )

    response = test_client.post(
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
async def test_login_incorrect_credentials(mock_external_services_and_singletons, mock_httpx_async_client_post, test_client):
    mock_auth0_create_method, mock_resend_emails_send, mock_validate_token, mock_get_jwks = mock_external_services_and_singletons

    # Setup mock_httpx_async_client_post for incorrect credentials (Auth0 returns 403 Forbidden)
    mock_httpx_async_client_post.return_value = MagicMock(status_code=403)
    mock_httpx_async_client_post.return_value.json.return_value = {"error": "access_denied", "error_description": "Wrong email or password."}
    mock_httpx_async_client_post.return_value.raise_for_status.side_effect = httpx.HTTPStatusError(
        "Client error '403 Forbidden' for url 'https://mock_domain/oauth/token'",
        request=httpx.Request("POST", "https://mock_domain/oauth/token"),
        response=mock_httpx_async_client_post.return_value
    )

    response = test_client.post(
        "/api/v1/auth/login",
        json={"email": "wrong@example.com", "password": "Password123!"}
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password."
    mock_httpx_async_client_post.assert_called_once()

# Test login with an internal Auth0 error (e.g., misconfiguration, 500 status)
@pytest.mark.asyncio
async def test_login_auth0_internal_error(mock_external_services_and_singletons, mock_httpx_async_client_post, test_client):
    mock_auth0_create_method, mock_resend_emails_send, mock_validate_token, mock_get_jwks = mock_external_services_and_singletons

    # Setup mock_httpx_async_client_post for an internal server error from Auth0
    mock_httpx_async_client_post.return_value = MagicMock(status_code=500)
    mock_httpx_async_client_post.return_value.json.return_value = {"error": "internal_error", "error_description": "Something went wrong at Auth0."}
    mock_httpx_async_client_post.return_value.raise_for_status.side_effect = httpx.HTTPStatusError(
        "Server error '500 Internal Server Error' for url 'https://mock_domain/oauth/token'",
        request=httpx.Request("POST", "https://mock_domain/oauth/token"),
        response=mock_httpx_async_client_post.return_value
    )

    response = test_client.post(
        "/api/v1/auth/login",
        json={"email": "internal@example.com", "password": "Password123!"}
    )

    assert response.status_code == 500
    assert "Auth0 login error" in response.json()["detail"]
    mock_httpx_async_client_post.assert_called_once()    # Restore original env var
    os.environ.clear()
    os.environ.update(original_env)


# ----------------------------------------------------
# User Content API Tests
# ----------------------------------------------------

@pytest.mark.asyncio
async def test_upload_file_success(mock_external_services_and_singletons, db_session: Session, test_client):
    mock_auth_service, mock_email_service, mock_validate_token, mock_get_jwks, mock_storage_service = mock_external_services_and_singletons

    # Authenticate a user
    user_email = "upload_test@example.com"
    user_password = "Password123!"
    test_client.post("/api/v1/auth/register", json={"email": user_email, "password": user_password})
    login_response = test_client.post("/api/v1/auth/login", json={"email": user_email, "password": user_password})
    access_token = login_response.json()["access_token"]
    
    # Mock the current user in dependencies
    mock_validate_token.return_value = {"sub": "auth0|mockuser123", "email": user_email, "is_verified": True}
    current_user_db = db_session.query(backend.app.models.user.User).filter(backend.app.models.user.User.email == user_email).first()
    mock_validate_token.return_value = {"sub": current_user_db.auth_provider_id, "email": current_user_db.email, "is_verified": current_user_db.is_verified}


    file_content = b"This is a test file for upload."
    file_name = "test_document.txt"
    
    response = test_client.post(
        "/api/v1/user-content/upload",
        headers={"Authorization": f"Bearer {access_token}"},
        files={"file": (file_name, file_content, "text/plain")}
    )

    assert response.status_code == 200
    assert response.json()["message"] == "File uploaded successfully"
    assert "file_id" in response.json()
    assert response.json()["filename"] == file_name
    assert "s3_key" in response.json()

    mock_storage_service.upload_file.assert_called_once()
    args, kwargs = mock_storage_service.upload_file.call_args
    assert args[0] == file_content
    assert re.match(r"users/\d+/[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\.txt", args[1]) # Check object_name format
    assert kwargs['content_type'] == "text/plain"

    study_material = db_session.query(backend.app.models.study_material.StudyMaterial).filter_by(id=response.json()["file_id"]).first()
    assert study_material is not None
    assert study_material.user_id == current_user_db.id
    assert study_material.file_name == file_name
    assert study_material.s3_key == response.json()["s3_key"]
    assert study_material.processing_status == "uploaded"

@pytest.mark.asyncio
async def test_upload_file_unauthenticated(test_client):
    file_content = b"This is a test file for upload."
    file_name = "test_document.txt"
    response = test_client.post(
        "/api/v1/user-content/upload",
        files={"file": (file_name, file_content, "text/plain")}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

@pytest.mark.asyncio
async def test_download_file_success(mock_external_services_and_singletons, db_session: Session, test_client):
    mock_auth_service, mock_email_service, mock_validate_token, mock_get_jwks, mock_storage_service = mock_external_services_and_singletons

    # Authenticate a user
    user_email = "download_test@example.com"
    user_password = "Password123!"
    test_client.post("/api/v1/auth/register", json={"email": user_email, "password": user_password})
    login_response = test_client.post("/api/v1/auth/login", json={"email": user_email, "password": user_password})
    access_token = login_response.json()["access_token"]
    
    current_user_db = db_session.query(backend.app.models.user.User).filter(backend.app.models.user.User.email == user_email).first()
    mock_validate_token.return_value = {"sub": current_user_db.auth_provider_id, "email": current_user_db.email, "is_verified": current_user_db.is_verified}

    # Manually create a StudyMaterial entry for download
    s3_object_name = f"users/{current_user_db.id}/download_test.txt"
    study_material = backend.app.models.study_material.StudyMaterial(
        user_id=current_user_db.id,
        file_name="download_document.txt",
        s3_key=s3_object_name,
        processing_status="completed"
    )
    db_session.add(study_material)
    db_session.commit()
    db_session.refresh(study_material)

    mock_storage_service.download_file.return_value = b"Downloaded content from S3"

    response = test_client.get(
        f"/api/v1/user-content/download/{study_material.id}",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == 200
    assert response.content == b"Downloaded content from S3"
    mock_storage_service.download_file.assert_called_once_with(s3_object_name)

@pytest.mark.asyncio
async def test_download_file_not_found_db(mock_external_services_and_singletons, db_session: Session, test_client):
    mock_auth_service, mock_email_service, mock_validate_token, mock_get_jwks, mock_storage_service = mock_external_services_and_singletons
    
    # Authenticate a user
    user_email = "download_notfound_test@example.com"
    user_password = "Password123!"
    test_client.post("/api/v1/auth/register", json={"email": user_email, "password": user_password})
    login_response = test_client.post("/api/v1/auth/login", json={"email": user_email, "password": user_password})
    access_token = login_response.json()["access_token"]
    
    current_user_db = db_session.query(backend.app.models.user.User).filter(backend.app.models.user.User.email == user_email).first()
    mock_validate_token.return_value = {"sub": current_user_db.auth_provider_id, "email": current_user_db.email, "is_verified": current_user_db.is_verified}


    response = test_client.get(
        "/api/v1/user-content/download/99999", # Non-existent ID
        headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "File not found or not owned by user"
    mock_storage_service.download_file.assert_not_called()

@pytest.mark.asyncio
async def test_download_file_not_found_s3(mock_external_services_and_singletons, db_session: Session, test_client):
    mock_auth_service, mock_email_service, mock_validate_token, mock_get_jwks, mock_storage_service = mock_external_services_and_singletons

    # Authenticate a user
    user_email = "download_s3_notfound_test@example.com"
    user_password = "Password123!"
    test_client.post("/api/v1/auth/register", json={"email": user_email, "password": user_password})
    login_response = test_client.post("/api/v1/auth/login", json={"email": user_email, "password": user_password})
    access_token = login_response.json()["access_token"]
    
    current_user_db = db_session.query(backend.app.models.user.User).filter(backend.app.models.user.User.email == user_email).first()
    mock_validate_token.return_value = {"sub": current_user_db.auth_provider_id, "email": current_user_db.email, "is_verified": current_user_db.is_verified}


    # Manually create a StudyMaterial entry
    s3_object_name = f"users/{current_user_db.id}/download_s3_notfound.txt"
    study_material = backend.app.models.study_material.StudyMaterial(
        user_id=current_user_db.id,
        file_name="s3_notfound_document.txt",
        s3_key=s3_object_name,
        processing_status="completed"
    )
    db_session.add(study_material)
    db_session.commit()
    db_session.refresh(study_material)

    mock_storage_service.download_file.return_value = None # Simulate file not found in S3

    response = test_client.get(
        f"/api/v1/user-content/download/{study_material.id}",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "File content not found in storage"
    mock_storage_service.download_file.assert_called_once_with(s3_object_name)

@pytest.mark.asyncio
async def test_download_file_unauthorized(mock_external_services_and_singletons, db_session: Session, test_client):
    mock_auth_service, mock_email_service, mock_validate_token, mock_get_jwks, mock_storage_service = mock_external_services_and_singletons

    # User 1 registers and uploads a file
    user1_email = "user1@example.com"
    user1_password = "Password123!"
    test_client.post("/api/v1/auth/register", json={"email": user1_email, "password": user1_password})
    login_response1 = test_client.post("/api/v1/auth/login", json={"email": user1_email, "password": user1_password})
    access_token1 = login_response1.json()["access_token"]
    
    user1_db = db_session.query(backend.app.models.user.User).filter(backend.app.models.user.User.email == user1_email).first()
    mock_validate_token.return_value = {"sub": user1_db.auth_provider_id, "email": user1_db.email, "is_verified": user1_db.is_verified}


    upload_response = test_client.post(
        "/api/v1/user-content/upload",
        headers={"Authorization": f"Bearer {access_token1}"},
        files={"file": ("user1_doc.txt", b"user1 content", "text/plain")}
    )
    assert upload_response.status_code == 200
    file_id_user1 = upload_response.json()["file_id"]

    # User 2 registers
    user2_email = "user2@example.com"
    user2_password = "Password123!"
    test_client.post("/api/v1/auth/register", json={"email": user2_email, "password": user2_password})
    login_response2 = test_client.post("/api/v1/auth/login", json={"email": user2_email, "password": user2_password})
    access_token2 = login_response2.json()["access_token"]

    user2_db = db_session.query(backend.app.models.user.User).filter(backend.app.models.user.User.email == user2_email).first()
    mock_validate_token.return_value = {"sub": user2_db.auth_provider_id, "email": user2_db.email, "is_verified": user2_db.is_verified}


    # User 2 tries to download User 1's file
    response = test_client.get(
        f"/api/v1/user-content/download/{file_id_user1}",
        headers={"Authorization": f"Bearer {access_token2}"}
    )

    assert response.status_code == 404 # Should be 404 because not found for user2
    assert response.json()["detail"] == "File not found or not owned by user"
    mock_storage_service.download_file.assert_not_called()

@pytest.mark.asyncio
async def test_delete_file_success(mock_external_services_and_singletons, db_session: Session, test_client):
    mock_auth_service, mock_email_service, mock_validate_token, mock_get_jwks, mock_storage_service = mock_external_services_and_singletons

    # Authenticate a user
    user_email = "delete_test@example.com"
    user_password = "Password123!"
    test_client.post("/api/v1/auth/register", json={"email": user_email, "password": user_password})
    login_response = test_client.post("/api/v1/auth/login", json={"email": user_email, "password": user_password})
    access_token = login_response.json()["access_token"]

    current_user_db = db_session.query(backend.app.models.user.User).filter(backend.app.models.user.User.email == user_email).first()
    mock_validate_token.return_value = {"sub": current_user_db.auth_provider_id, "email": current_user_db.email, "is_verified": current_user_db.is_verified}


    # Upload a file first
    upload_response = test_client.post(
        "/api/v1/user-content/upload",
        headers={"Authorization": f"Bearer {access_token}"},
        files={"file": ("delete_doc.txt", b"content to delete", "text/plain")}
    )
    assert upload_response.status_code == 200
    file_id_to_delete = upload_response.json()["file_id"]
    s3_key_to_delete = upload_response.json()["s3_key"]

    response = test_client.delete(
        f"/api/v1/user-content/delete/{file_id_to_delete}",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == 200
    assert response.json()["message"] == "File deleted successfully"
    mock_storage_service.delete_file.assert_called_once_with(s3_key_to_delete)

    # Verify deleted from DB
    deleted_material = db_session.query(backend.app.models.study_material.StudyMaterial).filter_by(id=file_id_to_delete).first()
    assert deleted_material is None

@pytest.mark.asyncio
async def test_delete_file_unauthorized(mock_external_services_and_singletons, db_session: Session, test_client):
    mock_auth_service, mock_email_service, mock_validate_token, mock_get_jwks, mock_storage_service = mock_external_services_and_singletons

    # User 1 registers and uploads a file
    user1_email = "delete_user1@example.com"
    user1_password = "Password123!"
    test_client.post("/api/v1/auth/register", json={"email": user1_email, "password": user1_password})
    login_response1 = test_client.post("/api/v1/auth/login", json={"email": user1_email, "password": user1_password})
    access_token1 = login_response1.json()["access_token"]

    user1_db = db_session.query(backend.app.models.user.User).filter(backend.app.models.user.User.email == user1_email).first()
    mock_validate_token.return_value = {"sub": user1_db.auth_provider_id, "email": user1_db.email, "is_verified": user1_db.is_verified}


    upload_response = test_client.post(
        "/api/v1/user-content/upload",
        headers={"Authorization": f"Bearer {access_token1}"},
        files={"file": ("user1_delete_doc.txt", b"user1 content", "text/plain")}
    )
    assert upload_response.status_code == 200
    file_id_user1 = upload_response.json()["file_id"]

    # User 2 registers
    user2_email = "delete_user2@example.com"
    user2_password = "Password123!"
    test_client.post("/api/v1/auth/register", json={"email": user2_email, "password": user2_password})
    login_response2 = test_client.post("/api/v1/auth/login", json={"email": user2_email, "password": user2_password})
    access_token2 = login_response2.json()["access_token"]
    
    user2_db = db_session.query(backend.app.models.user.User).filter(backend.app.models.user.User.email == user2_email).first()
    mock_validate_token.return_value = {"sub": user2_db.auth_provider_id, "email": user2_db.email, "is_verified": user2_db.is_verified}


    # User 2 tries to delete User 1's file
    response = test_client.delete(
        f"/api/v1/user-content/delete/{file_id_user1}",
        headers={"Authorization": f"Bearer {access_token2}"}
    )

    assert response.status_code == 404 # Should be 404 because not found for user2
    assert response.json()["detail"] == "File not found or not owned by user"
    mock_storage_service.delete_file.assert_not_called()

@pytest.mark.asyncio
async def test_list_files_success(mock_external_services_and_singletons, db_session: Session, test_client):
    mock_auth_service, mock_email_service, mock_validate_token, mock_get_jwks, mock_storage_service = mock_external_services_and_singletons

    # Authenticate a user
    user_email = "list_test@example.com"
    user_password = "Password123!"
    test_client.post("/api/v1/auth/register", json={"email": user_email, "password": user_password})
    login_response = test_client.post("/api/v1/auth/login", json={"email": user_email, "password": user_password})
    access_token = login_response.json()["access_token"]

    current_user_db = db_session.query(backend.app.models.user.User).filter(backend.app.models.user.User.email == user_email).first()
    mock_validate_token.return_value = {"sub": current_user_db.auth_provider_id, "email": current_user_db.email, "is_verified": current_user_db.is_verified}


    # Upload two files for the user
    file1_name = "list_doc1.txt"
    file2_name = "list_doc2.pdf"
    
    test_client.post(
        "/api/v1/user-content/upload",
        headers={"Authorization": f"Bearer {access_token}"},
        files={"file": (file1_name, b"content1", "text/plain")}
    )
    test_client.post(
        "/api/v1/user-content/upload",
        headers={"Authorization": f"Bearer {access_token}"},
        files={"file": (file2_name, b"content2", "application/pdf")}
    )

    response = test_client.get(
        "/api/v1/user-content/list",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == 200
    files_listed = response.json()
    assert len(files_listed) == 2
    assert any(f["file_name"] == file1_name for f in files_listed)
    assert any(f["file_name"] == file2_name for f in files_listed)

@pytest.mark.asyncio
async def test_list_files_empty(mock_external_services_and_singletons, db_session: Session, test_client):
    mock_auth_service, mock_email_service, mock_validate_token, mock_get_jwks, mock_storage_service = mock_external_services_and_singletons

    # Authenticate a user with no uploaded files
    user_email = "empty_list_test@example.com"
    user_password = "Password123!"
    test_client.post("/api/v1/auth/register", json={"email": user_email, "password": user_password})
    login_response = test_client.post("/api/v1/auth/login", json={"email": user_email, "password": user_password})
    access_token = login_response.json()["access_token"]
    
    current_user_db = db_session.query(backend.app.models.user.User).filter(backend.app.models.user.User.email == user_email).first()
    mock_validate_token.return_value = {"sub": current_user_db.auth_provider_id, "email": current_user_db.email, "is_verified": current_user_db.is_verified}


    response = test_client.get(
        "/api/v1/user-content/list",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == 200
    assert response.json() == []
