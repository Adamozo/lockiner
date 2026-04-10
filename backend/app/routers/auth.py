from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..schemas import (
    UserCreate,
    UserResponse,
    UserUpdate,
    LoginRequest,
    TokenResponse,
    RefreshTokenRequest,
    PasswordChangeRequest,
    ResetPasswordWithDekRequest,
    LoginResponse,
    TwoFactorSetupResponse,
    TwoFactorVerifySetupRequest,
    TwoFactorVerifySetupResponse,
    TwoFactorDisableRequest,
    TwoFactorStatusResponse,
    TwoFactorVerifyLoginRequest,
    TwoFactorRegenerateRequest,
    TwoFactorRegenerateResponse,
)
from ..services.auth import (
    AuthService,
    UserAlreadyExistsError,
    InvalidCredentialsError,
    InvalidTokenError,
    UserInactiveError,
    UserNotFoundError,
    InvalidVoucherError,
)

from ..services.two_factor import (
    TwoFactorService,
    TwoFactorAlreadyEnabledError,
    TwoFactorNotEnabledError,
    TwoFactorSetupNotStartedError,
    InvalidTwoFactorCodeError,
)
from ..dependencies import get_current_user
from ..models import User

# ---------------------------------------

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

# ---------------------------------------


async def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(db)

# ---------------------------------------


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    data: UserCreate,
    service: AuthService = Depends(get_auth_service),
):
    """Register a new user with a valid voucher."""
    try:
        user = await service.register(data)
        return UserResponse(
            id=user.id,
            name=user.name,
            role=user.role,
            created_at=user.created_at,
            is_active=user.is_active,
            totp_enabled=user.totp_enabled or False,
            language=user.language,
        )

    except InvalidVoucherError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    except UserAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )


@router.post("/login", response_model=LoginResponse)
async def login(
    data: LoginRequest,
    service: AuthService = Depends(get_auth_service),
):
    """Authenticate user and return access/refresh tokens."""
    try:
        return await service.login(data.email, data.password)

    except InvalidCredentialsError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )

    except UserInactiveError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    current_user: User = Depends(get_current_user),
):
    """Logout user (client should discard tokens)."""
    # JWT tokens are stateless, so logout is handled client-side
    # In a more advanced implementation, you could add the token to a blacklist
    return None


@router.post("/refresh-token", response_model=TokenResponse)
async def refresh_token(
    data: RefreshTokenRequest,
    service: AuthService = Depends(get_auth_service),
):
    """Refresh access token using refresh token."""
    try:
        return await service.refresh_tokens(data.refresh_token)

    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )

    except UserInactiveError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
):
    """Get current authenticated user's information."""
    return UserResponse(
        id=current_user.id,
        name=current_user.name,
        role=current_user.role,
        created_at=current_user.created_at,
        is_active=current_user.is_active,
        totp_enabled=current_user.totp_enabled or False,
        language=current_user.language,
    )


@router.put("/me", response_model=UserResponse)
async def update_profile(
    data: UserUpdate,
    current_user: User = Depends(get_current_user),
    service: AuthService = Depends(get_auth_service),
):
    """Update current user's profile."""
    try:
        user = await service.update_user(current_user.id, name=data.name, language=data.language)
        return UserResponse(
            id=user.id,
            name=user.name,
            role=user.role,
            created_at=user.created_at,
            is_active=user.is_active,
            totp_enabled=user.totp_enabled or False,
            language=user.language,
        )

    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.post("/change-password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    data: PasswordChangeRequest,
    current_user: User = Depends(get_current_user),
    service: AuthService = Depends(get_auth_service),
):
    """Change current user's password and re-encrypted DEK."""
    try:
        await service.change_password(
            current_user.id,
            data.current_password,
            data.new_password,
            encrypted_dek=data.encrypted_dek,
            dek_salt=data.dek_salt,
        )
        return None

    except InvalidCredentialsError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )


@router.post("/reset-password-with-dek", status_code=status.HTTP_204_NO_CONTENT)
async def reset_password_with_dek(
    data: ResetPasswordWithDekRequest,
    service: AuthService = Depends(get_auth_service),
):
    """Reset password using recovery key (DEK re-encrypted client-side). No auth required."""
    try:
        await service.reset_password_with_dek(
            data.email,
            data.new_password,
            data.encrypted_dek,
            data.dek_salt,
        )
        return None

    except UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not found",
        )

    except UserInactiveError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )


# ============ Two-Factor Authentication Endpoints ============


async def get_two_factor_service(db: AsyncSession = Depends(get_db)) -> TwoFactorService:
    return TwoFactorService(db)


@router.post("/2fa/setup", response_model=TwoFactorSetupResponse)
async def setup_two_factor(
    current_user: User = Depends(get_current_user),
    service: TwoFactorService = Depends(get_two_factor_service),
):
    """Initiate 2FA setup - returns secret and provisioning URI."""
    try:
        result = await service.initiate_setup(current_user)
        return TwoFactorSetupResponse(**result)
    except TwoFactorAlreadyEnabledError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/2fa/verify-setup", response_model=TwoFactorVerifySetupResponse)
async def verify_two_factor_setup(
    data: TwoFactorVerifySetupRequest,
    current_user: User = Depends(get_current_user),
    service: TwoFactorService = Depends(get_two_factor_service),
):
    """Verify initial 2FA setup with first TOTP code. Returns recovery codes."""
    try:
        recovery_codes = await service.verify_setup(current_user, data.code)
        return TwoFactorVerifySetupResponse(recovery_codes=recovery_codes)
    except TwoFactorAlreadyEnabledError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except TwoFactorSetupNotStartedError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except InvalidTwoFactorCodeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/2fa/disable", status_code=status.HTTP_204_NO_CONTENT)
async def disable_two_factor(
    data: TwoFactorDisableRequest,
    current_user: User = Depends(get_current_user),
    service: TwoFactorService = Depends(get_two_factor_service),
):
    """Disable 2FA (requires valid TOTP or recovery code)."""
    try:
        await service.disable(current_user, data.code)
        return None
    except TwoFactorNotEnabledError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except InvalidTwoFactorCodeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/2fa/status", response_model=TwoFactorStatusResponse)
async def get_two_factor_status(
    current_user: User = Depends(get_current_user),
    service: TwoFactorService = Depends(get_two_factor_service),
):
    """Check 2FA status for current user."""
    result = await service.get_status(current_user)
    return TwoFactorStatusResponse(**result)


@router.post("/2fa/verify", response_model=LoginResponse)
async def verify_two_factor_login(
    data: TwoFactorVerifyLoginRequest,
    service: AuthService = Depends(get_auth_service),
):
    """Complete login with 2FA verification code. No auth required - uses temp token."""
    try:
        return await service.verify_two_factor_login(data.two_factor_token, data.code)
    except InvalidCredentialsError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid two-factor authentication code",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except UserInactiveError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )


@router.post("/2fa/regenerate-recovery", response_model=TwoFactorRegenerateResponse)
async def regenerate_recovery_codes(
    data: TwoFactorRegenerateRequest,
    current_user: User = Depends(get_current_user),
    service: TwoFactorService = Depends(get_two_factor_service),
):
    """Regenerate recovery codes (requires valid TOTP code)."""
    try:
        recovery_codes = await service.regenerate_recovery_codes(current_user, data.code)
        return TwoFactorRegenerateResponse(recovery_codes=recovery_codes)
    except TwoFactorNotEnabledError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except InvalidTwoFactorCodeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
