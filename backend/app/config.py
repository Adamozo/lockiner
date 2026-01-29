from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    database_url: str = "postgresql+asyncpg://scrooge:scrooge_secret@postgres:5432/scrooge_db"
    jwt_secret_key: str | None = None
    encryption_key: str | None = None
    environment: str = "development"
    upload_dir: str = "/uploads"
    data_dir: str = "/data"


@lru_cache
def get_settings() -> Settings:
    return Settings()
