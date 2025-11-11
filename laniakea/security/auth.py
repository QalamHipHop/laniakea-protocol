"""
LaniakeA Protocol - JWT Authentication Utilities
Handles token creation, verification, and user authentication.
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from laniakea.utils.config import Config

# --- Configuration ---
SECRET_KEY = Config.get("SECRET_KEY", "default-secret-key-change-me")
ALGORITHM = Config.get("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = Config.get("ACCESS_TOKEN_EXPIRE_MINUTES", 30)

# --- Schemas ---
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    username: Optional[str] = None
    scopes: List[str] = []

class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None

# --- OAuth2 Scheme ---
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# --- JWT Functions ---
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Creates a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str, credentials_exception):
    """Verifies a JWT token and returns the payload."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    return token_data

# --- Dependency for Authentication ---
async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Dependency to get the current authenticated user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token_data = verify_token(token, credentials_exception)
    
    # In a real application, you would fetch the user from the database here
    # For now, we'll return a mock user
    user = User(username=token_data.username, email=f"{token_data.username}@laniakea.com")
    
    if user is None:
        raise credentials_exception
    return user

# --- Rate Limiting Setup (Placeholder for now, actual setup in api.py) ---
# Requires Redis to be running, which is handled by docker-compose.
