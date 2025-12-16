import os
import uuid
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from backend.app.models.user import User
from fastapi import HTTPException, status
from auth0.management import Auth0
from backend.app.services.email_service import email_service # Assuming email_service is correctly configured
import httpx # Import httpx for making HTTP requests
from datetime import datetime, timedelta # Import for token expiry
from jose import jwt # Import jwt for token decoding
import logging # Import logging module

# Configure logger for this module
logger = logging.getLogger(__name__)
# Set default logging level (can be overridden by root logger config)
logger.setLevel(os.getenv("LOG_LEVEL", "INFO").upper())

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

class VerificationTokenExpiredException(Exception):
    pass

class AuthService:
    def __init__(self):
        self.auth0_domain = os.getenv("AUTH0_DOMAIN")
        self.auth0_management_client_id = os.getenv("AUTH0_MANAGEMENT_CLIENT_ID")
        self.auth0_management_client_secret = os.getenv("AUTH0_MANAGEMENT_CLIENT_SECRET")
        
        self.auth0_client_id = os.getenv("AUTH0_CLIENT_ID") # For authentication API
        self.auth0_client_secret = os.getenv("AUTH0_CLIENT_SECRET") # For authentication API
        self._auth0_configured = False # Flag to indicate if Auth0 is configured

        # Determine if running in a development environment
        environment = os.getenv("ENVIRONMENT", "development").lower()
        is_development = environment in ["development", "dev"]

        if not all([self.auth0_domain, self.auth0_management_client_id, self.auth0_management_client_secret, self.auth0_client_id, self.auth0_client_secret]):
            if not is_development:
                raise RuntimeError("ERROR: Essential Auth0 environment variables are not fully set. Cannot run in non-development environment without Auth0 configured.")
            else:
                logger.warning("Auth0 environment variables are not fully set. Auth0-dependent features will be disabled in this development environment.")
                self._auth0 = None
        else:
            self._auth0 = Auth0(self.auth0_domain, self.auth0_management_client_id)
            self._auth0_configured = True
            logger.info(f"Auth0 management client initialized for domain: {self.auth0_domain}")

    async def register_user(self, email: str, password: str, db: Session):
        is_cypress_testing_active = os.getenv("CYPRESS_TESTING_ACTIVE", "false").lower() == "true"
        if not self._auth0_configured:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Auth0 service is not configured. User registration is currently unavailable.")

        # Check if user already exists in our database
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            raise DuplicateUserException("User with this email already exists")
        
        auth_provider_id = None
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
            logger.info(f"User created in Auth0: {email}, Auth0 ID: {auth_provider_id}")

        except Exception as e:
            logger.error(f"Exception in register_user Auth0 call: {e}", exc_info=True)
            # Auth0 errors can vary, catch general exception for now
            if "The user already exists." in str(e): # Specific Auth0 error for duplicate user
                raise DuplicateUserException("User with this email already exists in Auth0")
            raise Auth0CreationException(f"Failed to create user in Auth0: {e}")


        # Create user in our database
        new_user = User(auth_provider_id=auth_provider_id, email=email, is_verified=False)
        
        # Generate and store verification token
        new_user.verification_token = str(uuid.uuid4())
        new_user.verification_token_expires_at = datetime.now() + timedelta(hours=24) # Token valid for 24 hours

        db.add(new_user)
        try:
            db.commit()
            db.refresh(new_user)
        except IntegrityError:
            db.rollback()
            raise DuplicateUserException("User with this email already exists (DB constraint)") # Should be caught by Auth0 or earlier check

        frontend_verification_url = os.getenv("NEXT_PUBLIC_EMAIL_VERIFICATION_URL", "http://localhost:3000")
        verification_link = f"{frontend_verification_url}/verify-email?email={email}&token={new_user.verification_token}" # Use stored token

        await email_service.send_verification_email(email, verification_link)
        logger.info(f"User registered: {email}, Auth Provider ID: {auth_provider_id}")
        
        response_data = {"user_id": new_user.auth_provider_id, "email": new_user.email}
        if is_cypress_testing_active:
            response_data["verification_token"] = new_user.verification_token
        return response_data

    async def verify_email(self, email: str, token: str, db: Session):
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise UserNotFoundException("User not found")
        
        if user.is_verified:
            return True # Already verified

        if not user.verification_token or user.verification_token != token:
             raise InvalidVerificationTokenException("Invalid verification token")
        
        if user.verification_token_expires_at and user.verification_token_expires_at < datetime.now():
            raise VerificationTokenExpiredException("Verification token has expired")

        user.is_verified = True
        user.verification_token = None
        user.verification_token_expires_at = None
        db.add(user)
        db.commit()
        db.refresh(user)
        
        logger.info(f"User email verified: {email}")
        return True

    async def login(self, email: str, password: str, db: Session) -> dict:
        """Authenticates user with Auth0 and returns access token."""
        if not self._auth0_configured:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Auth0 service is not configured. User login is currently unavailable.")

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
                if user:
                    if not user.is_verified:
                        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User email not verified.")
                else:
                    # If user exists in Auth0 but not our DB, create a minimal entry
                    access_token = auth_data["access_token"]
                    decoded_token = {}
                    try:
                        # For now, just decode without signature verification to get payload
                        # A full validation would require fetching JWKS
                        decoded_token = jwt.decode(access_token, options={"verify_signature": False})
                    except Exception as e:
                        logger.warning(f"Could not decode access token to get sub: {e}. Falling back to UUID for auth_provider_id.", exc_info=True)
                        
                    auth_provider_id = decoded_token.get("sub", "auth0|" + str(uuid.uuid4()))
                    
                    new_user = User(auth_provider_id=auth_provider_id, email=email, is_verified=True) # Assume verified if logged in
                    db.add(new_user)
                    db.commit()
                    db.refresh(new_user)
                    logger.info(f"Created local user entry for {email} after successful Auth0 login.")

                logger.info(f"User {email} logged in successfully via Auth0.")
                return auth_data # Contains access_token, expires_in, token_type

            except httpx.HTTPStatusError as e:
                logger.error(f"Auth0 login failed for {email}: {e.response.text}", exc_info=True)
                if e.response.status_code == 403: # Forbidden, often indicates incorrect credentials
                    raise IncorrectLoginCredentialsException("Incorrect email or password.")
                raise HTTPException(status_code=e.response.status_code, detail=f"Auth0 login error: {e.response.text}")
            except IncorrectLoginCredentialsException as e: # Catch custom exception
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
            except Exception as e:
                logger.error(f"An unexpected error occurred during login for {email}: {e}", exc_info=True)
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred during login.")


auth_service = AuthService() # Instantiate once
