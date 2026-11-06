import json
from aiogram import Bot, Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from bot.keyboards import main_menu, showroom_keyboard
from services.claim_service import handle_claim

router = Router()

# High-fashion boutique banner
HERO_BANNER_URL = "https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=1000&q=80"


@router.message(CommandStart())
async def cmd_start(message: Message):
    caption = (
        "✨ <b>እንኳን ወደ ቦቲካ ኮኔክት በደህና መጡ!</b>\n"
        "✨ <b>Welcome to Boutique Connect // Archive Showroom</b>\n\n"
        "የተመረጡ ኦሪጅናል ጫማዎች፣ ሁዲዎች፣ ጃኬቶች እና 1-of-1 ብርቅዬ አልባሳት።\n"
        "Curated 1-of-1 streetwear, designer footwear, and vintage archive pieces.\n\n"
        "<b>ዋና ዋና አገልግሎቶች / Features:</b>\n"
        "• <b>6 ክፍሎች:</b> ጫማዎች፣ ሁዲዎች፣ ቲሸርቶች፣ ጃኬቶች፣ ሱሪዎችና ቆቦች\n"
        "• <b>የ 30 ደቂቃ መያዣ:</b> እቃውን ይዘው በቴሌብር ወይም በባንክ ይክፈሉ\n"
        "• <b>አማራጭ ማድረሻ:</b> ከሱቅ መውሰድ ወይም በሞተር ማድረስ (Delivery)\n"
        "• <b>ቋንቋ መቀየሪያ:</b> 🇪🇹 አማርኛ & 🇬🇧 English\n\n"
        "ከታች <b>🛍️ ሱቁን ክፈት (Open Store)</b> የሚለውን ተጭነው ይግቡ 👇"
    )

    try:
        await message.answer_photo(
            photo=HERO_BANNER_URL,
            caption=caption,
            reply_markup=main_menu()
        )
    except Exception:
        await message.answer(caption, reply_markup=main_menu())


@router.callback_query(F.data == "claims_info")
async def claims_info(call: CallbackQuery):
    text = (
        "💳 <b>የክፍያና የ 30 ደቂቃ መያዣ ሁኔታ / Payment & Hold Info:</b>\n\n"
        "1. <b>1-of-1 ልዩ እቃ:</b> ሁሉም እቃዎች አንድ ብቻ የቀረቡ ናቸው።\n"
        "2. <b>የ 30 ደቂቃ መያዣ:</b> በሾውሩሙ ውስጥ <b>ያዙ (Claim)</b> ሲሉ እቃው ለ 30 ደቂቃ ይቆለፋል፤ ሌላ ሰው ሊወስደው አይችልም።\n"
        "3. <b>ክፍያ (Payment):</b>\n"
        "   • <b>Telebirr:</b> 0911000000 (Boutique Shop)\n"
        "   • <b>CBE Account:</b> 1000XXXXXXXX (Boutique Retail)\n"
        "   • <b>በአካል:</b> ሱቅ መጥተው መክፈል ይችላሉ\n"
        "4. ክፍያ እንደፈጸሙ ደረሰኙን እዚህ ቻት ላይ በመላክ ያረጋግጡ!"
    )
    await call.message.answer(text, reply_markup=showroom_keyboard())
    await call.answer()


@router.callback_query(F.data == "store_info")
async def store_info(call: CallbackQuery):
    text = (
        "📍 <b>የሱቅ አድራሻና የስራ ሰዓት / Location & Hours:</b>\n\n"
        "🏬 <b>አድራሻ:</b> አዲስ አበባ፣ ቦሌ (ከመድኃኔዓለም ፊት ለፊት)\n"
        "🕒 <b>የስራ ሰዓት:</b> ከሰኞ – እሁድ (ከጠዋቱ 3:30 – ማታ 2:30)\n"
        "🚚 <b>ማድረሻ (Delivery):</b> አዲስ አበባ ውስጥ በፈጣን ሞተር እናደርሳለን\n"
        "📞 <b>ስልክ:</b> 0911000000 / @BoutiqueSupport"
    )
    await call.message.answer(text, reply_markup=showroom_keyboard())
    await call.answer()


@router.callback_query(F.data.in_({"prices", "info", "book"}))
async def legacy_fallback(call: CallbackQuery):
    await call.message.answer(
        "✨ ሱቁን ለመክፈት ከታች ያለውን ይጫኑ:",
        reply_markup=main_menu()
    )
    await call.answer()


@router.message(F.web_app_data)
async def got_claim(message: Message, bot: Bot):
    try:
        data = json.loads(message.web_app_data.data)
        item_id = data.get("item_id", "")
        title = data.get("title", "")
        brand = data.get("brand", "")
        price = data.get("price", "")
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

        ful_am = "🏬 ከሱቅ መውሰጃ" if fulfillment == "pickup" else "🚚 በሞተር ማድረሻ"

        receipt_msg = (
            f"✅ <b>እቃው ለ 30 ደቂቃ በተሳካ ሁኔታ ተይዟል!</b>\n"
            f"✅ <b>Item Locked for 30 Minutes!</b>\n\n"
            f"👕 <b>ዕቃ:</b> {brand} — {title}\n"
            f"💰 <b>ዋጋ:</b> {price}\n"
            f"📦 <b>መቀበያ:</b> {ful_am}\n"
            f"📱 <b>አድራሻ/ስልክ:</b> {contact or 'ያልተገለጸ'}\n\n"
            f"💳 <b>ክፍያ ለመፈጸም:</b>\n"
            f"• <b>Telebirr:</b> 0911000000\n"
            f"• <b>CBE Account:</b> 1000XXXXXXXX\n\n"
            f"<i>ክፍያ እንደፈጸሙ የደረሰኝ ስክሪንሾት (Screenshot) እዚህ ይላኩልን። ሻጩ ወዲያውኑ አረጋግጦ ይልክልዎታል!</i>"
        )
        await message.answer(receipt_msg, reply_markup=main_menu())
    except Exception:
        await message.answer(
            "✅ <b>እቃዎ ተይዟል!</b> ሻጩ በቅርቡ ያናግርዎታል።",
            reply_markup=main_menu(),
        )
