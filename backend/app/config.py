from base64 import urlsafe_b64encode
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

    # VAPID keys for Web Push
    vapid_private_key: str = ""
    vapid_public_key: str = ""
    vapid_contact_email: str = ""

    # Timezone for reminder schedules (IANA format)
    app_timezone: str = "Europe/Warsaw"

    @computed_field
    @property
    def vapid_private_key_raw(self) -> str:
        """Convert PEM private key to raw base64url format for pywebpush."""
        if not self.vapid_private_key:
            return ""
        key_str = self.vapid_private_key
        # Handle literal \\n from .env files
        if "\\n" in key_str:
            key_str = key_str.replace("\\n", "\n")
        if not key_str.startswith("-----"):
            return key_str  # Already in raw format
        try:
            from cryptography.hazmat.primitives.serialization import (
                load_pem_private_key, Encoding, PublicFormat, NoEncryption,
            )
            from cryptography.hazmat.primitives.asymmetric.ec import ECDSA
            pkey = load_pem_private_key(key_str.encode(), password=None)
            raw_bytes = pkey.private_numbers().private_value.to_bytes(32, "big")
            return urlsafe_b64encode(raw_bytes).rstrip(b"=").decode()
        except Exception:
            return self.vapid_private_key


@lru_cache
def get_settings() -> Settings:
    return Settings()
