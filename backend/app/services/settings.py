from typing import Optional
from pathlib import Path
from datetime import datetime
import json
import logging

from cryptography.fernet import Fernet, InvalidToken

from ..schemas import APIProviderConfigResponse, APIProviderListResponse
from ..integrations.ocr_provider import OCRProvider
from ..config import get_settings

logger = logging.getLogger(__name__)

# ---------------------------------------

SETTINGS_DIR = Path(get_settings().data_dir)
SETTINGS_FILE = SETTINGS_DIR / "settings.json"

# ---------------------------------------


class InvalidProviderError(Exception):
    def __init__(self, provider: str):
        self.provider = provider
        super().__init__(f"Invalid provider. Must be one of: {', '.join([p.value for p in OCRProvider])}")


class ProviderNotConfiguredError(Exception):
    def __init__(self, provider: str):
        self.provider = provider
        super().__init__(f"Provider {provider} is not configured. Add it first.")


class EncryptionError(Exception):
    def __init__(self):
        super().__init__("Failed to encrypt API key")


class DecryptionError(Exception):
    def __init__(self):
        super().__init__("Failed to decrypt API key. ENCRYPTION_KEY may have changed.")


class SettingsSaveError(Exception):
    def __init__(self, message: str):
        super().__init__(f"Failed to save settings: {message}")


# ---------------------------------------


