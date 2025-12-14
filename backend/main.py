from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from backend.app.api.v1.auth import router as auth_router
from backend.app.database import create_db_and_tables

# Temporary placeholder for JWT validation logic
# In a real app, this would involve decoding the JWT, verifying its signature,
# checking claims (e.g., expiration, audience, issuer), and potentially fetching
# user details from the database if needed.
# For now, we'll just check for the presence of a token.
token_auth_scheme = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(token_auth_scheme)):
    # This is a placeholder for actual JWT validation.
    # In a real application, you would:
    # 1. Decode the JWT (using python-jose for Auth0)
    # 2. Verify the signature against Auth0's public keys
    # 3. Validate claims (exp, aud, iss, etc.)
    # 4. Extract user information (e.g., user ID)
    if not credentials.credentials: # Check if token string is present
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # In a real scenario, you'd return a user object or ID from the token
    return {"user_token": credentials.credentials} # Just return the token for now

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    create_db_and_tables()

@app.get("/api/v1/health")
def read_root():
    return {"status": "ok"}

@app.get("/api/v1/protected")
async def protected_route(current_user: dict = Depends(get_current_user)):
    return {"message": f"Hello, {current_user['user_token']}! You have access to protected data."}

app.include_router(auth_router, prefix="/api/v1")

