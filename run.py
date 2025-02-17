import asyncio

from aiogram import Bot, Dispatcher
from sqlalchemy import select

import config
from bot import mail_router, menu_router
from db import Base, Customer, async_session, engine
from log import logger

bot = Bot(token=config.BOT_TOKEN)

dp = Dispatcher()

dp.include_router(menu_router)
dp.include_router(mail_router)


async def main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    try:
        # Get customers from db
        async with async_session() as session:
            a = (await session.execute(select(Customer.tg_id))).all()

        # Get whitelist
        for i in a:
            config.whitelist.add(i.tg_id)

        await dp.start_polling(bot)
    except BaseException as e:
        logger.error(e)


if __name__ == "__main__":
    asyncio.run(main())
