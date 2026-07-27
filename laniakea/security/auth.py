"""
LaniakeA Protocol - JWT Authentication Utilities
Handles token creation, verification, and user authentication.
Author: Qalam — Master Rebuild v4
"""

from datetime import datetime, timedelta, timezone
from typing import List, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel, ConfigDict

from laniakea.core.config import settings
from laniakea.utils.logger import get_logger

logger = get_logger("laniakea.security.auth")

# --- Configuration (single source of truth: laniakea.core.config.settings) ---
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.JWT_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

# --- Schemas ---
class Token(BaseModel):
    model_config = ConfigDict(extra="forbid")
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    model_config = ConfigDict(extra="forbid")
    username: Optional[str] = None
    scopes: List[str] = []

class User(BaseModel):
    model_config = ConfigDict(extra="forbid")
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None

# --- OAuth2 Scheme ---
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=True)

# --- JWT Functions ---
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str, credentials_exception: HTTPException) -> TokenData:
    """Verify a JWT token and return the payload as TokenData."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: Optional[str] = payload.get("sub")
        if username is None:
            raise credentials_exception
        return TokenData(username=username, scopes=payload.get("scopes", []))
    except JWTError as exc:
        logger.warning("JWT verification failed: %s", exc)
        raise credentials_exception

# --- Dependency for Authentication ---
async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """FastAPI dependency to get the current authenticated user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token_data = verify_token(token, credentials_exception)
    # In a real application, the user is fetched from a database here.
    return User(
        username=token_data.username,
        email=f"{token_data.username}@laniakea.com" if token_data.username else None,
    )

__all__ = [
    "Token",
    "TokenData",
    "User",
    "oauth2_scheme",
    "create_access_token",
    "verify_token",
    "get_current_user",
]
