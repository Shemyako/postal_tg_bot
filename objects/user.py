from pydantic import BaseModel
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from db import Customer, connection
from config import whitelist


class UserModel(BaseModel):
    tg_id: int
    status: int = 0
    phone: str


class User:
    @classmethod
    @connection
    async def _get_status(cls, session: AsyncSession, user_id: int):
        query = (select(Customer.status).where(Customer.id == user_id)).scalar()

        return (await session.execute(query)).scalar()

    @classmethod
    @connection
    async def create(cls, session: AsyncSession, data: UserModel):
        query = insert(Customer)
        await session.execute(
            query,
            {
                "tg_id": data.tg_id,
                "phone": data.phone,
                "status": data.status,
            },
        )
        await session.commit()

        whitelist.add(data.tg_id)
