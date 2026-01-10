import os
import logging
from typing import Optional
from datetime import datetime, timezone

from cryptography.fernet import Fernet, InvalidToken
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import User, UserAPIKey
from ..schemas import APIProviderConfigResponse, APIProviderListResponse
from ..integrations.ocr_provider import OCRProvider

logger = logging.getLogger(__name__)


class UserAPIKeyService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self._fernet: Optional[Fernet] = None

    def _get_fernet(self) -> Fernet:
        if self._fernet is None:
            env_key = os.getenv("ENCRYPTION_KEY")
            if not env_key:
                if os.getenv("ENVIRONMENT", "development") == "production":
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
            raise RuntimeError("Failed to decrypt API key. ENCRYPTION_KEY may have changed.")

    async def add_api_key(
        self,
        user: User,
        provider: OCRProvider,
        api_key: str,
        set_active: bool = False,
    ) -> APIProviderConfigResponse:
        encrypted_key = self._encrypt(api_key.strip())
        now = datetime.now(timezone.utc).isoformat()

        stmt = select(UserAPIKey).where(
            UserAPIKey.user_id == user.id,
            UserAPIKey.provider == provider.value
        )
        result = await self.db.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing:
            existing.encrypted_key = encrypted_key
            existing.updated_at = now
            if set_active:
                await self._set_active(user, provider)
            await self.db.commit()
        else:
            new_key = UserAPIKey(
                user_id=user.id,
                provider=provider.value,
                encrypted_key=encrypted_key,
                is_active=set_active,
                created_at=now,
            )
            self.db.add(new_key)
            if set_active:
                await self._set_active(user, provider)
            await self.db.commit()

        key_preview = api_key[:8] + "..." if len(api_key) > 8 else api_key[:4] + "..."

        return APIProviderConfigResponse(
            provider=provider.value,
            key_preview=key_preview,
            is_active=set_active,
            configured_at=now,
        )

    async def _set_active(self, user: User, provider: OCRProvider):
        stmt = update(UserAPIKey).where(
            UserAPIKey.user_id == user.id
        ).values(is_active=False)
        await self.db.execute(stmt)

        stmt = update(UserAPIKey).where(
            UserAPIKey.user_id == user.id,
            UserAPIKey.provider == provider.value
        ).values(is_active=True)
        await self.db.execute(stmt)

    async def get_active_provider(self, user: User) -> tuple[Optional[OCRProvider], Optional[str]]:
        stmt = select(UserAPIKey).where(
            UserAPIKey.user_id == user.id,
            UserAPIKey.is_active == True
        )
        result = await self.db.execute(stmt)
        active_key = result.scalar_one_or_none()

        if not active_key:
            return None, None

        try:
            decrypted = self._decrypt(active_key.encrypted_key)
            return OCRProvider(active_key.provider), decrypted
        except Exception as e:
            logger.error(f"Failed to decrypt API key for user {user.id}: {e}")
            return None, None

    async def list_providers(self, user: User) -> APIProviderListResponse:
        stmt = select(UserAPIKey).where(UserAPIKey.user_id == user.id)
        result = await self.db.execute(stmt)
        keys = result.scalars().all()

        providers = []
        active_provider = None

        for key in keys:
            try:
                decrypted = self._decrypt(key.encrypted_key)
                key_preview = decrypted[:8] + "..." if len(decrypted) > 8 else decrypted[:4] + "..."
                providers.append(APIProviderConfigResponse(
                    provider=key.provider,
                    key_preview=key_preview,
                    is_active=key.is_active,
                    configured_at=key.created_at,
                ))
                if key.is_active:
                    active_provider = key.provider
            except Exception as e:
                logger.error(f"Failed to decrypt key for provider {key.provider}: {e}")

        return APIProviderListResponse(
            providers=providers,
            active_provider=active_provider,
        )

    async def delete_provider(self, user: User, provider: OCRProvider) -> bool:
        stmt = delete(UserAPIKey).where(
            UserAPIKey.user_id == user.id,
            UserAPIKey.provider == provider.value
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount > 0

    async def set_active_provider(self, user: User, provider: OCRProvider) -> bool:
        stmt = select(UserAPIKey).where(
            UserAPIKey.user_id == user.id,
            UserAPIKey.provider == provider.value
        )
        result = await self.db.execute(stmt)
        exists = result.scalar_one_or_none()

        if not exists:
            return False

        await self._set_active(user, provider)
        await self.db.commit()
        return True
