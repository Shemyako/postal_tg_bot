import asyncio
import logging
from sqlalchemy import insert
from aiogram import Bot, Dispatcher, types
from bot.handlers import work_with_mail
from bot import config
import db


# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)
# Объект бота
bot = Bot(token=config.BOT_TOKEN)
# Диспетчер
dp = Dispatcher()


# Хэндлер на команду /start
@dp.message(commands=["start"])
async def cmd_start(message: types.Message):
    query = db.customers.select().outerjoin(db.mails).where(db.customers.c.tg_id == message.from_user.id)

    answer =  await db.database.fetch_all(query)
    
    print((answer))
    
    # Если пользователь ещё не зарегистрирован
    if answer == []:
        kb = [
            [types.KeyboardButton(text="Зарегистрироваться", request_contact=True)]
        ]
        keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True)
        await message.answer("Вам нужно будет разегестрироваться. Для этого нужно предоставить номер телефона. Нажмите по кнопке ниже.", reply_markup=keyboard)

    else:
        kb = [
            [types.KeyboardButton(text="Добавить почту", request_contact=True)],
            [types.KeyboardButton(text="Список почт", request_contact=True)],
            [types.KeyboardButton(text="Зарегистрироваться", request_contact=True)]
        ]
        keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True)
        await message.answer("Приветик. Это меню:", reply_markup=keyboard)


@dp.message(content_types='contact')
async def contact_handler(message: types.Message):
    print(message.contact)
    query = db.customers.select().where(db.customers.c.tg_id == message.from_user.id)

    answer =  await db.database.fetch_all(query)
    
    if answer != []:
        await message.answer("Вы уже зарегистрированы! Для работы введите /start")
    
    else:
        query = insert(db.customers)
        await db.database.execute(query, {"tg_id":message.contact.user_id, "phone":message.contact.phone_number})
        await message.answer("Теперь Вы зарегистрированы! Для работы введите /start")


dp.include_router(work_with_mail.router)
    

# Запуск процесса поллинга новых апдейтов
async def main():
    try:
        await db.database.connect()
        await dp.start_polling(bot)
    except:
        await db.database.disconnect()


if __name__ == "__main__":
    asyncio.run(main())