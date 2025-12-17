import secrets
from datetime import timedelta
from typing import Annotated, Dict
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from passlib.context import CryptContext
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from starlette import status
from starlette.responses import RedirectResponse

from app.config import get_settings
from app.database import get_db
from app.models import Users
from app.utils.auth_utils import (
    GOOGLE_AUTH_URL,
    GOOGLE_TOKEN_URL,
    GOOGLE_USERINFO_URL,
    authenticate_user,
    create_access_token,
    create_refresh_token,
    verify_refresh_token,
)

router = APIRouter(prefix="/auth", tags=["auth"])
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
settings = get_settings()

db_dependency = Annotated[Session, Depends(get_db)]


class CreateUserRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: str = Field(min_length=5, max_length=255)
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=8, max_length=100)
    role: str = Field(min_length=3, max_length=50)
    phone_number: str | None = Field(default=None, min_length=7, max_length=20)


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


# Already adding prefix "/auth" in APIRouter
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(
    db: db_dependency, create_user_request: CreateUserRequest
) -> None:
    create_user_model = Users(
        **create_user_request.model_dump(exclude={"password"}),
        hashed_password=bcrypt_context.hash(create_user_request.password),
        is_active=True,
    )
    db.add(create_user_model)
    db.commit()


@router.post("/token/", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency
) -> Dict[str, str]:
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials.",
        )

    access_token = create_access_token(
        username=user.username,
        user_id=user.id,
        role=user.role,
        expires_delta=timedelta(minutes=30),
    )

    refresh_token = create_refresh_token(
        username=user.username,
        user_id=user.id,
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/token/refresh/", response_model=Token)
async def refresh_access_token(refresh_token: str, db: db_dependency) -> Dict[str, str]:
    token_data = verify_refresh_token(refresh_token)
    user = db.query(Users).filter(Users.id == token_data["id"]).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials.",
        )

    new_access_token = create_access_token(
        username=user.username,
        user_id=user.id,
        role=user.role,
        expires_delta=timedelta(minutes=30),
    )

    new_refresh_token = create_refresh_token(
        username=user.username,
        user_id=user.id,
    )

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
    }


@router.get("/google/login", status_code=status.HTTP_302_FOUND)
async def google_login() -> RedirectResponse:
    params = dict(
        client_id=settings.GOOGLE_CLIENT_ID,
        redirect_uri=f"{settings.GOOGLE_REDIRECT_URI}",
        response_type="code",
        scope="openid email profile",
        access_type="offline",
        prompt="consent",
    )
    auth_url = f"{GOOGLE_AUTH_URL}?{urlencode(params)}"
    return RedirectResponse(auth_url)


@router.get("/google/callback", status_code=status.HTTP_302_FOUND)
async def google_callback(code: str, db: db_dependency) -> RedirectResponse:
    async with httpx.AsyncClient() as client:
        # Exchange code for token. Note that this token is different from our JWT token in that
        # it is used to access Google APIs. Not to be confused with our own access token.
        token_response = await client.post(
            GOOGLE_TOKEN_URL,
            data=dict(
                code=code,
                client_id=settings.GOOGLE_CLIENT_ID,
                client_secret=settings.GOOGLE_CLIENT_SECRET,
                redirect_uri=f"{settings.GOOGLE_REDIRECT_URI}",
                grant_type="authorization_code",
            ),
        )
        if token_response.status_code != status.HTTP_200_OK:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to obtain access token from Google.",
            )

        tokens = token_response.json()
        access_token = tokens.get("access_token")

        # Use the access token to get user info
        userinfo_response = await client.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        if userinfo_response.status_code != status.HTTP_200_OK:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to obtain user info from Google.",
            )
        user_info = userinfo_response.json()

        # Check if user exists, if not create new user
        user = db.query(Users).filter(Users.email == user_info["email"]).first()
        if not user:
            google_username = user_info["email"].split("@")[0]
            unique_username = f"{google_username}_{secrets.token_hex(4)}"
            user = Users(
                email=user_info["email"],
                username=unique_username,
                first_name=user_info.get("given_name", ""),
                last_name=user_info.get("family_name", ""),
                hashed_password="",  # No password since using Google OAuth
                is_active=True,
                role="user",
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        # Create a JWT token for the user
        access_token = create_access_token(
            username=user.username,
            user_id=user.id,
            role=user.role,
            expires_delta=timedelta(minutes=30),
        )

        refresh_token = create_refresh_token(
            username=user.username,
            user_id=user.id,
        )

        response = RedirectResponse(f"{settings.CLIENT_URL}/oauth-success")
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            samesite="lax",
            max_age=1800,
        )
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            samesite="lax",
            max_age=604800,
        )
        return response
