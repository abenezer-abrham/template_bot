from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from bot.keyboards import main_menu_keyboard

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    user_name = message.from_user.first_name if message.from_user else "there"
    await message.answer(
        f"Hello, {user_name}! How can we help you today?",
        reply_markup=main_menu_keyboard()
    )
