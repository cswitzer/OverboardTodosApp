from datetime import timedelta, datetime, timezone
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from models import Users
from starlette import status
from database import get_db
from passlib.context import CryptContext
from fastapi.security import (
    OAuth2PasswordRequestForm,
    OAuth2PasswordBearer,  # check the bearer token
)
from jose import jwt, JWTError

router = APIRouter(prefix="/auth", tags=["auth"])

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth_bearer = OAuth2PasswordBearer(tokenUrl="auth/token/")

# Never expose your secret key in production code like this. I am just learning here.
SECRET_KEY = "f65da53e49581fc4b58ec88c6907fec197bddabd5619d91fc12e70e709f34903"
ALGORITHM = "HS256"

db_dependency = Annotated[Session, Depends(get_db)]


def authenticate_user(username: str, password: str, db: Session) -> Users | None:
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return None
    if not bcrypt_context.verify(password, user.hashed_password):
        return None
    return user


def create_access_token(
    username: str, user_id: int, role: str, expires_delta: timedelta
):
    # build the payload and set the expiration
    encode = {"sub": username, "id": user_id, "role": role}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({"exp": expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: Annotated[str, Depends(oauth_bearer)]):
    try:
        # check if signature is valid and not expired
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        user_role: str = payload.get("role")
        if username is None or user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials.",
            )
        return {"username": username, "id": user_id, "user_role": user_role}
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate user.",
        )


class CreateUserRequest(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    role: str


class Token(BaseModel):
    access_token: str
    token_type: str


# Already adding prefix "/auth" in APIRouter
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, create_user_request: CreateUserRequest):
    create_user_model = Users(
        **create_user_request.model_dump(exclude={"password"}),
        hashed_password=bcrypt_context.hash(create_user_request.password),
        is_active=True,
    )
    db.add(create_user_model)
    db.commit()


@router.get("/users/", status_code=status.HTTP_200_OK)
async def get_users(db: db_dependency):
    return db.query(Users).all()


@router.post("/token/", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency
):
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
