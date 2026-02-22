import hashlib
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional

from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import User, Voucher
from ..schemas import UserCreate, TokenResponse
from ..repositories.user import UserRepository
from ..repositories.voucher import VoucherRepository
from ..config import get_settings

logger = logging.getLogger(__name__)

SECRET_KEY = get_settings().jwt_secret_key
if not SECRET_KEY:
    if get_settings().environment == "production":
        raise RuntimeError("JWT_SECRET_KEY environment variable is required in production")
    SECRET_KEY = "dev-only-secret-key-do-not-use-in-production"
    logger.warning("Using default JWT secret. Set JWT_SECRET_KEY for production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ---------------------------------------


class UserNotFoundError(Exception):
    def __init__(self):
        super().__init__("User not found")


class UserAlreadyExistsError(Exception):
    def __init__(self):
        super().__init__("User with this email already exists")


class InvalidCredentialsError(Exception):
    def __init__(self):
        super().__init__("Invalid email or password")


class InvalidTokenError(Exception):
    def __init__(self, message: str = "Invalid token"):
        super().__init__(message)


class UserInactiveError(Exception):
    def __init__(self):
        super().__init__("User account is inactive")


class InvalidVoucherError(Exception):
    def __init__(self, message: str = "Invalid or already used voucher"):
        super().__init__(message)


# ---------------------------------------


def hash_email(email: str) -> str:
    """Hash email for storage (one-way hash)."""
    normalized = email.lower().strip()
    return hashlib.sha256(normalized.encode()).hexdigest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    """Hash a password for storage."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT refresh token."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_two_factor_token(data: dict) -> str:
    """Create a short-lived JWT for 2FA verification."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=5)
    to_encode.update({"exp": expire, "type": "two_factor"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    """Decode and validate a JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        raise InvalidTokenError(str(e))


# ---------------------------------------


class AuthService:
    def __init__(self, db: AsyncSession):
        self.repository = UserRepository(db)
        self.voucher_repository = VoucherRepository(db)
        self.db = db

    async def validate_voucher(self, voucher_code: str) -> Voucher:
        """Validate a voucher code and return the voucher if valid."""
        voucher = await self.voucher_repository.get_by_code(voucher_code)
        if voucher is None or voucher.status != "available":
            raise InvalidVoucherError()
        return voucher

    async def register(self, data: UserCreate) -> User:
        """Register a new user with a valid voucher."""
        # First, validate the voucher
        voucher = await self.validate_voucher(data.voucher_code)

        email_hash = hash_email(data.email)

        if await self.repository.exists_by_email_hash(email_hash):
            raise UserAlreadyExistsError()

        user = User(
            email_hash=email_hash,
            password_hash=hash_password(data.password),
            name=data.name,
            language=data.language,
        )

        # Create the user first
        user = await self.repository.create(user)

        # Mark voucher as used
        await self.voucher_repository.mark_as_used(voucher, user.id)

        return user

    async def login(self, email: str, password: str) -> dict:
        """Authenticate user and return tokens, or 2FA challenge."""
        email_hash = hash_email(email)
        user = await self.repository.get_by_email_hash(email_hash)

        if user is None:
            raise InvalidCredentialsError()

        if not verify_password(password, user.password_hash):
            raise InvalidCredentialsError()

        if not user.is_active:
            raise UserInactiveError()

        if user.totp_enabled:
            two_factor_token = create_two_factor_token({"sub": str(user.id)})
            return {
                "requires_2fa": True,
                "two_factor_token": two_factor_token,
            }

        token_data = {"sub": str(user.id)}
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "requires_2fa": False,
        }

    async def verify_two_factor_login(self, two_factor_token: str, code: str) -> TokenResponse:
        """Complete 2FA login by verifying the TOTP/recovery code."""
        try:
            payload = decode_token(two_factor_token)

            if payload.get("type") != "two_factor":
                raise InvalidTokenError("Not a two-factor token")

            user_id = int(payload.get("sub"))
            user = await self.repository.get_by_id(user_id)

            if user is None:
                raise UserNotFoundError()

            if not user.is_active:
                raise UserInactiveError()

            from .two_factor import TwoFactorService, InvalidTwoFactorCodeError
            two_factor_service = TwoFactorService(self.db)

            if not await two_factor_service.verify_login_code(user, code):
                raise InvalidCredentialsError()

            token_data = {"sub": str(user.id)}
            access_token = create_access_token(token_data)
            refresh_token = create_refresh_token(token_data)

            return TokenResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            )

        except (JWTError, ValueError) as e:
            raise InvalidTokenError(str(e))

    async def refresh_tokens(self, refresh_token: str) -> TokenResponse:
        """Refresh access token using refresh token."""
        try:
            payload = decode_token(refresh_token)

            if payload.get("type") != "refresh":
                raise InvalidTokenError("Not a refresh token")

            user_id = int(payload.get("sub"))
            user = await self.repository.get_by_id(user_id)

            if user is None:
                raise UserNotFoundError()

            if not user.is_active:
                raise UserInactiveError()

            token_data = {"sub": str(user.id)}
            new_access_token = create_access_token(token_data)
            new_refresh_token = create_refresh_token(token_data)

            return TokenResponse(
                access_token=new_access_token,
                refresh_token=new_refresh_token,
                expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            )

        except (JWTError, ValueError) as e:
            raise InvalidTokenError(str(e))

    async def get_current_user(self, token: str) -> User:
        """Get the current user from an access token."""
        try:
            payload = decode_token(token)

            if payload.get("type") != "access":
                raise InvalidTokenError("Not an access token")

            user_id = int(payload.get("sub"))
            user = await self.repository.get_by_id(user_id)

            if user is None:
                raise UserNotFoundError()

            if not user.is_active:
                raise UserInactiveError()

            return user

        except (JWTError, ValueError) as e:
            raise InvalidTokenError(str(e))

    async def change_password(self, user_id: int, current_password: str, new_password: str) -> None:
        """Change user's password."""
        user = await self.repository.get_by_id(user_id)

        if user is None:
            raise UserNotFoundError()

        if not verify_password(current_password, user.password_hash):
            raise InvalidCredentialsError()

        user.password_hash = hash_password(new_password)
        await self.repository.update(user)

    async def get_user_by_id(self, user_id: int) -> User:
        """Get user by ID."""
        user = await self.repository.get_by_id(user_id)

        if user is None:
            raise UserNotFoundError()

        return user

    async def update_user(self, user_id: int, name: Optional[str] = None, language: Optional[str] = None) -> User:
        """Update user profile."""
        user = await self.repository.get_by_id(user_id)

        if user is None:
            raise UserNotFoundError()

        if name is not None:
            user.name = name

        if language is not None:
            user.language = language

        return await self.repository.update(user)
