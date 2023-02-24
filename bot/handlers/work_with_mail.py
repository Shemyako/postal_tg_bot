from aiogram import Router, types
from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
import db
import uuid
from sqlalchemy import insert, select, update, and_
from bot import config


user_status = {}


router = Router()  # [1]


@router.message(lambda message: message.from_user.id in config.whitelist and message.text=="Добавить почту")
async def mail_creation(message: types.Message):
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

    mails = uuid.uuid4()
    query = insert(db.mails)
    result = await db.database.execute(query, {"name":f"{mails}", "owner":message.from_user.id})

    await message.answer(f"`{mails}` \- Ваша почта", parse_mode="MarkdownV2", reply_markup=keyboard)
    

@router.message(lambda message: message.from_user.id in config.whitelist and message.text=="Список почт")
async def mail_showing(message: types.Message):
    query = select([db.mails.c.name]).where(
        and_(db.mails.c.owner == message.from_user.id,
            db.mails.c.is_active == True  
        )
    )

    mails =  await db.database.fetch_all(query)
    mails = "\n".join(["`" + i[0] + "`" for i in mails])

    kb = [[types.KeyboardButton(text="Меню")]]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True)
    
    # Если почт нет
    if not mails:
        return await message.answer("Список почт пуст.", reply_markup=keyboard)
    else:
        await message.answer(f"{mails}\nВаши почты", parse_mode="MarkdownV2", reply_markup=keyboard)


@router.message(lambda message: message.from_user.id in config.whitelist and message.text=="Удалить почту")
async def pre_mail_deleting(message: types.Message):
    query = select([db.mails.c.name]).where(
        and_(
            db.mails.c.owner == message.from_user.id,
            db.mails.c.is_active == True
        )
    )
    mails =  await db.database.fetch_all(query)

    if not mails:
        kb = [[types.KeyboardButton(text="Меню")]]
        keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True)
        return await message.answer("У вас нет почт.", reply_markup=keyboard)

    
    builder = InlineKeyboardBuilder()
    for i in mails:
        # print(i)
        builder.row(types.InlineKeyboardButton(
            text=i[0], callback_data=f"delete {i[0]}")
        )
    
    builder.row(types.InlineKeyboardButton(
        text="Меню", callback_data="menu")
    )

    await message.answer("Нажмите почту для удаления.", reply_markup=builder.as_markup())


@router.callback_query(lambda call: call.from_user.id in config.whitelist and len(call.data)>7 and  call.data[:6]=="delete")
async def mail_deleting(call: types.CallbackQuery):
    query = select([db.mails.c.id]).where(
        and_(
            db.mails.c.owner == call.from_user.id, 
            db.mails.c.name == call.data[7], 
            db.mails.c.is_active == True
        )
    )
    mails =  await db.database.fetch_one(query)

    if mails:
        print(mails['id'])
        query = update(db.mails).where(mails['id'] == db.mails.c.id).values(is_active = False)
        print(query)
        await db.database.execute(query)
    else:
        
        # Добавить всплывающее окно
        pass

    await call.message.delete()
    await pre_mail_deleting(call.message)