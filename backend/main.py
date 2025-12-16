from fastapi import FastAPI, Depends, HTTPException, status
from backend.app.api.v1.auth import router as auth_router
from backend.app.api.v1.user_content import router as user_content_router
from backend.app.database import connect_to_mongo, close_mongo_connection, get_database
from backend.app.dependencies import get_current_user
from motor.motor_asyncio import AsyncIOMotorClient
import os

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    await connect_to_mongo()

@app.on_event("shutdown")
async def shutdown_event():
    await close_mongo_connection()

@app.get("/api/v1/health")
def read_root():
    return {"status": "ok"}

@app.get("/api/v1/protected")
async def protected_route(current_user: dict = Depends(get_current_user)):
    return {"message": f"Hello, user {current_user['user_id']}! You have access to protected data."}

# Test-only endpoint for Cypress to verify email status
from backend.app.models.user import User as PydanticUser # Alias to avoid conflict if User is still used elsewhere
from backend.app.database import DATABASE_NAME # Import database name

@app.get("/api/v1/test/user-verification-status/{email}")
async def get_user_verification_status(email: str, db: AsyncIOMotorClient = Depends(get_database)):
    environment = os.getenv("ENVIRONMENT", "development").lower()
    if environment not in ["development", "test"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied. This endpoint is only available in development or test environments.")
    
    user_collection = db[DATABASE_NAME]["users"] # Access the 'users' collection
    user_data = await user_collection.find_one({"email": email})

    if not user_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    # Convert MongoDB BSON ObjectId to string for Pydantic model if needed, or extract directly
    user = PydanticUser(**user_data)
    
    return {"email": user.email, "is_verified": user.is_verified}

app.include_router(auth_router, prefix="/api/v1")
app.include_router(user_content_router, prefix="/api/v1")

