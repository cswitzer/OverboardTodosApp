from pydantic_settings import BaseSettings
from functools import lru_cache


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

    class Config:
        env_file = ".env/.env.local"


@lru_cache(maxsize=1)
def get_settings() -> LocalSettings:
    return LocalSettings()
