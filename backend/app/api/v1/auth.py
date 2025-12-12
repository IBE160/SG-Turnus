# backend/app/api/v1/auth.py
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr
from backend.app.core.auth_service import auth_service

router = APIRouter()

# Pydantic model for user registration request
class UserCreate(BaseModel):
    email: EmailStr
    password: str

# Pydantic model for email verification request
class EmailVerify(BaseModel):
    email: EmailStr
    token: str

@router.post("/auth/register", status_code=status.HTTP_201_CREATED)
async def register_user_endpoint(user: UserCreate):
    response_content, status_code = await auth_service.register_user(user.email, user.password)
    if status_code != 201:
        raise HTTPException(status_code=status_code, detail=response_content["detail"])
    return response_content

@router.post("/auth/verify-email", status_code=status.HTTP_200_OK)
async def verify_email_endpoint(data: EmailVerify):
    response_content, status_code = await auth_service.verify_email(data.email, data.token)
    if status_code != 200:
        raise HTTPException(status_code=status_code, detail=response_content["detail"])
    return response_content
