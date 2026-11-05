from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def main_menu_keyboard() -> ReplyKeyboardMarkup:
    keyboard = [
        [KeyboardButton(text="📅 Book"), KeyboardButton(text="💼 Services")],
        [KeyboardButton(text="🕒 Hours"), KeyboardButton(text="📍 Location")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
