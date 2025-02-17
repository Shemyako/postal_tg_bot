from aiogram import F, Router, types
from aiogram.utils.keyboard import InlineKeyboardBuilder

import config
from objects import Mail

mail_router = Router()


@mail_router.message(F.from_user.id.in_(config.whitelist) & F.text == "Добавить почту")
async def mail_creation(message: types.Message):
    """
    Обработчик добавления почт.
    Добавить могут либо те, у кого нет почт, либо VIP
    """
    mail_instance = Mail()
    kb = [[types.KeyboardButton(text="Меню")]]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        # one_time_keyboard=True
    )

    try:
        mail_name = await mail_instance.create(user_id=message.from_user.id)
    except BaseException:
        return await message.answer("У Вас уже есть одна почта.", reply_markup=keyboard)

    return await message.answer(
        f"`{mail_name}` \- Ваша почта", parse_mode="MarkdownV2", reply_markup=keyboard
    )


@mail_router.message(F.from_user.id.in_(config.whitelist) & F.text == "Список почт")
async def mail_showing(message: types.Message):
    """
    Обработка отображения всех почт.
    Высылается сообщение с указанием всех почт.
    Почты в режиме копирования
    """
    mail_instance = Mail()
    mails = await mail_instance.get_active_mails(user_id=message.from_user.id)

    kb = [[types.KeyboardButton(text="Меню")]]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        # one_time_keyboard=True
    )

    # Если почт нет
    if not mails:
        return await message.answer("Список почт пуст.", reply_markup=keyboard)

    # Оформляем почты для последующего вывода
    mails = "\n".join(["`" + i[0] + "@" + config.DOMEN + "`" for i in mails])

    await message.answer(
        f"Ваши почты\n{mails}", parse_mode="MarkdownV2", reply_markup=keyboard
    )


@mail_router.message(F.from_user.id.in_(config.whitelist) & F.text == "Удалить почту")
async def pre_mail_deleting(message: types.Message):
    """
    Генерируем клавиатуру с почтами для удаления и кнопкой Меню
    """
    mail_instance = Mail()
    mails = await mail_instance.get_active_mails(user_id=message.chat.id)

    # Если почт нет у пользователя активных
    if not mails:
        kb = [[types.KeyboardButton(text="Меню")]]
        keyboard = types.ReplyKeyboardMarkup(
            keyboard=kb,
            resize_keyboard=True,
            # one_time_keyboard=True
        )
        return await message.answer("У вас нет почт.", reply_markup=keyboard)

    # Генерируем клавиатуру с почтами
    builder = InlineKeyboardBuilder()
    for mail in mails:
        builder.row(
            types.InlineKeyboardButton(
                text=mail.name, callback_data=f"delete {mail.name}"
            )
        )

    builder.row(types.InlineKeyboardButton(text="Меню", callback_data="menu"))

    return await message.answer(
        "Нажмите почту для удаления.", reply_markup=builder.as_markup()
    )


@mail_router.callback_query(
    F.from_user.id.in_(config.whitelist) & (F.data.len() > 7) & (F.data[:6] == "delete")
)
async def mail_deleting(call: types.CallbackQuery):
    """
    Обработка удаления почты. Удалять могут только пользователи с статусом 1
    По факту не удаляем, а помечаем как неактивную
    """
    mail_instance = Mail()
    res = await mail_instance.deactivate(
        user_id=call.from_user.id, mail_name=call.data[7:]
    )

    match res:
        case 1:
            await call.answer(text="Почта удалена", show_alert=True)
        case 2:
            await call.answer(
                text="Удалить почту может только VIP аккаунт. Если хотите стать VIP, свяжитесь с администратором",
                show_alert=True,
            )
        case _:
            await call.answer(text="У Вас нет активной почты", show_alert=True)

    # Удаляем сообщение и заново его генерируем
    await call.message.delete()
    await pre_mail_deleting(call.message)
