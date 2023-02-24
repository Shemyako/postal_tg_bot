import asyncio
import logging
from sqlalchemy import insert, select
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
@dp.callback_query(lambda call: call.data == "menu")
async def menu_from_inline(call: types.CallbackQuery):
    try:
        await bot.edit_message_text("Вы перешли в меню", call.message.chat.id, call.message.message_id)
    except:
        pass
    await cmd_start(call)


@dp.message(commands=["start"])
@dp.message(text="Меню")
async def cmd_start(message: types.Message):
    # Если пользователь ещё не зарегистрирован
    if message.from_user.id not in config.whitelist:
        kb = [
            [types.KeyboardButton(text="Зарегистрироваться", request_contact=True)]
        ]
        keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True)
        await bot.send_message(message.from_user.id, "Вам нужно будет разегестрироваться. Для этого нужно предоставить номер телефона. Нажмите по кнопке ниже.", reply_markup=keyboard)

    else:
        # проверяем, есть ли на нём почта
        query = db.mails.select().where(db.mails.c.owner == message.from_user.id)
        answer =  await db.database.fetch_all(query)
        
        kb = [
            [types.KeyboardButton(text="Добавить почту")]
        ]

        # Если почта есть, то предлагаем отобразить их все
        if answer != []:
            kb.append([types.KeyboardButton(text="Список почт")])
            kb.append([types.KeyboardButton(text="Удалить почту")])
        
        keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True)
        await bot.send_message(message.from_user.id, "Приветик. Это меню:", reply_markup=keyboard)


@dp.message(content_types='contact')
async def contact_handler(message: types.Message):
    # print(message.contact)
    # query = db.customers.select().where(db.customers.c.tg_id == message.from_user.id)

    # answer =  await db.database.fetch_all(query)
    
    if message.from_user.id in config.whitelist:
        await message.answer("Вы уже зарегистрированы! Для работы введите /start")
    
    else:
        query = insert(db.customers)
        await db.database.execute(query, {"tg_id":message.contact.user_id, "phone":message.contact.phone_number, "status":0})
        await message.answer("Теперь Вы зарегистрированы! Для работы введите /start")
        config.whitelist.add(message.from_user.id)


dp.include_router(work_with_mail.router)
    

# Запуск процесса поллинга новых апдейтов
async def main():
    try:
        await db.database.connect()
        a = (await db.database.fetch_all(select(db.customers.c.tg_id)))
        
        for i in a:
            config.whitelist.add(*i.values())

        print(config.whitelist)
        await dp.start_polling(bot)
    except BaseException as e:
        print(e)
        await db.database.disconnect()


if __name__ == "__main__":
    asyncio.run(main())