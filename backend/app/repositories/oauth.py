import json
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..models import OAuthClient, OAuthAuthorizationCode, OAuthAccessToken


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
