import base64
import hashlib
import json
import secrets
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from ..models import OAuthClient, OAuthAuthorizationCode
from ..repositories.oauth import OAuthRepository
from ..repositories.user import UserRepository


class OAuthError(Exception):
    def __init__(self, error: str, description: str = ""):
        self.error = error
        self.description = description
        super().__init__(description or error)


class OAuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = OAuthRepository(db)
        self.user_repo = UserRepository(db)

    async def get_client_or_raise(self, client_id: str) -> OAuthClient:
        client = await self.repo.get_client(client_id)
        if not client:
            raise OAuthError("invalid_client", "Unknown client_id")
        return client

    def _validate_redirect_uri(self, client: OAuthClient, redirect_uri: str) -> None:
        allowed = json.loads(client.redirect_uris)
        if redirect_uri not in allowed:
            raise OAuthError("invalid_request", "redirect_uri not allowed")

    def _verify_pkce(self, code_verifier: str, code_challenge: str) -> bool:
        digest = hashlib.sha256(code_verifier.encode()).digest()
        computed = base64.urlsafe_b64encode(digest).rstrip(b"=").decode()
        return computed == code_challenge

    async def create_authorization_code(
        self,
        client_id: str,
        redirect_uri: str,
        code_challenge: str,
        user_id: int,
    ) -> str:
        client = await self.get_client_or_raise(client_id)
        self._validate_redirect_uri(client, redirect_uri)
        code = secrets.token_urlsafe(48)
        await self.repo.create_authorization_code(
            code=code,
            client_id=client.id,
            user_id=user_id,
            code_challenge=code_challenge,
            redirect_uri=redirect_uri,
        )
        return code

    async def exchange_code(
        self,
        code: str,
        code_verifier: str,
        client_id: str,
        redirect_uri: str,
    ) -> dict:
        client = await self.get_client_or_raise(client_id)
        code_obj = await self.repo.get_authorization_code(code)

        if not code_obj:
            raise OAuthError("invalid_grant", "Authorization code not found or already used")

        if code_obj.client_id != client.id:
            raise OAuthError("invalid_grant", "Code does not belong to this client")

        if code_obj.redirect_uri != redirect_uri:
            raise OAuthError("invalid_grant", "redirect_uri mismatch")

        expires_at = datetime.fromisoformat(code_obj.expires_at)
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        if datetime.now(timezone.utc) > expires_at:
            raise OAuthError("invalid_grant", "Authorization code expired")

        if not self._verify_pkce(code_verifier, code_obj.code_challenge):
            raise OAuthError("invalid_grant", "PKCE verification failed")

        await self.repo.mark_code_used(code_obj)

        access_token = secrets.token_urlsafe(48)
        refresh_token = secrets.token_urlsafe(48)
        await self.repo.create_access_token(
            access_token=access_token,
            refresh_token=refresh_token,
            client_id=client.id,
            user_id=code_obj.user_id,
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": 3600,
        }

    async def refresh_access_token(self, refresh_token: str, client_id: str) -> dict:
        client = await self.get_client_or_raise(client_id)
        token_obj = await self.repo.get_by_refresh_token(refresh_token)

        if not token_obj or token_obj.client_id != client.id:
            raise OAuthError("invalid_grant", "Invalid refresh token")

        refresh_expires = datetime.fromisoformat(token_obj.refresh_token_expires_at)
        if refresh_expires.tzinfo is None:
            refresh_expires = refresh_expires.replace(tzinfo=timezone.utc)
        if datetime.now(timezone.utc) > refresh_expires:
            raise OAuthError("invalid_grant", "Refresh token expired")

        await self.repo.revoke_token(token_obj)

        new_access = secrets.token_urlsafe(48)
        new_refresh = secrets.token_urlsafe(48)
        await self.repo.create_access_token(
            access_token=new_access,
            refresh_token=new_refresh,
            client_id=client.id,
            user_id=token_obj.user_id,
        )

        return {
            "access_token": new_access,
            "refresh_token": new_refresh,
            "token_type": "bearer",
            "expires_in": 3600,
        }

    async def get_user_from_token(self, access_token: str):
        token_obj = await self.repo.get_by_access_token(access_token)
        if not token_obj:
            raise OAuthError("invalid_token", "Access token not found or revoked")

        expires_at = datetime.fromisoformat(token_obj.expires_at)
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        if datetime.now(timezone.utc) > expires_at:
            raise OAuthError("invalid_token", "Access token expired")

        user = await self.user_repo.get_by_id(token_obj.user_id)
        if not user or not user.is_active:
            raise OAuthError("invalid_token", "User not found or inactive")

        return user

    async def revoke(self, access_token: str) -> None:
        token_obj = await self.repo.get_by_access_token(access_token)
        if token_obj:
            await self.repo.revoke_token(token_obj)
