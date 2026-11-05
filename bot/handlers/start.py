import json
from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from bot.keyboards import main_menu, booking_keyboard

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
    await call.message.answer("Tap the button below to choose your time:",
                              reply_markup=booking_keyboard())
    await call.answer()


@router.message(F.web_app_data)
async def got_booking(message: Message):
    try:
        data = json.loads(message.web_app_data.data)
        service = data.get("service", "Service")
        date = data.get("date", "Unknown date")
        time = data.get("time", "Unknown time")
        await message.answer(
            f"Request received ✅\n{service} on {date} at {time}",
            reply_markup=main_menu()
        )
    except Exception:
        await message.answer(
            "Request received ✅",
            reply_markup=main_menu()
        )
