from datetime import timedelta
from typing import Annotated, Dict
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from starlette import status
from app.models import Users
from app.database import get_db
from app.utils.auth_utils import authenticate_user, create_access_token
from passlib.context import CryptContext
from fastapi.security import (
    OAuth2PasswordRequestForm,
)

router = APIRouter(prefix="/auth", tags=["auth"])
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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

    token = create_access_token(
        username=user.username,
        user_id=user.id,
        role=user.role,
        expires_delta=timedelta(minutes=30),
    )
    return {"access_token": token, "token_type": "bearer"}
