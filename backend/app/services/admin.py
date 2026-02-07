"""Admin service for voucher and user management."""

import uuid
import logging
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from ..models import User, Voucher
from ..repositories.user import UserRepository
from ..repositories.voucher import VoucherRepository

logger = logging.getLogger(__name__)


class VoucherNotFoundError(Exception):
    def __init__(self):
        super().__init__("Voucher not found")


class CannotUnblockUsedVoucherError(Exception):
    def __init__(self):
        super().__init__("Cannot unblock a used voucher")


class UserNotFoundError(Exception):
    def __init__(self):
        super().__init__("User not found")


class AdminService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
        self.voucher_repo = VoucherRepository(db)

    # ========================================================================
    # Voucher Management
    # ========================================================================

    async def get_all_vouchers(self) -> List[dict]:
        """Get all vouchers with user details."""
        vouchers = await self.voucher_repo.get_all()
        result = []
        for v in vouchers:
            data = {
                "id": v.id,
                "code": v.code,
                "status": v.status,
                "used_by_user_id": v.used_by_user_id,
                "used_by_name": None,
                "used_at": v.used_at,
                "created_at": v.created_at,
            }
            if v.used_by_user_id:
                user = await self.user_repo.get_by_id(v.used_by_user_id)
                if user:
                    data["used_by_name"] = user.name
            result.append(data)
        return result

    async def generate_vouchers(self, count: int) -> List[Voucher]:
        """Generate new UUID vouchers."""
        vouchers = []
        for _ in range(count):
            voucher = Voucher(code=str(uuid.uuid4()))
            vouchers.append(voucher)
        return await self.voucher_repo.create_many(vouchers)

    async def block_voucher(self, voucher_id: int) -> Voucher:
        """Block a voucher."""
        voucher = await self.voucher_repo.get_by_id(voucher_id)
        if voucher is None:
            raise VoucherNotFoundError()
        return await self.voucher_repo.block(voucher)

    async def unblock_voucher(self, voucher_id: int) -> Voucher:
        """Unblock a voucher (only if not used)."""
        voucher = await self.voucher_repo.get_by_id(voucher_id)
        if voucher is None:
            raise VoucherNotFoundError()
        if voucher.status == "used":
            raise CannotUnblockUsedVoucherError()
        return await self.voucher_repo.unblock(voucher)

    # ========================================================================
    # User Management
    # ========================================================================

    async def get_all_users(self) -> List[User]:
        """Get all users."""
        return await self.user_repo.get_all()

    async def block_user(self, user_id: int) -> User:
        """Deactivate a user."""
        user = await self.user_repo.get_by_id(user_id)
        if user is None:
            raise UserNotFoundError()
        user.is_active = False
        return await self.user_repo.update(user)

    async def unblock_user(self, user_id: int) -> User:
        """Reactivate a user."""
        user = await self.user_repo.get_by_id(user_id)
        if user is None:
            raise UserNotFoundError()
        user.is_active = True
        return await self.user_repo.update(user)

    async def set_user_role(self, user_id: int, role: str) -> User:
        """Change user role."""
        user = await self.user_repo.get_by_id(user_id)
        if user is None:
            raise UserNotFoundError()
        user.role = role
        return await self.user_repo.update(user)
