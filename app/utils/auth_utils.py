from datetime import datetime, timedelta
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
from starlette import status
from typing import Annotated, Any

from app.models import Users
from app.database import Session
from app.config import get_settings

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth_bearer = OAuth2PasswordBearer(tokenUrl="auth/token/")
settings = get_settings()


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
        "exp": datetime.now() + expires_delta,
    }
    return jwt.encode(claims=body, key=settings.SECRET_KEY, headers=headers)


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
