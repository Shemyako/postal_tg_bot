from aiogram import Router, types
from aiogram.types import ReplyKeyboardMarkup
from aiogram.methods import AnswerCallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
import db
import uuid
from sqlalchemy import insert, select, update, and_
from bot import config

router = Router()  # [1]


@router.message(lambda message: message.from_user.id in config.whitelist and message.text=="Добавить почту")
async def mail_creation(message: types.Message):
    """
    Обработчик добавления почт. Добавить могут либо те, у кого нет почт, либо VIP
    """
    # Получаем активные почты пользователя
    query = select([db.customers.c.status, db.mails.c.owner]).join(db.customers).where(
        and_(db.mails.c.owner == message.from_user.id,
            db.mails.c.is_active == True
        )
    )
    mails =  await db.database.fetch_all(query)

    kb = [[types.KeyboardButton(text="Меню")]]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True)

    # Если уже есть почты и статус обычный,
    # то больше почту создать не дадим
    if mails and mails[0][0] == 0:
        return await message.answer("У Вас уже есть одна почта.", reply_markup=keyboard)

    # Если почт нет / пользователь - VIP
    mails = uuid.uuid4()
    query = insert(db.mails)
    result = await db.database.execute(query, {"name":f"{mails}", "owner":message.from_user.id})

    return await message.answer(f"`{mails}` \- Ваша почта", parse_mode="MarkdownV2", reply_markup=keyboard)
    

@router.message(lambda message: message.from_user.id in config.whitelist and message.text=="Список почт")
async def mail_showing(message: types.Message):
    """
    Обработка отображения всех почт. Высылается сообщение с указанием всех почт. Почты в режиме копирования
    """
    # Получаем почты
    query = select([db.mails.c.name]).where(
        and_(db.mails.c.owner == message.from_user.id,
            db.mails.c.is_active == True  
        )
    )
    mails =  await db.database.fetch_all(query)
    # Оформляем почты для последующего вывода
    mails = "\n".join(["`" + i[0] + "`" for i in mails])

    kb = [[types.KeyboardButton(text="Меню")]]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True)
    
    # Если почт нет
    if not mails:
        return await message.answer("Список почт пуст.", reply_markup=keyboard)
    else:
        await message.answer(f"Ваши почты\n{mails}", parse_mode="MarkdownV2", reply_markup=keyboard)


@router.message(lambda message: message.from_user.id in config.whitelist and message.text=="Удалить почту")
async def pre_mail_deleting(message: types.Message):
    """
    Генерируем клавиатуру с почтами для удаления и кнопкой Меню
    """

    query = select([db.mails.c.name]).where(
        and_(
            db.mails.c.owner == message.chat.id,
            db.mails.c.is_active == True
        )
    )
    mails =  await db.database.fetch_all(query)

    # Если почт нет у пользователя активных
    if not mails:
        kb = [[types.KeyboardButton(text="Меню")]]
        keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True)
        return await message.answer("У вас нет почт.", reply_markup=keyboard)

    # Генерируем клавиатуру с почтами
    builder = InlineKeyboardBuilder()
    for i in mails:
        builder.row(types.InlineKeyboardButton(
            text=i[0], callback_data=f"delete {i[0]}")
        )
    
    builder.row(types.InlineKeyboardButton(
        text="Меню", callback_data="menu")
    )

    return await message.answer("Нажмите почту для удаления.", reply_markup=builder.as_markup())


@router.callback_query(lambda call: call.from_user.id in config.whitelist and len(call.data)>7 and  call.data[:6]=="delete")
async def mail_deleting(call: types.CallbackQuery):
    """
    Обработка удаления почты. Удалять могут только пользователи с статусом 1
    По факту не удаляем, а помечаем как неактивную
    """
    # Получаем почтовый ящик и статус пользователя
    query = select([db.mails.c.id, db.customers.c.status]).join(db.customers).where(
        and_(
            db.mails.c.owner == call.from_user.id, 
            db.mails.c.name == call.data[7:], 
            db.mails.c.is_active == True
        )
    )
    
    mails =  await db.database.fetch_one(query)
    
    # Если есть требуемая почта
    if mails:
        # Если пользователь VIP
        if mails['status'] == 1:
            query = update(db.mails).where(mails['id'] == db.mails.c.id).values(is_active = False)
            await db.database.execute(query)
            await call.answer(text="Почта удалена", show_alert=True)
        # Если не VIP
        else:
            await call.answer(text="Удалить почту может только VIP аккаунт. Если хотите стать VIP, свяжитесь с администратором", show_alert=True)
    else:
        await call.answer(text="У Вас нет активной почты", show_alert=True)
    
    # Удаляем сообщение и заново его генерируем
    await call.message.delete()
    await pre_mail_deleting(call.message)