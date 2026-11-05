from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config import WEBAPP_URL


def main_menu():
    kb = InlineKeyboardBuilder()
    kb.button(text="📅 Book appointment", callback_data="book")
    kb.button(text="💰 Prices", callback_data="prices")
    kb.button(text="🕒 Hours & location", callback_data="info")
    kb.adjust(1)
    return kb.as_markup()


def booking_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📅 Open booking form",
                                  web_app=WebAppInfo(url=WEBAPP_URL))]],
        resize_keyboard=True
    )
