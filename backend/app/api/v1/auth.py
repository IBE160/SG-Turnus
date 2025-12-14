# backend/app/api/v1/auth.py
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr
from backend.app.core.auth_service import auth_service, UserNotFoundException, InvalidVerificationTokenException, DuplicateUserException, Auth0CreationException, IncorrectLoginCredentialsException
from backend.app.database import get_db
from sqlalchemy.orm import Session
from backend.app.api.schemas import LoginRequest, TokenResponse # Import new schemas

router = APIRouter()

# Pydantic model for user registration request
class UserCreate(BaseModel):
    email: EmailStr
    password: str

from backend.app.api import schemas

@router.post("/auth/register", status_code=status.HTTP_201_CREATED)
async def register_user_endpoint(user: UserCreate, db: Session = Depends(get_db)):
    try:
        response_content = await auth_service.register_user(user.email, user.password, db)
        return response_content
    except DuplicateUserException as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except Auth0CreationException as e: # Catch the new exception
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/auth/verify-email", status_code=status.HTTP_200_OK)
async def verify_email_endpoint(data: schemas.VerifyEmailRequest, db: Session = Depends(get_db)):
    try:
        await auth_service.verify_email(data.email, data.token, db)
        return {"message": "Email verified successfully."}
    except UserNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except InvalidVerificationTokenException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/auth/login", response_model=TokenResponse)
async def login_for_access_token(request: LoginRequest, db: Session = Depends(get_db)):
    try:
        token_data = await auth_service.login(request.email, request.password, db)
        return TokenResponse(access_token=token_data["access_token"], token_type=token_data.get("token_type", "bearer"))
    except IncorrectLoginCredentialsException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )

