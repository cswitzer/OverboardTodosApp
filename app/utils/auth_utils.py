from datetime import datetime, timedelta
from typing import Any

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from starlette import status

from app.config import get_settings
from app.database import Session
from app.models import Users

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth_bearer = OAuth2PasswordBearer(tokenUrl="auth/token/")
settings = get_settings()

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"


def authenticate_user(username: str, password: str, db: Session) -> Users | None:
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return None
    if not bcrypt_context.verify(password, user.hashed_password):
        return None
    return user


def create_access_token(
    username: str, user_id: int, role: str, expires_delta: timedelta
) -> str:
    headers = {"alg": "HS256", "typ": "JWT"}
    body = {
        "sub": username,
        "id": user_id,
        "role": role,
        "token_type": "access",
        "exp": datetime.now() + expires_delta,
    }
    return jwt.encode(claims=body, key=settings.SECRET_KEY, headers=headers)


def create_refresh_token(username: str, user_id: int) -> str:
    headers = {"alg": "HS256", "typ": "JWT"}
    body = {
        "sub": username,
        "id": user_id,
        "token_type": "refresh",
        "exp": datetime.now() + timedelta(days=7),
    }
    return jwt.encode(claims=body, key=settings.SECRET_KEY, headers=headers)


def verify_refresh_token(token: str) -> dict[str, Any]:
    """Verify the refresh token and return the payload if valid."""
    try:
        payload = jwt.decode(
            token=token,
            key=settings.SECRET_KEY,
            algorithms=["HS256"],
        )
        if payload.get("token_type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type.",
            )

        username: str | None = payload.get("sub")
        user_id: int | None = payload.get("id")
        if username is None or user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials.",
            )
        return {"username": username, "id": user_id}
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate refresh token.",
        )


async def get_current_user(
    token: str = Depends(oauth_bearer),
) -> dict[str, Any]:
    try:
        payload = jwt.decode(
            token=token,
            key=settings.SECRET_KEY,
            algorithms=["HS256"],
        )
        username: str | None = payload.get("sub")
        user_id: int | None = payload.get("id")
        user_role: str | None = payload.get("role")
        if username is None or user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials.",
            )
        return {"username": username, "id": user_id, "user_role": user_role}
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user."
        )
