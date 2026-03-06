import json
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..models import OAuthClient, OAuthAuthorizationCode, OAuthAccessToken, OAuthDeviceCode


class OAuthRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_client(self, client_id: str) -> OAuthClient | None:
        result = await self.db.execute(
            select(OAuthClient).where(
                OAuthClient.client_id == client_id,
                OAuthClient.is_active == True,
            )
        )
        return result.scalar_one_or_none()

    async def create_authorization_code(
        self,
        code: str,
        client_id: int,
        user_id: int,
        code_challenge: str,
        redirect_uri: str,
        expires_in_seconds: int = 300,
    ) -> OAuthAuthorizationCode:
        expires_at = (datetime.now(timezone.utc) + timedelta(seconds=expires_in_seconds)).isoformat()
        obj = OAuthAuthorizationCode(
            code=code,
            client_id=client_id,
            user_id=user_id,
            code_challenge=code_challenge,
            redirect_uri=redirect_uri,
            expires_at=expires_at,
        )
        self.db.add(obj)
        await self.db.commit()
        await self.db.refresh(obj)
        return obj

    async def get_authorization_code(self, code: str) -> OAuthAuthorizationCode | None:
        result = await self.db.execute(
            select(OAuthAuthorizationCode).where(
                OAuthAuthorizationCode.code == code,
                OAuthAuthorizationCode.used == False,
            )
        )
        return result.scalar_one_or_none()

    async def mark_code_used(self, code_obj: OAuthAuthorizationCode) -> None:
        code_obj.used = True
        await self.db.commit()

    async def create_access_token(
        self,
        access_token: str,
        refresh_token: str,
        client_id: int,
        user_id: int,
        access_expires_in: int = 3600,
        refresh_expires_in: int = 2592000,
    ) -> OAuthAccessToken:
        now = datetime.now(timezone.utc)
        obj = OAuthAccessToken(
            access_token=access_token,
            refresh_token=refresh_token,
            client_id=client_id,
            user_id=user_id,
            expires_at=(now + timedelta(seconds=access_expires_in)).isoformat(),
            refresh_token_expires_at=(now + timedelta(seconds=refresh_expires_in)).isoformat(),
        )
        self.db.add(obj)
        await self.db.commit()
        await self.db.refresh(obj)
        return obj

    async def get_by_access_token(self, token: str) -> OAuthAccessToken | None:
        result = await self.db.execute(
            select(OAuthAccessToken).where(
                OAuthAccessToken.access_token == token,
                OAuthAccessToken.revoked == False,
            )
        )
        return result.scalar_one_or_none()

    async def get_by_refresh_token(self, token: str) -> OAuthAccessToken | None:
        result = await self.db.execute(
            select(OAuthAccessToken).where(
                OAuthAccessToken.refresh_token == token,
                OAuthAccessToken.revoked == False,
            )
        )
        return result.scalar_one_or_none()

    async def revoke_token(self, token_obj: OAuthAccessToken) -> None:
        token_obj.revoked = True
        await self.db.commit()

    async def create_device_code(
        self,
        device_code: str,
        user_code: str,
        client_id: int,
        expires_in_seconds: int = 600,
    ) -> OAuthDeviceCode:
        expires_at = (datetime.now(timezone.utc) + timedelta(seconds=expires_in_seconds)).isoformat()
        obj = OAuthDeviceCode(
            device_code=device_code,
            user_code=user_code,
            client_id=client_id,
            status="pending",
            expires_at=expires_at,
        )
        self.db.add(obj)
        await self.db.commit()
        await self.db.refresh(obj)
        return obj

    async def get_device_code_by_device(self, device_code: str) -> OAuthDeviceCode | None:
        result = await self.db.execute(
            select(OAuthDeviceCode).where(OAuthDeviceCode.device_code == device_code)
        )
        return result.scalar_one_or_none()

    async def get_device_code_by_user_code(self, user_code: str) -> OAuthDeviceCode | None:
        result = await self.db.execute(
            select(OAuthDeviceCode).where(OAuthDeviceCode.user_code == user_code)
        )
        return result.scalar_one_or_none()

    async def approve_device_code(self, device_code_obj: OAuthDeviceCode, user_id: int) -> None:
        device_code_obj.status = "approved"
        device_code_obj.user_id = user_id
        await self.db.commit()

    async def deny_device_code(self, device_code_obj: OAuthDeviceCode) -> None:
        device_code_obj.status = "denied"
        await self.db.commit()
