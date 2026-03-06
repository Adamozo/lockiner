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

    def _generate_user_code(self) -> str:
        """Generates a human-friendly code like ABCD-1234."""
        import random
        import string
        letters = ''.join(random.choices(string.ascii_uppercase, k=4))
        digits = ''.join(random.choices(string.digits, k=4))
        return f"{letters}-{digits}"

    async def create_device_code(self, client_id: str) -> dict:
        client = await self.get_client_or_raise(client_id)
        device_code = secrets.token_urlsafe(48)
        user_code = self._generate_user_code()
        expires_in = 600
        await self.repo.create_device_code(
            device_code=device_code,
            user_code=user_code,
            client_id=client.id,
            expires_in_seconds=expires_in,
        )
        return {
            "device_code": device_code,
            "user_code": user_code,
            "verification_uri": "https://lockiner.com/device",
            "expires_in": expires_in,
            "interval": 5,
        }

    async def approve_device_code(self, user_code: str, user_id: int) -> None:
        obj = await self.repo.get_device_code_by_user_code(user_code.upper())
        if not obj:
            raise OAuthError("not_found", "Invalid user code")
        if obj.status != "pending":
            raise OAuthError("already_processed", "Code already used")
        expires_at = datetime.fromisoformat(obj.expires_at)
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        if datetime.now(timezone.utc) > expires_at:
            raise OAuthError("expired_token", "Code has expired")
        await self.repo.approve_device_code(obj, user_id)

    async def deny_device_code(self, user_code: str) -> None:
        obj = await self.repo.get_device_code_by_user_code(user_code.upper())
        if obj and obj.status == "pending":
            await self.repo.deny_device_code(obj)

    async def poll_device_token(self, device_code: str, client_id: str) -> dict:
        """Called by device while polling. Returns token or raises OAuthError."""
        client = await self.get_client_or_raise(client_id)
        obj = await self.repo.get_device_code_by_device(device_code)
        if not obj or obj.client_id != client.id:
            raise OAuthError("invalid_grant", "Invalid device_code")

        expires_at = datetime.fromisoformat(obj.expires_at)
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        if datetime.now(timezone.utc) > expires_at:
            raise OAuthError("expired_token", "Device code expired")

        if obj.status == "pending":
            raise OAuthError("authorization_pending", "User has not yet approved")
        if obj.status == "denied":
            raise OAuthError("access_denied", "User denied the request")

        # approved — issue tokens
        access_token = secrets.token_urlsafe(48)
        refresh_token = secrets.token_urlsafe(48)
        await self.repo.create_access_token(
            access_token=access_token,
            refresh_token=refresh_token,
            client_id=client.id,
            user_id=obj.user_id,
        )
        # mark device code as used (reuse denied)
        obj.status = "used"
        await self.db.commit()

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": 3600,
        }
