import json
from aiogram import Bot, Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from bot.keyboards import main_menu, showroom_keyboard
from services.claim_service import handle_claim

router = Router()

# Editorial boutique fashion banner image
HERO_BANNER_URL = "https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=1200&q=85"


@router.message(CommandStart())
async def cmd_start(message: Message):
    caption = (
        "✨ <b>Welcome to Boutique Connect // Archive Showroom</b>\n\n"
        "Your verified digital retail showroom for 1-of-1 streetwear, designer footwear, "
        "outerwear, and vintage archive pieces.\n\n"
        "<b>What you can do:</b>\n"
        "• <b>Explore 6 Departments:</b> Shoes, Hoodies, Tees, Jackets, Pants & Accessories\n"
        "• <b>Live Search & Size Filters:</b> Find your exact fit in seconds\n"
        "• <b>Instant 30-Min Lock:</b> Claim any piece to freeze stock while finalizing order\n"
        "• <b>Flexible Fulfillment:</b> Boutique in-store pickup or local courier delivery\n\n"
        "Tap <b>Open Store</b> below to enter the live showroom 👇"
    )

    try:
        await message.answer_photo(
            photo=HERO_BANNER_URL,
            caption=caption,
            reply_markup=main_menu()
        )
    except Exception:
        # Fallback to text message if photo fails to load
        await message.answer(caption, reply_markup=main_menu())


@router.callback_query(F.data == "claims_info")
async def claims_info(call: CallbackQuery):
    text = (
        "⏱️ <b>How the 30-Minute Claim Works</b>\n\n"
        "1. <b>1-of-1 Scarcity:</b> Every piece listed in our boutique showroom is physically unique.\n"
        "2. <b>Instant Reservation:</b> When you tap <b>Claim</b> in the Mini App, the item is locked for 30 minutes so no one else can grab it.\n"
        "3. <b>Fulfillment Choice:</b> Select <b>Store Pickup</b> or <b>Courier Delivery</b>.\n"
        "4. <b>Verification:</b> You finalize payment via Telegram chat before the 30-minute reservation expires."
    )
    await call.message.answer(text, reply_markup=showroom_keyboard())
    await call.answer()


@router.callback_query(F.data == "store_info")
async def store_info(call: CallbackQuery):
    text = (
        "📍 <b>Boutique Location & Schedule</b>\n\n"
        "🏬 <b>Store:</b> 104 Fashion District, Downtown Boutique Strip\n"
        "🕒 <b>Hours:</b> Tuesday – Sunday, 11:00 AM – 8:00 PM\n"
        "📦 <b>Drop Schedule:</b> Fresh 1-of-1 archive drops every Friday at 6:00 PM\n"
        "🚚 <b>Delivery:</b> Same-day courier dispatch for verified city orders."
    )
    await call.message.answer(text, reply_markup=showroom_keyboard())
    await call.answer()


@router.callback_query(F.data.in_({"prices", "info", "book"}))
async def legacy_fallback(call: CallbackQuery):
    await call.message.answer(
        "✨ Tap below to explore the live boutique catalog:",
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
