from functools import lru_cache
from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    db_user: str = "scrooge"
    db_password: str = "scrooge_secret"
    db_host: str = "postgres"
    db_port: int = 5432
    db_name: str = "scrooge_db"
    
    @computed_field
    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    jwt_secret_key: str | None = None
    encryption_key: str | None = None
    gemini_api_key: str | None = None
    environment: str = "development"
    upload_dir: str = "/uploads"
    data_dir: str = "/data"


@lru_cache
def get_settings() -> Settings:
    return Settings()
