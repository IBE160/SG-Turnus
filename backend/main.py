from fastapi import FastAPI, Depends, HTTPException, status
from backend.app.api.v1.auth import router as auth_router
from backend.app.api.v1.user_content import router as user_content_router
from backend.app.database import create_db_and_tables, get_db
from backend.app.dependencies import get_current_user
from backend.app.models.user import User
from sqlalchemy.orm import Session
import os

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    create_db_and_tables()

@app.get("/api/v1/health")
def read_root():
    return {"status": "ok"}

@app.get("/api/v1/protected")
async def protected_route(current_user: dict = Depends(get_current_user)):
    return {"message": f"Hello, user {current_user['user_id']}! You have access to protected data."}

# Test-only endpoint for Cypress to verify email status
@app.get("/api/v1/test/user-verification-status/{email}")
async def get_user_verification_status(email: str, db: Session = Depends(get_db)):
    environment = os.getenv("ENVIRONMENT", "development").lower()
    if environment not in ["development", "test"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied. This endpoint is only available in development or test environments.")
    
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    return {"email": user.email, "is_verified": user.is_verified}

app.include_router(auth_router, prefix="/api/v1")
app.include_router(user_content_router, prefix="/api/v1")

