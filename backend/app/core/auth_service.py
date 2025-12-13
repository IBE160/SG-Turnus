# backend/app/core/auth_service.py
import os
from typing import Dict
import uuid
from backend.app.services.email_service import email_service # Assuming email_service is correctly configured

class UserNotFoundException(Exception):
    pass

class InvalidVerificationTokenException(Exception):
    pass

class DuplicateUserException(Exception):
    pass

# Mock database and auth provider for now
mock_db: Dict[str, Dict[str, str]] = {} # email -> {auth_provider_id, password_hash, is_verified, verification_token}
mock_auth_provider_users: Dict[str, str] = {} # auth_provider_id -> email

class AuthService:
    async def register_user(self, email: str, password: str):
        if email in mock_db:
            raise DuplicateUserException("User with this email already exists")
        
        auth_provider_id = f"mock_auth_id_{len(mock_auth_provider_users) + 1}"
        mock_auth_provider_users[auth_provider_id] = email

        verification_token = str(uuid.uuid4())
        frontend_verification_url = os.getenv("NEXT_PUBLIC_EMAIL_VERIFICATION_URL", "http://localhost:3000")
        verification_link = f"{frontend_verification_url}/verify-email?email={email}&token={verification_token}" # Frontend URL

        mock_db[email] = {
            "auth_provider_id": auth_provider_id,
            "password_hash": f"hashed_{password}", # Mock hashing
            "is_verified": False,
            "verification_token": verification_token
        }

        await email_service.send_verification_email(email, verification_link)
        print(f"User registered: {email}, Auth Provider ID: {auth_provider_id}")
        return {"user_id": auth_provider_id, "email": email}

    async def verify_email(self, email: str, token: str):
        user_data = mock_db.get(email)
        if not user_data:
            raise UserNotFoundException("User not found")
        
        # If already verified, consider it a success, regardless of token
        if user_data.get("is_verified"):
            return True

        # If not verified, proceed to check token
        if user_data.get("verification_token") != token:
            raise InvalidVerificationTokenException("Invalid verification token")

        user_data["is_verified"] = True
        user_data["verification_token"] = None # Invalidate token after use
        mock_db[email] = user_data # Update mock DB
        
        print(f"User email verified: {email}")
        return True

auth_service = AuthService() # Instantiate once
