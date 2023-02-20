from aiogram import Router, types
from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
import db


user_status = {}


router = Router()  # [1]


@router.callback_query(text="mail_creation")
async def mail_creation(callback: types.CallbackQuery):
    pass
