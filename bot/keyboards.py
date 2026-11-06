from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config import WEBAPP_URL


def main_menu():
    kb = InlineKeyboardBuilder()
    # Prominent Full Catalog Launch Button
    kb.button(text="🛍️ Open Store (All Departments)", web_app=WebAppInfo(url=WEBAPP_URL))
    kb.button(text="👟 Shoes", web_app=WebAppInfo(url=WEBAPP_URL))
    kb.button(text="🧥 Hoodies & Tees", web_app=WebAppInfo(url=WEBAPP_URL))
    kb.button(text="⏱️ How 30-Min Lock Works", callback_data="claims_info")
    kb.button(text="📍 Boutique & Store Details", callback_data="store_info")
    kb.adjust(1, 2, 2)
    return kb.as_markup()


def showroom_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🛍️ Open Boutique Store", web_app=WebAppInfo(url=WEBAPP_URL))],
            [KeyboardButton(text="📍 Hours & Location", callback_data="store_info")]
        ],
        resize_keyboard=True
    )


# Backward-compatible alias
booking_keyboard = showroom_keyboard
