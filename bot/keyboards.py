from aiogram.utils.keyboard import InlineKeyboardBuilder


def main_menu():
    kb = InlineKeyboardBuilder()
    kb.button(text="📅 Book appointment", callback_data="book")
    kb.button(text="💰 Prices", callback_data="prices")
    kb.button(text="🕒 Hours & location", callback_data="info")
    kb.adjust(1)
    return kb.as_markup()
