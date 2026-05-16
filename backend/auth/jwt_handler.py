"""
MockPilot AI — JWT Auth Handler
Uses PyJWT (actively maintained, Python 3.14 compatible).
"""
from datetime import datetime, timedelta, timezone
from typing import Optional
import jwt
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from backend.config import get_settings
from backend.database.models import get_db, User

settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    # Always convert sub to string — JWT spec + avoids int/str decode mismatch
    if "sub" in to_encode:
        to_encode["sub"] = str(to_encode["sub"])
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode["exp"] = expire
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired session. Please log in again.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        sub = payload.get("sub")
        if sub is None:
            raise exc
        user_id = int(sub)  # Always cast to int
    except (InvalidTokenError, ValueError, TypeError):
        raise exc

    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        raise exc
    return user
