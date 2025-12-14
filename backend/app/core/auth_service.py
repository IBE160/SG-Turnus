import os
import uuid
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from backend.app.models.user import User
from fastapi import HTTPException, status
from auth0.management import Auth0
from backend.app.services.email_service import email_service # Assuming email_service is correctly configured
import httpx # Import httpx for making HTTP requests

class UserNotFoundException(Exception):
    pass

class InvalidVerificationTokenException(Exception):
    pass

class DuplicateUserException(Exception):
    pass

class Auth0CreationException(Exception):
    pass

class IncorrectLoginCredentialsException(Exception):
    pass

class AuthService:
    def __init__(self):
        self.auth0_domain = os.getenv("AUTH0_DOMAIN")
        self.auth0_management_client_id = os.getenv("AUTH0_MANAGEMENT_CLIENT_ID")
        self.auth0_management_client_secret = os.getenv("AUTH0_MANAGEMENT_CLIENT_SECRET")
        
        self.auth0_client_id = os.getenv("AUTH0_CLIENT_ID") # For authentication API
        self.auth0_client_secret = os.getenv("AUTH0_CLIENT_SECRET") # For authentication API

        if not all([self.auth0_domain, self.auth0_management_client_id, self.auth0_management_client_secret, self.auth0_client_id, self.auth0_client_secret]):
            raise ValueError("CRITICAL: All required Auth0 environment variables (AUTH0_DOMAIN, AUTH0_MANAGEMENT_CLIENT_ID, AUTH0_MANAGEMENT_CLIENT_SECRET, AUTH0_CLIENT_ID, AUTH0_CLIENT_SECRET) must be set for AuthService to initialize securely.")
        else:
            self._auth0 = Auth0(self.auth0_domain, self.auth0_management_client_id)
            print(f"Auth0 management client initialized for domain: {self.auth0_domain}")

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

    async def login(self, email: str, password: str, db: Session) -> dict:
        """Authenticates user with Auth0 and returns access token."""
        auth_url = f"https://{self.auth0_domain}/oauth/token"
        headers = {"Content-Type": "application/json"}
        payload = {
            "grant_type": "password",
            "username": email,
            "password": password,
            "audience": os.getenv("AUTH0_API_AUDIENCE"), # The audience for your API
            "client_id": self.auth0_client_id,
            "client_secret": self.auth0_client_secret
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(auth_url, json=payload, headers=headers)
                response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)
                auth_data = await response.json()

                if "access_token" not in auth_data:
                    raise IncorrectLoginCredentialsException("Auth0 did not return an access token.")
                
                # Verify or create user in our database if not exists
                user = db.query(User).filter(User.email == email).first()
                if not user:
                    # If user exists in Auth0 but not our DB, create a minimal entry
                    # In a real system, you might fetch user_id from Auth0 token or /userinfo endpoint
                    # For now, we'll use a placeholder auth_provider_id or extract from token if available
                    auth_provider_id = "auth0|" + str(uuid.uuid4()) # Placeholder
                    # A more robust solution would decode the JWT to get the sub (user_id)
                    new_user = User(auth_provider_id=auth_provider_id, email=email, is_verified=True) # Assume verified if logged in
                    db.add(new_user)
                    db.commit()
                    db.refresh(new_user)
                    print(f"Created local user entry for {email} after successful Auth0 login.")

                print(f"User {email} logged in successfully via Auth0.")
                return auth_data # Contains access_token, expires_in, token_type

            except httpx.HTTPStatusError as e:
                print(f"Auth0 login failed for {email}: {e.response.text}")
                if e.response.status_code == 403: # Forbidden, often indicates incorrect credentials
                    raise IncorrectLoginCredentialsException("Incorrect email or password.")
                raise HTTPException(status_code=e.response.status_code, detail=f"Auth0 login error: {e.response.text}")
            except IncorrectLoginCredentialsException as e: # Catch custom exception
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
            except Exception as e:
                print(f"An unexpected error occurred during login for {email}: {e}")
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred during login.")


auth_service = AuthService() # Instantiate once
