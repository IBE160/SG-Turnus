from fastapi.testclient import TestClient
from backend.main import app
from backend.app.core import auth_service
import pytest
from unittest.mock import patch, AsyncMock

client = TestClient(app)

@pytest.fixture(autouse=True)
def clear_auth_service_mocks():
    """
    Pytest autouse fixture to clear auth_service.mock_db and
    auth_service.mock_auth_provider_users before each test.
    """
    auth_service.mock_db.clear()
    auth_service.mock_auth_provider_users.clear()

def test_health_check():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

@patch('backend.app.core.auth_service.email_service.send_verification_email', new_callable=AsyncMock)
def test_register_user_success(mock_send_email):
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "test@example.com", "password": "Password123!"}
    )
    assert response.status_code == 201
    assert "user_id" in response.json()
    assert response.json()["email"] == "test@example.com"
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

@patch('backend.app.core.auth_service.email_service.send_verification_email', new_callable=AsyncMock)
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

def test_verify_email_already_verified():
    # First, register and verify a user
    register_response = client.post(
        "/api/v1/auth/register",
        json={"email": "alreadyverified@example.com", "password": "Password123!"}
    )
    assert register_response.status_code == 201

    token = auth_service.mock_db["alreadyverified@example.com"]["verification_token"]
    verify_response = client.post(
        "/api/v1/auth/verify-email",
        json={"email": "alreadyverified@example.com", "token": token}
    )
    assert verify_response.status_code == 200
    assert auth_service.mock_db["alreadyverified@example.com"]["is_verified"] == True

    # Try to verify again
    reverify_response = client.post(
        "/api/v1/auth/verify-email",
        json={"email": "alreadyverified@example.com", "token": token}
    )
    assert reverify_response.status_code == 200
    assert reverify_response.json() == {"message": "Email verified successfully."}