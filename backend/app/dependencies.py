from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # In a real application, you would decode and validate the token.
        # For now, we'll just return a dummy user.
        user = db.query(User).first()
        if user is None:
            raise credentials_exception
        return user
    except JWTError:
        raise credentials_exception
