from aiogram import F, Router, types
from aiogram.filters import Command
from sqlalchemy.ext.asyncio import AsyncSession

import config
from db import connection
from objects import Menu, User, UserModel

menu_router = Router()


@menu_router.callback_query(F.data == "menu")
async def menu_from_inline(call: types.CallbackQuery):
    try:
        await call.message.delete()
        # await bot.edit_message_text(
        #     "Вы перешли в меню",
        #     call.message.chat.id,
        #     call.message.message_id
        # )
    except BaseException:
        pass
    await cmd_start(call)


@menu_router.message(Command("start"))
@menu_router.message(F.text == "Меню")
@connection
async def cmd_start(message: types.Message, session: AsyncSession):
    """
    Отображение меню
    Если пользователь не зарегестрирован, ему предложат зарегестрироваться
    """
    await Menu.show(message=message)


@menu_router.message(F.content_type == "contact")
@connection
async def contact_handler(message: types.Message, session: AsyncSession):
    """
    При регистрации пользователь отправляет свой номер телефона.
    Создание аккаунта
    """
    # Есть ли в сете зарегестрированых пользователей
    if message.from_user.id in config.whitelist:
        return await message.answer(
            "Вы уже зарегистрированы! Для работы введите /start"
        )

    await User.create(
        data=UserModel(tg_id=message.from_user.id, phone=message.contact.phone_number)
    )

    return await message.answer("Теперь Вы зарегистрированы! Для работы введите /start")
