from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from bot.keyboards import main_menu

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer("Welcome to Demo Salon! How can I help?",
                         reply_markup=main_menu())


@router.callback_query(F.data == "prices")
async def prices(call: CallbackQuery):
    await call.message.answer("Haircut: 20\nColoring: 50\nBeard trim: 10")
    await call.answer()


@router.callback_query(F.data == "info")
async def info(call: CallbackQuery):
    await call.message.answer("Open Mon-Sat, 9:00-19:00\nMain Street 12")
    await call.answer()


@router.callback_query(F.data == "book")
async def book(call: CallbackQuery):
    await call.message.answer("Booking is coming in the next step.")
    await call.answer()
