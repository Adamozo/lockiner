from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone
from typing import List

from ..models import Voucher


class VoucherRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_code(self, code: str) -> Voucher | None:
        """Get voucher by code."""
        result = await self.db.execute(
            select(Voucher).filter(Voucher.code == code)
        )
        return result.scalar_one_or_none()

    async def get_unused_by_code(self, code: str) -> Voucher | None:
        """Get unused voucher by code."""
        result = await self.db.execute(
            select(Voucher).filter(
                Voucher.code == code,
                Voucher.used_by_user_id.is_(None)
            )
        )
        return result.scalar_one_or_none()

    async def mark_as_used(self, voucher: Voucher, user_id: int) -> Voucher:
        """Mark voucher as used by a user."""
        voucher.status = "used"
        voucher.used_by_user_id = user_id
        voucher.used_at = datetime.now(timezone.utc).isoformat()
        await self.db.commit()
        await self.db.refresh(voucher)
        return voucher

    async def create(self, voucher: Voucher) -> Voucher:
        """Create a new voucher."""
        self.db.add(voucher)
        await self.db.commit()
        await self.db.refresh(voucher)
        return voucher

    async def create_many(self, vouchers: List[Voucher]) -> List[Voucher]:
        """Create multiple vouchers."""
        self.db.add_all(vouchers)
        await self.db.commit()
        for voucher in vouchers:
            await self.db.refresh(voucher)
        return vouchers

    async def get_all(self) -> List[Voucher]:
        """Get all vouchers."""
        result = await self.db.execute(select(Voucher))
        return list(result.scalars().all())

    async def get_unused(self) -> List[Voucher]:
        """Get all unused vouchers."""
        result = await self.db.execute(
            select(Voucher).filter(Voucher.used_by_user_id.is_(None))
        )
        return list(result.scalars().all())

    async def get_by_id(self, voucher_id: int) -> Voucher | None:
        """Get voucher by ID."""
        result = await self.db.execute(
            select(Voucher).filter(Voucher.id == voucher_id)
        )
        return result.scalar_one_or_none()

    async def block(self, voucher: Voucher) -> Voucher:
        """Block a voucher."""
        voucher.status = "blocked"
        await self.db.commit()
        await self.db.refresh(voucher)
        return voucher

    async def unblock(self, voucher: Voucher) -> Voucher:
        """Unblock a voucher (only if not used)."""
        voucher.status = "available"
        await self.db.commit()
        await self.db.refresh(voucher)
        return voucher
