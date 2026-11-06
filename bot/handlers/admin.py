"""
Admin-only bot commands. All handlers check ADMIN_ID before executing.
Commands:
  /stock                — live inventory table (all items + status)
  /mark_paid <claim_id> — confirm payment, mark item sold
  /expire               — manually flush all stale claims
  /add_item             — guided item add via conversation
"""
import logging
import uuid
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from config import ADMIN_ID
from db.database import (
    get_all_items_stock,
    mark_claim_paid,
    get_claim,
    expire_stale_claims,
    add_item,
)

log = logging.getLogger(__name__)
router = Router()


def _is_admin(message: Message) -> bool:
    return ADMIN_ID and message.from_user.id == ADMIN_ID


def _guard(msg: Message) -> bool:
    """Return True and silently ignore if not admin."""
    if not _is_admin(msg):
        return False
    return True


# ── /stock ────────────────────────────────────────────────────────────────────

@router.message(Command("stock"))
async def cmd_stock(message: Message):
    if not _guard(message):
        return
    items = await get_all_items_stock()
    if not items:
        await message.answer("📦 No items in inventory yet.")
        return

    lines = ["📦 <b>Live Inventory</b>\n"]
    for item in items:
        if not item["available"]:
            status = "🔴 SOLD"
        elif item["claim_id"]:
            buyer = f"@{item['tg_username']}" if item["tg_username"] else "unknown"
            status = f"🔒 LOCKED — {buyer} (Claim #{item['claim_id']})"
        else:
            status = "🟢 AVAILABLE"

        lines.append(
            f"<b>{item['brand']} — {item['title']}</b>\n"
            f"  Size: {item['size']}  ·  {item['price']}\n"
            f"  {status}\n"
        )

    # Telegram message limit is 4096 chars — split if needed
    text = "\n".join(lines)
    if len(text) <= 4096:
        await message.answer(text)
    else:
        for chunk in [text[i:i+4000] for i in range(0, len(text), 4000)]:
            await message.answer(chunk)


# ── /mark_paid ────────────────────────────────────────────────────────────────

@router.message(Command("mark_paid"))
async def cmd_mark_paid(message: Message):
    if not _guard(message):
        return

    parts = message.text.split(maxsplit=1)
    if len(parts) < 2 or not parts[1].strip().isdigit():
        await message.answer(
            "Usage: <code>/mark_paid &lt;claim_id&gt;</code>\n"
            "Example: <code>/mark_paid 7</code>"
        )
        return

    claim_id = int(parts[1].strip())
    claim = await get_claim(claim_id)

    if not claim:
        await message.answer(f"❌ Claim #{claim_id} not found.")
        return

    if claim["status"] != "pending":
        await message.answer(
            f"⚠️ Claim #{claim_id} is already <b>{claim['status']}</b>.\n"
            "Only pending claims can be marked paid."
        )
        return

    success = await mark_claim_paid(claim_id)
    if success:
        buyer = f"@{claim['tg_username']}" if claim["tg_username"] else f"User {claim['tg_user_id']}"
        await message.answer(
            f"✅ <b>Claim #{claim_id} marked PAID</b>\n\n"
            f"Item is now sold and removed from the showroom.\n"
            f"Buyer: {buyer}\n"
            f"Fulfillment: {claim['fulfillment'].capitalize()}"
        )
    else:
        await message.answer(f"❌ Failed to mark Claim #{claim_id} as paid. It may have already expired.")


# ── /expire ───────────────────────────────────────────────────────────────────

@router.message(Command("expire"))
async def cmd_expire(message: Message):
    if not _guard(message):
        return
    count = await expire_stale_claims()
    if count:
        await message.answer(f"⏱️ Expired <b>{count}</b> stale claim(s). Those items are back in stock.")
    else:
        await message.answer("✅ No stale claims to expire right now.")


# ── /add_item (FSM conversation) ──────────────────────────────────────────────

class AddItem(StatesGroup):
    brand   = State()
    title   = State()
    size    = State()
    price   = State()
    badge   = State()
    image   = State()


@router.message(Command("add_item"))
async def cmd_add_item_start(message: Message, state: FSMContext):
    if not _guard(message):
        return
    await state.clear()
    await message.answer(
        "➕ <b>Add a new item</b>\n\n"
        "I'll ask a few questions. Send /cancel at any point to abort.\n\n"
        "Step 1/6 — <b>Brand name?</b> (e.g. Nike, Stüssy)"
    )
    await state.set_state(AddItem.brand)


@router.message(Command("cancel"), AddItem)
async def cmd_add_item_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Cancelled.")


@router.message(AddItem.brand)
async def add_brand(message: Message, state: FSMContext):
    await state.update_data(brand=message.text.strip())
    await message.answer("Step 2/6 — <b>Item title?</b> (e.g. Dunk Low Retro 'Panda')")
    await state.set_state(AddItem.title)


@router.message(AddItem.title)
async def add_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text.strip())
    await message.answer("Step 3/6 — <b>Size?</b> (e.g. M, L, XL, US 10)")
    await state.set_state(AddItem.size)


@router.message(AddItem.size)
async def add_size(message: Message, state: FSMContext):
    await state.update_data(size=message.text.strip())
    await message.answer("Step 4/6 — <b>Price?</b> (e.g. $120)")
    await state.set_state(AddItem.price)


@router.message(AddItem.price)
async def add_price(message: Message, state: FSMContext):
    await state.update_data(price=message.text.strip())
    await message.answer(
        "Step 5/6 — <b>Badge label?</b>\n"
        "Common choices: 1-OF-1, DEADSTOCK, ARCHIVE, GRAIL, VINTAGE\n"
        "(or type your own)"
    )
    await state.set_state(AddItem.badge)


@router.message(AddItem.badge)
async def add_badge(message: Message, state: FSMContext):
    badge_text = message.text.strip().upper()
    # Auto-assign badge_class
    if "GRAIL" in badge_text:
        badge_class = "grail"
    elif "ARCHIVE" in badge_text or "VINTAGE" in badge_text:
        badge_class = "archive"
    else:
        badge_class = "one-of-one"
    await state.update_data(badge=badge_text, badge_class=badge_class)
    await message.answer(
        "Step 6/6 — <b>Image URL?</b>\n"
        "Paste a direct image link (Unsplash, Imgur, etc.)\n"
        "Or send <code>skip</code> to leave it blank."
    )
    await state.set_state(AddItem.image)


@router.message(AddItem.image)
async def add_image(message: Message, state: FSMContext):
    raw = message.text.strip()
    image_url = None if raw.lower() == "skip" else raw
    data = await state.get_data()
    await state.clear()

    item = {
        "id":         f"botz-{uuid.uuid4().hex[:8]}",
        "brand":      data["brand"],
        "title":      data["title"],
        "size":       data["size"],
        "price":      data["price"],
        "badge":      data["badge"],
        "badge_class": data["badge_class"],
        "image_url":  image_url,
    }

    await add_item(item)

    await message.answer(
        f"✅ <b>Item added!</b>\n\n"
        f"🏷 ID: <code>{item['id']}</code>\n"
        f"👕 {item['brand']} — {item['title']}\n"
        f"📏 Size: {item['size']}  ·  💰 {item['price']}\n"
        f"🔖 Badge: {item['badge']}\n\n"
        f"It's now live in the showroom."
    )
