from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session # Import Session for type hinting
from backend.app.api.v1.auth import router as auth_router
from backend.app.api.v1.study_materials import router as study_materials_router
from backend.app.api.v1.nlp import router as nlp_router
from backend.app.api.v1.clarity import router as clarity_router
from backend.app.dependencies import get_current_user
from backend.app.database import init_db, get_db, Base # Import init_db, get_db, and Base
from backend.app.models.user import User # Import SQLAlchemy User model
from backend.app.models.study_material import StudyMaterial # Import SQLAlchemy StudyMaterial model

app = FastAPI()

# Initialize the database and create tables
@app.on_event("startup")
def startup_event():
    init_db() # Call init_db to create tables

@app.get("/api/v1/health")
def read_root():
    return {"status": "ok"}

@app.get("/api/v1/protected")
async def protected_route(current_user: dict = Depends(get_current_user)):
    return {"message": f"Hello, user {current_user['email']}! You have access to protected data."} # Assuming current_user will have 'email'

# Remove the MongoDB-specific test-only endpoint
# @app.get("/api/v1/test/user-verification-status/{email}")
# async def get_user_verification_status(email: str, db: AsyncIOMotorClient = Depends(get_database)):
#     ... (MongoDB specific logic) ...


app.include_router(auth_router, prefix="/api/v1")
app.include_router(study_materials_router, prefix="/api/v1")
app.include_router(nlp_router, prefix="/api/v1")
app.include_router(clarity_router, prefix="/api/v1")