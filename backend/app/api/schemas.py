from pydantic import BaseModel, EmailStr

class UserRegistration(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    user_id: str
    email: EmailStr

class VerifyEmailRequest(BaseModel):
    email: EmailStr
    token: str