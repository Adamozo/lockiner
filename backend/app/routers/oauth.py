from fastapi import APIRouter, Depends, HTTPException, status, Request, Cookie
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from ..database import get_db
from ..dependencies import get_current_user
from ..models import User
from ..schemas.oauth import OAuthTokenRequest, OAuthTokenResponse, OAuthUserInfoResponse
from ..services.oauth import OAuthService, OAuthError
from ..services.auth import AuthService, InvalidTokenError, UserNotFoundError, UserInactiveError

router = APIRouter(prefix="/oauth", tags=["oauth"])

_bearer = HTTPBearer(auto_error=False)


async def get_current_user_cookie_or_bearer(
    db: AsyncSession = Depends(get_db),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer),
    scrooge_access_token: Optional[str] = Cookie(default=None),
) -> User:
    """Akceptuje token z nagłówka Bearer LUB z ciasteczka scrooge_access_token."""
    token = None
    if credentials:
        token = credentials.credentials
    elif scrooge_access_token:
        token = scrooge_access_token

    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    auth_service = AuthService(db)
    try:
        return await auth_service.get_current_user(token)
    except UserInactiveError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User account is inactive")
    except (InvalidTokenError, UserNotFoundError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")


async def get_oauth_service(db: AsyncSession = Depends(get_db)) -> OAuthService:
    return OAuthService(db)


@router.get("/authorize")
async def authorize(
    client_id: str,
    redirect_uri: str,
    code_challenge: str,
    response_type: str = "code",
    code_challenge_method: str = "S256",
    state: str | None = None,
    current_user: User = Depends(get_current_user_cookie_or_bearer),
    service: OAuthService = Depends(get_oauth_service),
):
    """
    Punkt wejścia OAuth. Wymaga zalogowanego użytkownika (Bearer token Lockinera).
    Zwraca redirect z kodem autoryzacyjnym.
    """
    if response_type != "code":
        raise HTTPException(status_code=400, detail="Only response_type=code supported")
    if code_challenge_method != "S256":
        raise HTTPException(status_code=400, detail="Only S256 code_challenge_method supported")

    try:
        code = await service.create_authorization_code(
            client_id=client_id,
            redirect_uri=redirect_uri,
            code_challenge=code_challenge,
            user_id=current_user.id,
        )
    except OAuthError as e:
        raise HTTPException(status_code=400, detail=e.description)

    separator = "&" if "?" in redirect_uri else "?"
    location = f"{redirect_uri}{separator}code={code}"
    if state:
        location += f"&state={state}"

    return RedirectResponse(url=location, status_code=302)


@router.post("/token", response_model=OAuthTokenResponse)
async def token(
    data: OAuthTokenRequest,
    service: OAuthService = Depends(get_oauth_service),
):
    """Wymiana authorization code → access token (grant_type=authorization_code lub refresh_token)."""
    try:
        if data.grant_type == "authorization_code":
            if not data.code or not data.code_verifier or not data.redirect_uri:
                raise HTTPException(status_code=400, detail="code, code_verifier and redirect_uri required")
            result = await service.exchange_code(
                code=data.code,
                code_verifier=data.code_verifier,
                client_id=data.client_id,
                redirect_uri=data.redirect_uri,
            )
        elif data.grant_type == "refresh_token":
            if not data.refresh_token:
                raise HTTPException(status_code=400, detail="refresh_token required")
            result = await service.refresh_access_token(
                refresh_token=data.refresh_token,
                client_id=data.client_id,
            )
        else:
            raise HTTPException(status_code=400, detail="Unsupported grant_type")
    except OAuthError as e:
        raise HTTPException(status_code=400, detail=e.description)

    return OAuthTokenResponse(**result)


@router.post("/revoke", status_code=204)
async def revoke(
    access_token: str,
    service: OAuthService = Depends(get_oauth_service),
):
    await service.revoke(access_token)


@router.get("/userinfo", response_model=OAuthUserInfoResponse)
async def userinfo(
    current_user: User = Depends(get_current_user),
    service: OAuthService = Depends(get_oauth_service),
):
    """
    Zwraca dane zalogowanego użytkownika.
    Akceptuje zarówno Lockiner JWT jak i OAuth access token.
    """
    return OAuthUserInfoResponse(
        sub=str(current_user.id),
        name=current_user.name,
        email_hash=current_user.email_hash,
        role=current_user.role,
    )
