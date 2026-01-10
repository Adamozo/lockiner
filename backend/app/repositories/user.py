from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone

from ..models import User


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: int) -> User | None:
        result = await self.db.execute(
            select(User).filter(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_by_email_hash(self, email_hash: str) -> User | None:
        result = await self.db.execute(
            select(User).filter(User.email_hash == email_hash)
        )
        return result.scalar_one_or_none()

    async def exists_by_email_hash(self, email_hash: str) -> bool:
        result = await self.db.execute(
            select(User).filter(User.email_hash == email_hash)
        )
        return result.scalar_one_or_none() is not None

    async def create(self, user: User) -> User:
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def update(self, user: User) -> User:
        user.updated_at = datetime.now(timezone.utc).isoformat()
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def delete(self, user: User) -> None:
        await self.db.delete(user)
        await self.db.commit()
