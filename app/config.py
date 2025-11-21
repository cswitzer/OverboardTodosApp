from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    pass


class LocalSettings(Settings):
    # Get override by env file when they are added
    DEBUG: bool = True
    DATABASE_URL: str | None = None

    class Config:
        env_file = ".env/.env.local"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return LocalSettings()
