from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    pass


class LocalSettings(Settings):
    # Get override by env file when they are added
    FASTAPI_CONFIG: str = "local"
    DATABASE_URL: str = ""
    POSTGRES_USER: str = "todo_user"
    POSTGRES_PASSWORD: str = ""
    POSTGRES_HOST: str = "db"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "todo_db"
    CELERY_BROKER_URL: str = "redis://redis:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/0"
    SECRET_KEY: str = ""
    BASE_URL: str = "http://localhost:8080"
    CLIENT_URL: str = "http://localhost:3000"
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = f"{BASE_URL}/auth/google/callback"

    class Config:
        env_file = ".env/.env.local"


@lru_cache(maxsize=1)
def get_settings() -> LocalSettings:
    return LocalSettings()
