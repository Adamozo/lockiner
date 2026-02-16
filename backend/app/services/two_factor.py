import json
import logging
import secrets
import string
from typing import Optional

import pyotp
from cryptography.fernet import Fernet, InvalidToken
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import User
from ..config import get_settings

logger = logging.getLogger(__name__)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

RECOVERY_CODE_COUNT = 8


class TwoFactorAlreadyEnabledError(Exception):
    def __init__(self):
        super().__init__("Two-factor authentication is already enabled")


class TwoFactorNotEnabledError(Exception):
    def __init__(self):
        super().__init__("Two-factor authentication is not enabled")


class TwoFactorSetupNotStartedError(Exception):
    def __init__(self):
        super().__init__("Two-factor setup has not been initiated")


class InvalidTwoFactorCodeError(Exception):
    def __init__(self):
        super().__init__("Invalid two-factor authentication code")


class TwoFactorService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self._fernet: Optional[Fernet] = None

    def _get_fernet(self) -> Fernet:
        if self._fernet is None:
            settings = get_settings()
            env_key = settings.encryption_key
            if not env_key:
                if settings.environment == "production":
                    raise RuntimeError("ENCRYPTION_KEY environment variable is required in production")
                logger.warning("ENCRYPTION_KEY not set. Using temporary key")
                env_key = Fernet.generate_key().decode()
            self._fernet = Fernet(env_key.encode())
        return self._fernet

    def _encrypt(self, value: str) -> str:
        return self._get_fernet().encrypt(value.encode()).decode()

    def _decrypt(self, encrypted_value: str) -> str:
        try:
            return self._get_fernet().decrypt(encrypted_value.encode()).decode()
        except InvalidToken:
            raise RuntimeError("Failed to decrypt TOTP secret. ENCRYPTION_KEY may have changed.")

    def _generate_recovery_code(self) -> str:
        chars = string.ascii_uppercase + string.digits
        part1 = ''.join(secrets.choice(chars) for _ in range(4))
        part2 = ''.join(secrets.choice(chars) for _ in range(4))
        return f"{part1}-{part2}"

    def _generate_recovery_codes(self) -> list[str]:
        return [self._generate_recovery_code() for _ in range(RECOVERY_CODE_COUNT)]

    def _hash_recovery_codes(self, codes: list[str]) -> str:
        hashed = [pwd_context.hash(code) for code in codes]
        return json.dumps(hashed)

    def _get_recovery_hashes(self, user: User) -> list[str]:
        if not user.recovery_codes_hash:
            return []
        return json.loads(user.recovery_codes_hash)

    def _verify_recovery_code(self, code: str, user: User) -> bool:
        hashes = self._get_recovery_hashes(user)
        for i, h in enumerate(hashes):
            if pwd_context.verify(code, h):
                # Consume the code
                hashes.pop(i)
                user.recovery_codes_hash = json.dumps(hashes)
                return True
        return False

    def _is_recovery_code_format(self, code: str) -> bool:
        return len(code) == 9 and code[4] == '-'

    async def initiate_setup(self, user: User) -> dict:
        if user.totp_enabled:
            raise TwoFactorAlreadyEnabledError()

        secret = pyotp.random_base32()
        user.totp_secret_encrypted = self._encrypt(secret)
        await self.db.commit()

        totp = pyotp.TOTP(secret)
        uri = totp.provisioning_uri(name=user.name, issuer_name="LockIner")

        return {"secret": secret, "uri": uri}

    async def verify_setup(self, user: User, code: str) -> list[str]:
        if user.totp_enabled:
            raise TwoFactorAlreadyEnabledError()

        if not user.totp_secret_encrypted:
            raise TwoFactorSetupNotStartedError()

        secret = self._decrypt(user.totp_secret_encrypted)
        totp = pyotp.TOTP(secret)

        if not totp.verify(code, valid_window=1):
            raise InvalidTwoFactorCodeError()

        recovery_codes = self._generate_recovery_codes()
        user.recovery_codes_hash = self._hash_recovery_codes(recovery_codes)
        user.totp_enabled = True
        await self.db.commit()

        return recovery_codes

    async def disable(self, user: User, code: str) -> None:
        if not user.totp_enabled:
            raise TwoFactorNotEnabledError()

        if not self._verify_code(user, code):
            raise InvalidTwoFactorCodeError()

        user.totp_secret_encrypted = None
        user.totp_enabled = False
        user.recovery_codes_hash = None
        await self.db.commit()

    async def get_status(self, user: User) -> dict:
        recovery_count = 0
        if user.recovery_codes_hash:
            hashes = json.loads(user.recovery_codes_hash)
            recovery_count = len(hashes)
        return {
            "enabled": user.totp_enabled or False,
            "recovery_codes_remaining": recovery_count,
        }

    def _verify_code(self, user: User, code: str) -> bool:
        """Verify a TOTP code or recovery code."""
        if self._is_recovery_code_format(code):
            return self._verify_recovery_code(code, user)

        if not user.totp_secret_encrypted:
            return False

        secret = self._decrypt(user.totp_secret_encrypted)
        totp = pyotp.TOTP(secret)
        return totp.verify(code, valid_window=1)

    async def verify_login_code(self, user: User, code: str) -> bool:
        result = self._verify_code(user, code)
        if result:
            await self.db.commit()  # Commit consumed recovery codes if any
        return result

    async def regenerate_recovery_codes(self, user: User, code: str) -> list[str]:
        if not user.totp_enabled:
            raise TwoFactorNotEnabledError()

        # Must use a TOTP code, not recovery code
        if not user.totp_secret_encrypted:
            raise InvalidTwoFactorCodeError()

        secret = self._decrypt(user.totp_secret_encrypted)
        totp = pyotp.TOTP(secret)

        if not totp.verify(code, valid_window=1):
            raise InvalidTwoFactorCodeError()

        recovery_codes = self._generate_recovery_codes()
        user.recovery_codes_hash = self._hash_recovery_codes(recovery_codes)
        await self.db.commit()

        return recovery_codes
