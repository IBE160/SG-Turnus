from fastapi.testclient import TestClient
from main import app
from app.core.auth_service import auth_service # Import the auth_service instance
from unittest.mock import patch, AsyncMock # Import patch and AsyncMock
import pytest # Import pytest for fixtures

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_and_teardown_mocks(mocker):
    """
    Fixture to patch and clear instance-level mocks of the auth_service instance.
    """
    mocker.patch.object(auth_service, 'mock_db', {})
    mocker.patch.object(auth_service, 'mock_auth_provider_users', {})
    yield

def test_health_check():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

@patch('app.core.auth_service.email_service.send_verification_email', new_callable=AsyncMock)
def test_register_user_success(mock_send_email):
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "test@example.com", "password": "Password123!"}
    )
    assert response.status_code == 201
    assert "user_id" in response.json()
    assert response.json()["email"] == "test@example.com"
    # Now we can directly assert against the patched mock_db via auth_service instance
    assert auth_service.mock_db["test@example.com"]["is_verified"] == False
    assert auth_service.mock_db["test@example.com"]["verification_token"] is not None
    mock_send_email.assert_called_once()
    assert mock_send_email.call_args.args[0] == "test@example.com"
    assert "http://localhost:3000/verify-email" in mock_send_email.call_args.args[1]

def test_register_user_duplicate_email():
    client.post(
        "/api/v1/auth/register",
        json={"email": "test@example.com", "password": "Password123!"}
    )
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "test@example.com", "password": "AnotherPassword!"}
    )
    assert response.status_code == 409
    assert response.json() == {"detail": "User with this email already exists"}

@patch('app.core.auth_service.email_service.send_verification_email', new_callable=AsyncMock)
def test_verify_email_success(mock_send_email):
    # First, register a user
    register_response = client.post(
        "/api/v1/auth/register",
        json={"email": "verify@example.com", "password": "Password123!"}
    )
    assert register_response.status_code == 201
    mock_send_email.assert_called_once() # Email sent during registration

    # Get the verification token from the mock_db
    token = auth_service.mock_db["verify@example.com"]["verification_token"]

    # Now, verify the email
    verify_response = client.post(
        "/api/v1/auth/verify-email",
        json={"email": "verify@example.com", "token": token}
    )
    assert verify_response.status_code == 200
    assert verify_response.json() == {"message": "Email verified successfully."}
    assert auth_service.mock_db["verify@example.com"]["is_verified"] == True
    assert auth_service.mock_db["verify@example.com"]["verification_token"] is None

def test_verify_email_invalid_token():
    # First, register a user
    client.post(
        "/api/v1/auth/register",
        json={"email": "invalidtoken@example.com", "password": "Password123!"}
    )

    # Try to verify with an invalid token
    response = client.post(
        "/api/v1/auth/verify-email",
        json={"email": "invalidtoken@example.com", "token": "wrong_token"}
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid verification token"}

def test_verify_email_user_not_found():
    response = client.post(
        "/api/v1/auth/verify-email",
        json={"email": "nonexistent@example.com", "token": "any_token"}
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}
