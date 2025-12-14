from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from backend.app.api.v1.auth import router as auth_router
from backend.app.database import create_db_and_tables
from backend.app.core.jwt_utils import validate_token # Import the validation function
import os

token_auth_scheme = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(token_auth_scheme)):
    try:
        payload = await validate_token(credentials.credentials)
        # In a real scenario, you might fetch user details from your database
        # using the 'sub' (subject) claim from the payload.
        return {"user_id": payload.get("sub"), "token_payload": payload}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )

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

app.include_router(auth_router, prefix="/api/v1")

