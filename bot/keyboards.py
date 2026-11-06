from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config import WEBAPP_URL


def main_menu():
    kb = InlineKeyboardBuilder()
    # Prominent Store Launcher
    kb.button(text="🛍️ ሱቁን ክፈት (Open Store)", web_app=WebAppInfo(url=WEBAPP_URL))
    kb.button(text="👟 ጫማዎች (Shoes)", web_app=WebAppInfo(url=WEBAPP_URL))
    kb.button(text="🧥 ሁዲና ጃኬት (Apparel)", web_app=WebAppInfo(url=WEBAPP_URL))
    kb.button(text="💳 ክፍያና አያያዝ (Payment & Lock)", callback_data="claims_info")
    kb.button(text="📍 አድራሻና ሰዓት (Store Location)", callback_data="store_info")
    kb.adjust(1, 2, 2)
    return kb.as_markup()


def showroom_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🛍️ ሱቁን ክፈት (Open Store)", web_app=WebAppInfo(url=WEBAPP_URL))],
            [KeyboardButton(text="📍 አድራሻ (Location)", callback_data="store_info")]
        ],
        resize_keyboard=True
    )


# Backward-compatible alias
booking_keyboard = showroom_keyboard
