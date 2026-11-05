import json
from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from bot.keyboards import main_menu, showroom_keyboard

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    welcome_text = (
        "⚡ <b>Welcome to BOTZ Streetwear & Thrift Archive</b>\n\n"
        "Curated 1-of-1 vintage pieces, rare sneakers, and deadstock drops.\n\n"
        "• <b>Shop My Size:</b> Instant size filtering\n"
        "• <b>30-Minute Hold:</b> Claim any piece to reserve it while paying\n"
        "• <b>Pickup or Delivery:</b> Choose your preferred fulfillment\n\n"
        "Tap below to browse the live collection:"
    )
    await message.answer(welcome_text, reply_markup=main_menu())


@router.callback_query(F.data == "claims_info")
async def claims_info(call: CallbackQuery):
    text = (
        "⏱️ <b>How the 30-Minute Claim Works</b>\n\n"
        "1. Every piece is <b>1-of-1</b> (first come, first served).\n"
        "2. When you tap <b>Claim</b> in the showroom, the item is instantly locked for 30 minutes.\n"
        "3. You choose <b>Store Pickup</b> or <b>Local Delivery</b>.\n"
        "4. Complete payment via Telegram to secure your purchase before the 30-minute timer expires."
    )
    await call.message.answer(text, reply_markup=showroom_keyboard())
    await call.answer()


@router.callback_query(F.data == "store_info")
async def store_info(call: CallbackQuery):
    text = (
        "📍 <b>Boutique Location & Drop Schedule</b>\n\n"
        "🏬 <b>Store:</b> 104 Fashion District, Downtown\n"
        "🕒 <b>Hours:</b> Tue–Sun, 12:00 – 20:00\n"
        "📦 <b>Drop Day:</b> Every Friday at 18:00\n"
        "🚚 <b>Local Delivery:</b> Same-day delivery for all verified claims."
    )
    await call.message.answer(text, reply_markup=showroom_keyboard())
    await call.answer()


@router.callback_query(F.data.in_({"prices", "info", "book"}))
async def legacy_fallback(call: CallbackQuery):
    await call.message.answer(
        "⚡ Tap below to explore current inventory and prices:",
        reply_markup=main_menu()
    )
    await call.answer()


@router.message(F.web_app_data)
async def got_claim(message: Message):
    try:
        data = json.loads(message.web_app_data.data)
        title = data.get("title", data.get("service", "1-of-1 Piece"))
        brand = data.get("brand", "")
        size = data.get("size", "One Size")
        price = data.get("price", "TBD")
        fulfillment = data.get("fulfillment", "pickup").capitalize()
        contact = data.get("contact", "N/A")

        item_display = f"{brand} {title}".strip() if brand else title
        fulfillment_display = "🏬 In-Store Pickup" if fulfillment.lower() == "pickup" else "🚚 Local Delivery"

        text = (
            f"✅ <b>1-of-1 Claim Reserved!</b>\n\n"
            f"👕 <b>Piece:</b> {item_display}\n"
            f"📏 <b>Size:</b> {size}\n"
            f"💰 <b>Price:</b> {price}\n"
            f"📦 <b>Fulfillment:</b> {fulfillment_display}\n"
            f"📱 <b>Contact:</b> {contact}\n\n"
            f"⏱️ <i>This item is locked for you for <b>30 minutes</b>. "
            f"An admin will message you to confirm payment and dispatch!</i>"
        )
        await message.answer(text, reply_markup=main_menu())
    except Exception:
        await message.answer(
            "✅ <b>Claim received!</b> Our team is reviewing your reservation.",
            reply_markup=main_menu()
        )

