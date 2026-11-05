import json
from aiogram import Bot, Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from bot.keyboards import main_menu, showroom_keyboard
from services.claim_service import handle_claim

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
async def got_claim(message: Message, bot: Bot):
    try:
        data = json.loads(message.web_app_data.data)
        item_id = data.get("item_id", "")
        fulfillment = data.get("fulfillment", "pickup")
        contact = data.get("contact", "").strip() or None

        success, reply_text = await handle_claim(
            bot=bot,
            tg_user_id=message.from_user.id,
            tg_username=message.from_user.username,
            item_id=item_id,
            fulfillment=fulfillment,
            contact=contact,
        )
        await message.answer(reply_text, reply_markup=main_menu())
    except Exception:
        await message.answer(
            "✅ <b>Claim received!</b> Our team is reviewing your reservation.",
            reply_markup=main_menu(),
        )
