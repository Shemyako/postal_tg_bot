from aiogram import types
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config import whitelist
from db import Mail, connection


class Menu:
    @classmethod
    @connection
    async def show(cls, session: AsyncSession, message: types.Message):
        # Если пользователь ещё не зарегистрирован
        if message.from_user.id not in whitelist:
            kb = [
                [types.KeyboardButton(text="Зарегистрироваться", request_contact=True)]
            ]
            keyboard = types.ReplyKeyboardMarkup(
                keyboard=kb,
                resize_keyboard=True,
                # one_time_keyboard=True
            )
            await message.answer(
                "Вам нужно будет разегестрироваться. "
                "Для этого нужно предоставить номер телефона. "
                "Нажмите по кнопке ниже.",
                reply_markup=keyboard,
            )

        # Пользователь уже зарегестрирован
        else:
            # проверяем, есть ли на нём почта
            query = select(Mail).where(
                Mail.owner == message.from_user.id, Mail.is_active.__eq__(True)
            )
            has_mails = (await session.execute(query)).all()

            kb = [[types.KeyboardButton(text="Добавить почту")]]

            # Если почта есть, то предлагаем отобразить их все
            if has_mails:
                kb.append([types.KeyboardButton(text="Список почт")])
                kb.append([types.KeyboardButton(text="Удалить почту")])

            keyboard = types.ReplyKeyboardMarkup(
                keyboard=kb,
                resize_keyboard=True,
                # one_time_keyboard=True
            )

            await message.answer("Приветик. Это меню:", reply_markup=keyboard)
