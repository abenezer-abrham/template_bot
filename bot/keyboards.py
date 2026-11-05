from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config import WEBAPP_URL


def main_menu():
    kb = InlineKeyboardBuilder()
    kb.button(text="🔥 Open Showroom (1-of-1)", web_app=WebAppInfo(url=WEBAPP_URL))
    kb.button(text="⏱️ How 30-Min Lock Works", callback_data="claims_info")
    kb.button(text="📍 Boutique & Drop Location", callback_data="store_info")
    kb.adjust(1)
    return kb.as_markup()


def showroom_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="🔥 Open Showroom",
                                  web_app=WebAppInfo(url=WEBAPP_URL))]],
        resize_keyboard=True
    )


# Backward-compatible alias
booking_keyboard = showroom_keyboard