class SettingsService:
    def __init__(self):
        self._encryption_key: Optional[bytes] = None

    def _get_encryption_key(self) -> bytes:
        settings = get_settings()
        env_key = settings.encryption_key

        if not env_key:
            if settings.environment == "production":
                raise RuntimeError(
                    "ENCRYPTION_KEY environment variable is required in production"
                )
            logger.warning("ENCRYPTION_KEY not set. Using temporary key (data will be lost on restart)")
            return Fernet.generate_key()

        try:
            key_bytes = env_key.encode()
            Fernet(key_bytes)
            return key_bytes
        except Exception as e:
            raise RuntimeError(f"Invalid ENCRYPTION_KEY format: {e}")

    def _encrypt_api_key(self, api_key: str) -> str:
        """Encrypt API key using Fernet symmetric encryption."""
        try:
            encryption_key = self._get_encryption_key()
            cipher = Fernet(encryption_key)
            encrypted_bytes = cipher.encrypt(api_key.encode())
            return encrypted_bytes.decode()

        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            raise EncryptionError()

    def _decrypt_api_key(self, encrypted_api_key: str) -> str:
        """Decrypt API key using Fernet symmetric encryption."""
        try:
            encryption_key = self._get_encryption_key()
            cipher = Fernet(encryption_key)
            decrypted_bytes = cipher.decrypt(encrypted_api_key.encode())
            return decrypted_bytes.decode()

        except InvalidToken:
            logger.error("Decryption failed: Invalid token or wrong encryption key")
            raise DecryptionError()

        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise DecryptionError()

    def _load_settings(self) -> dict:
        """Load settings from JSON file."""
        try:
            SETTINGS_DIR.mkdir(parents=True, exist_ok=True)

        except (PermissionError, OSError):
            pass

        if SETTINGS_FILE.exists():
            try:
                with open(SETTINGS_FILE, "r") as f:
                    return json.load(f)

            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"Failed to load settings file: {e}")
                return {}

        return {}

    def _save_settings(self, settings: dict) -> None:
        """Save settings to JSON file."""
        try:
            SETTINGS_DIR.mkdir(parents=True, exist_ok=True)
            with open(SETTINGS_FILE, "w") as f:
                json.dump(settings, f, indent=2)

        except (IOError, PermissionError) as e:
            raise SettingsSaveError(str(e))

    def get_active_ocr_provider(self) -> tuple[Optional[OCRProvider], Optional[str]]:
        """Get the active OCR provider and its API key."""
        settings = self._load_settings()
        providers = settings.get("ocr_providers", {})
        active_provider = settings.get("active_ocr_provider")

        if not active_provider:
            return None, None

        provider_config = providers.get(active_provider)
        if provider_config is None:
            return None, None

        try:
            encrypted_key = provider_config.get("encrypted_key")
            if encrypted_key:
                api_key = self._decrypt_api_key(encrypted_key)
                return OCRProvider(active_provider), api_key

        except Exception as e:
            logger.error(f"Failed to decrypt API key for {active_provider}: {e}")
            return None, None

        return None, None

    def add_api_provider(
        self,
        provider: str,
        api_key: str,
        is_active: bool = False,
    ) -> APIProviderConfigResponse:
        """Add or update API provider configuration."""
        try:
            provider_type = OCRProvider(provider.lower())

        except ValueError:
            raise InvalidProviderError(provider)

        settings = self._load_settings()

        if "ocr_providers" not in settings:
            settings["ocr_providers"] = {}

        encrypted_key = self._encrypt_api_key(api_key.strip())

        settings["ocr_providers"][provider_type.value] = {
            "encrypted_key": encrypted_key,
            "configured_at": datetime.utcnow().isoformat(),
        }

        if is_active or not settings.get("active_ocr_provider"):
            settings["active_ocr_provider"] = provider_type.value

        self._save_settings(settings)

        logger.info(f"{provider_type.value} API key saved successfully (encrypted)")

        key_preview = api_key[:8] + "..." if len(api_key) > 8 else api_key[:4] + "..."

        return APIProviderConfigResponse(
            provider=provider_type.value,
            key_preview=key_preview,
            is_active=settings["active_ocr_provider"] == provider_type.value,
            configured_at=settings["ocr_providers"][provider_type.value]["configured_at"],
        )

    def list_api_providers(self) -> APIProviderListResponse:
        """List all configured API providers."""
        settings = self._load_settings()
        providers = settings.get("ocr_providers", {})
        active_provider = settings.get("active_ocr_provider")

        providers_list = []
        for provider_name, provider_config in providers.items():
            try:
                encrypted_key = provider_config.get("encrypted_key")
                if encrypted_key:
                    api_key = self._decrypt_api_key(encrypted_key)
                    key_preview = api_key[:8] + "..." if len(api_key) > 8 else api_key[:4] + "..."
                    providers_list.append(APIProviderConfigResponse(
                        provider=provider_name,
                        key_preview=key_preview,
                        is_active=active_provider == provider_name,
                        configured_at=provider_config.get("configured_at"),
                    ))

            except Exception as e:
                logger.error(f"Failed to load provider {provider_name}: {e}")

        return APIProviderListResponse(
            providers=providers_list,
            active_provider=active_provider,
        )

    def set_active_provider(self, provider: str) -> dict:
        """Set the active OCR provider."""
        settings = self._load_settings()
        providers = settings.get("ocr_providers", {})

        if provider not in providers:
            raise ProviderNotConfiguredError(provider)

        settings["active_ocr_provider"] = provider
        self._save_settings(settings)

        logger.info(f"Active OCR provider set to: {provider}")

        return {
            "message": f"Active OCR provider set to {provider}",
            "active_provider": provider,
        }

    def delete_api_provider(self, provider: str) -> None:
        """Delete saved API provider configuration."""
        settings = self._load_settings()
        providers = settings.get("ocr_providers", {})

        if provider in providers:
            del providers[provider]
            settings["ocr_providers"] = providers

            if settings.get("active_ocr_provider") == provider:
                if providers:
                    settings["active_ocr_provider"] = next(iter(providers.keys()))
                else:
                    settings["active_ocr_provider"] = None

            self._save_settings(settings)

    def get_byczq_config(self) -> dict:
        """Pobiera konfigurację Byczq (URL + zamaskowany secret)."""
        settings = self._load_settings()
        byczq = settings.get("byczq", {})
        secret = byczq.get("notify_secret", "")
        masked = (secret[:4] + "..." + secret[-4:]) if len(secret) > 8 else ("***" if secret else "")
        return {
            "service_url": byczq.get("service_url", ""),
            "notify_secret_masked": masked,
            "configured": bool(byczq.get("service_url")),
        }

    def save_byczq_config(self, service_url: str, notify_secret: str | None = None) -> dict:
        """Zapisuje konfigurację Byczq. Secret pomijany jeśli None (brak zmiany)."""
        data = self._load_settings()
        byczq = data.get("byczq", {})
        byczq["service_url"] = service_url.rstrip("/")
        if notify_secret is not None:
            byczq["notify_secret"] = notify_secret
        data["byczq"] = byczq
        self._save_settings(data)
        return self.get_byczq_config()

    def get_byczq_notify_secret(self) -> str:
        """Zwraca plaintext secret do weryfikacji powiadomień do Byczq."""
        settings = self._load_settings()
        return settings.get("byczq", {}).get("notify_secret", "")

    def get_byczq_service_url(self) -> str:
        """Zwraca URL serwisu Byczq (DB ma priorytet nad env)."""
        settings = self._load_settings()
        url = settings.get("byczq", {}).get("service_url", "")
        if not url:
            from ..config import get_settings
            url = get_settings().byczq_service_url
        return url

    def get_gemini_key_status(self) -> dict:
        """Check if Gemini API key is configured (backward compatibility)."""
        settings = self._load_settings()
        providers = settings.get("ocr_providers", {})

        if "gemini" in providers:
            try:
                encrypted_key = providers["gemini"].get("encrypted_key")
                api_key = self._decrypt_api_key(encrypted_key)
                key_preview = api_key[:8] + "..." if len(api_key) > 8 else api_key[:4] + "..."
                return {
                    "configured": True,
                    "key_preview": key_preview,
                }

            except:
                pass

        return {
            "configured": False,
            "key_preview": None,
        }
