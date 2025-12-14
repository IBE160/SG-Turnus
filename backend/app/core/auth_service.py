# backend/app/core/auth_service.py
import os
import uuid
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from backend.app.models.user import User
from fastapi import HTTPException, status
from auth0.management import Auth0
from backend.app.services.email_service import email_service # Assuming email_service is correctly configured

class UserNotFoundException(Exception):
    pass

class InvalidVerificationTokenException(Exception):
    pass

class DuplicateUserException(Exception):
    pass

class Auth0CreationException(Exception):
    pass

class AuthService:
    def __init__(self):
        self.auth0_domain = os.getenv("AUTH0_DOMAIN")
        self.auth0_management_client_id = os.getenv("AUTH0_MANAGEMENT_CLIENT_ID")
        self.auth0_management_client_secret = os.getenv("AUTH0_MANAGEMENT_CLIENT_SECRET")

        if not all([self.auth0_domain, self.auth0_management_client_id, self.auth0_management_client_secret]):
            # Instead of falling back to mock, raise an error
            raise ValueError("CRITICAL: Auth0 environment variables (AUTH0_DOMAIN, AUTH0_MANAGEMENT_CLIENT_ID, AUTH0_MANAGEMENT_CLIENT_SECRET) must be set for AuthService to initialize securely.")
        else:
            self._auth0 = Auth0(self.auth0_domain, self.auth0_management_client_id)
            print(f"Auth0 client initialized for domain: {self.auth0_domain}")

    async def register_user(self, email: str, password: str, db: Session):
        # Check if user already exists in our database
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            raise DuplicateUserException("User with this email already exists")
        
        auth_provider_id = None
        # Since _auth0 is guaranteed to be initialized, we can directly use it
        try:
            # Create user in Auth0
            auth0_user = self._auth0.users.create({
                "email": email,
                "password": password,
                "connection": "Username-Password-Authentication", # Or your specific database connection
                "email_verified": False,
                "app_metadata": {}
            })
            auth_provider_id = auth0_user["user_id"]
            print(f"User created in Auth0: {email}, Auth0 ID: {auth_provider_id}")

        except Exception as e:
            print(f"DEBUG: Exception in register_user Auth0 call: {e}")
            # Auth0 errors can vary, catch general exception for now
            if "The user already exists." in str(e): # Specific Auth0 error for duplicate user
                raise DuplicateUserException("User with this email already exists in Auth0")
            raise Auth0CreationException(f"Failed to create user in Auth0: {e}")


        # Create user in our database
        new_user = User(auth_provider_id=auth_provider_id, email=email, is_verified=False)
        db.add(new_user)
        try:
            db.commit()
            db.refresh(new_user)
        except IntegrityError:
            db.rollback()
            raise DuplicateUserException("User with this email already exists (DB constraint)") # Should be caught by Auth0 or earlier check

        # Generate and send verification email (simplified for now)
        verification_token = str(uuid.uuid4()) # Store this temporarily for verification mock
        # In a real scenario, this token would be stored in the DB or a temporary cache
        # and linked to the user. For now, we'll assume it's part of the email.
        
        frontend_verification_url = os.getenv("NEXT_PUBLIC_EMAIL_VERIFICATION_URL", "http://localhost:3000")
        verification_link = f"{frontend_verification_url}/verify-email?email={email}&token={verification_token}" # Frontend URL

        await email_service.send_verification_email(email, verification_link)
        print(f"User registered: {email}, Auth Provider ID: {auth_provider_id}")
        return {"user_id": new_user.auth_provider_id, "email": new_user.email}

    async def verify_email(self, email: str, token: str, db: Session):
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise UserNotFoundException("User not found")
        
        if user.is_verified:
            return True # Already verified

        # In a real application, you'd verify the token against a stored token
        # linked to the user. For this mock, we assume the token sent matches.
        # This part needs proper implementation when a real token system is in place.
        # For now, we'll just check if it's any non-empty token as a placeholder.
        if not token:
             raise InvalidVerificationTokenException("Verification token is missing")

        user.is_verified = True
        db.add(user)
        db.commit()
        db.refresh(user)
        
        print(f"User email verified: {email}")
        return True

auth_service = AuthService() # Instantiate once
