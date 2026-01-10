"""
Settings management API endpoints.

This module provides endpoints for managing application settings,
including API keys and configuration options.

Security Notes:
    - API keys are encrypted using Fernet (AES-128) before storage
    - Encryption key must be set via ENCRYPTION_KEY environment variable
    - If ENCRYPTION_KEY is not set, a key is auto-generated (WARNING: not persistent across restarts)
    - Gemini API key format is validated (AIza prefix, 39 characters)
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field, field_validator
from typing import Optional
import json
import os
import re
from pathlib import Path
from cryptography.fernet import Fernet, InvalidToken
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/settings", tags=["settings"])

# Settings file path - stored in /data directory (persistent Docker volume)
SETTINGS_DIR = Path(os.getenv("DATA_DIR", "/data"))
SETTINGS_FILE = SETTINGS_DIR / "settings.json"

# Gemini API key validation regex (AIza + 35 alphanumeric/dash/underscore = 39 chars total)
GEMINI_API_KEY_PATTERN = re.compile(r"^AIza[A-Za-z0-9_-]{35}$")


def _get_encryption_key() -> bytes:
    """
    Get or generate encryption key for API key storage.

    Returns:
        Fernet encryption key (32 bytes, base64-encoded)

    Note:
        - First checks ENCRYPTION_KEY environment variable
        - If not set, generates a random key (WARNING: not persistent across restarts)
        - In production, ALWAYS set ENCRYPTION_KEY in environment
    """
    env_key = os.getenv("ENCRYPTION_KEY")

    if env_key:
        try:
            # Validate that the key is valid Fernet key
            key_bytes = env_key.encode()
            Fernet(key_bytes)  # This will raise if invalid
            return key_bytes
        except Exception as e:
            logger.error(f"Invalid ENCRYPTION_KEY in environment: {e}")
            logger.warning("Generating temporary encryption key (will not persist across restarts)")
    else:
        logger.warning("ENCRYPTION_KEY not set in environment. Generating temporary key.")
        logger.warning("Set ENCRYPTION_KEY for production to persist encrypted data across restarts.")

    # Generate new key (NOT RECOMMENDED for production)
    return Fernet.generate_key()


def _encrypt_api_key(api_key: str) -> str:
    """
    Encrypt API key using Fernet symmetric encryption.

    Args:
        api_key: Plain text API key

    Returns:
        Base64-encoded encrypted API key

    Note:
        Uses AES-128 encryption in CBC mode with PKCS7 padding
    """
    try:
        encryption_key = _get_encryption_key()
        cipher = Fernet(encryption_key)
        encrypted_bytes = cipher.encrypt(api_key.encode())
        return encrypted_bytes.decode()
    except Exception as e:
        logger.error(f"Encryption failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to encrypt API key"
        )


def _decrypt_api_key(encrypted_api_key: str) -> str:
    """
    Decrypt API key using Fernet symmetric encryption.

    Args:
        encrypted_api_key: Base64-encoded encrypted API key

    Returns:
        Plain text API key

    Raises:
        HTTPException: If decryption fails (invalid key or corrupted data)
    """
    try:
        encryption_key = _get_encryption_key()
        cipher = Fernet(encryption_key)
        decrypted_bytes = cipher.decrypt(encrypted_api_key.encode())
        return decrypted_bytes.decode()
    except InvalidToken:
        logger.error("Decryption failed: Invalid token or wrong encryption key")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to decrypt API key. ENCRYPTION_KEY may have changed."
        )
    except Exception as e:
        logger.error(f"Decryption failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to decrypt API key"
        )


class GeminiKeyRequest(BaseModel):
    """
    Request schema for saving Gemini API key.

    Security:
        - Validates API key format (must start with 'AIza' and be 39 characters)
        - Key is encrypted before storage using Fernet symmetric encryption
    """
    api_key: str = Field(..., min_length=39, max_length=39, description="Google Gemini API key")

    @field_validator("api_key")
    @classmethod
    def validate_gemini_key_format(cls, v: str) -> str:
        """
        Validate Gemini API key format.

        Args:
            v: API key to validate

        Returns:
            Validated API key

        Raises:
            ValueError: If API key format is invalid
        """
        if not GEMINI_API_KEY_PATTERN.match(v):
            raise ValueError(
                "Invalid Gemini API key format. "
                "Key must start with 'AIza' and be exactly 39 characters."
            )
        return v


class GeminiKeyStatusResponse(BaseModel):
    """Response schema for Gemini API key status."""
    configured: bool = Field(..., description="Whether API key is configured")
    key_preview: Optional[str] = Field(None, description="First 8 characters of key")


class SettingsResponse(BaseModel):
    """Response schema for general settings."""
    gemini_key_configured: bool


def _load_settings() -> dict:
    """
    Load settings from JSON file.

    Returns:
        Dictionary containing all settings
    """
    try:
        SETTINGS_DIR.mkdir(parents=True, exist_ok=True)
    except (PermissionError, OSError):
        pass  # Directory will be created by Docker volume

    if SETTINGS_FILE.exists():
        try:
            with open(SETTINGS_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Failed to load settings file: {e}")
            return {}
    return {}


def _save_settings(settings: dict) -> None:
    """
    Save settings to JSON file.

    Args:
        settings: Dictionary containing all settings

    Raises:
        HTTPException: If saving fails
    """
    try:
        SETTINGS_DIR.mkdir(parents=True, exist_ok=True)
        with open(SETTINGS_FILE, "w") as f:
            json.dump(settings, f, indent=2)
    except (IOError, PermissionError) as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save settings: {str(e)}",
        )


def get_gemini_api_key() -> Optional[str]:
    """
    Get Gemini API key from settings or environment.

    Returns:
        Decrypted API key if configured, None otherwise

    Note:
        This function checks:
        1. Settings file (/data/settings.json) - encrypted key
        2. Environment variable GEMINI_API_KEY - plain text fallback

    Security:
        - Keys stored in settings file are encrypted using Fernet
        - Environment variable keys are used as-is (plain text)
    """
    # First check settings file (encrypted)
    settings = _load_settings()
    encrypted_key = settings.get("gemini_api_key")

    if encrypted_key:
        try:
            # Decrypt the stored key
            return _decrypt_api_key(encrypted_key)
        except HTTPException:
            # Decryption failed - key may be corrupted or ENCRYPTION_KEY changed
            logger.error("Failed to decrypt stored API key")
            # Don't fallback to env - this would mask the issue
            return None

    # Fallback to environment variable (plain text)
    return os.getenv("GEMINI_API_KEY")


@router.post("/gemini-key", status_code=status.HTTP_200_OK)
async def save_gemini_key(request: GeminiKeyRequest):
    """
    Save Google Gemini API key.

    Request Body:
        api_key: Google Gemini API key (required, must start with 'AIza', 39 chars)

    Returns:
        Success message

    Security:
        - API key format is validated (AIza prefix, exactly 39 characters)
        - API key is encrypted using Fernet before storage
        - Encrypted key is stored in /data/settings.json
        - Requires ENCRYPTION_KEY environment variable for persistence
    """
    # API key is already validated by Pydantic field_validator
    api_key = request.api_key.strip()

    # Load existing settings
    settings = _load_settings()

    # Encrypt API key before storage
    encrypted_key = _encrypt_api_key(api_key)

    # Update Gemini API key (encrypted)
    settings["gemini_api_key"] = encrypted_key

    # Save settings
    _save_settings(settings)

    logger.info("Gemini API key saved successfully (encrypted)")

    return {
        "message": "Gemini API key saved successfully",
        "configured": True,
    }


@router.get("/gemini-key-status", response_model=GeminiKeyStatusResponse)
async def get_gemini_key_status():
    """
    Check if Gemini API key is configured.

    Returns:
        Status indicating if key is configured (doesn't return actual key)

    Note:
        For security, this endpoint never returns the full API key,
        only whether it's configured and a preview of the first 8 characters.
    """
    api_key = get_gemini_api_key()

    if api_key and len(api_key) > 0:
        # Return preview (first 8 characters)
        preview = api_key[:8] + "..." if len(api_key) > 8 else api_key[:4] + "..."
        return GeminiKeyStatusResponse(
            configured=True,
            key_preview=preview,
        )

    return GeminiKeyStatusResponse(
        configured=False,
        key_preview=None,
    )


@router.delete("/gemini-key", status_code=status.HTTP_204_NO_CONTENT)
async def delete_gemini_key():
    """
    Delete saved Gemini API key.

    Returns:
        No content on success
    """
    settings = _load_settings()

    if "gemini_api_key" in settings:
        del settings["gemini_api_key"]
        _save_settings(settings)

    # Return 204 No Content
    return None


@router.get("/", response_model=SettingsResponse)
async def get_settings():
    """
    Get all application settings status.

    Returns:
        Settings status (without sensitive data)
    """
    api_key = get_gemini_api_key()

    return SettingsResponse(
        gemini_key_configured=bool(api_key)
    )
