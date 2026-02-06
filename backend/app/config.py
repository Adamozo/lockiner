from functools import lru_cache
from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    postgres_user: str = "lockiner"
    postgres_password: str = "lockiner_secret"
    postgres_host: str = "postgres"
    postgres_port: int = 5432
    postgres_db: str = "lockiner_db"

    @computed_field
    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"

    jwt_secret_key: str | None = None
    encryption_key: str | None = None
    gemini_api_key: str | None = None
    environment: str = "development"
    upload_dir: str = "/uploads"
    data_dir: str = "/data"


@lru_cache
def get_settings() -> Settings:
    return Settings()
