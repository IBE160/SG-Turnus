# backend/app/api/v1/auth.py
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr
from backend.app.core.auth_service import auth_service, UserNotFoundException, InvalidVerificationTokenException, DuplicateUserException

router = APIRouter()

# Pydantic model for user registration request
class UserCreate(BaseModel):
    email: EmailStr
    password: str

from backend.app.api import schemas

@router.post("/auth/register", status_code=status.HTTP_201_CREATED)
async def register_user_endpoint(user: UserCreate):
    try:
        response_content = await auth_service.register_user(user.email, user.password)
        return response_content
    except DuplicateUserException as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

@router.post("/auth/verify-email", status_code=status.HTTP_200_OK)
async def verify_email_endpoint(data: schemas.VerifyEmailRequest):
    try:
        await auth_service.verify_email(data.email, data.token)
        return {"message": "Email verified successfully."}
    except UserNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except InvalidVerificationTokenException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
