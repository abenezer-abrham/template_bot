"""
Business logic for item claims and 30-minute lock management.
"""
import logging
from aiogram import Bot
from config import ADMIN_ID
from db.database import create_claim, get_item, expire_stale_claims

log = logging.getLogger(__name__)


async def handle_claim(
    bot: Bot,
    tg_user_id: int,
    tg_username: str | None,
    item_id: str,
    fulfillment: str,
    contact: str | None,
) -> tuple[bool, str]:
    """
    Process a claim from the WebApp payload.
    Returns (success: bool, message: str).
    """
    item = await get_item(item_id)
    if not item:
        return False, "❌ Item not found. It may have already sold."

    claim_id = await create_claim(
        item_id=item_id,
        tg_user_id=tg_user_id,
        tg_username=tg_username,
        fulfillment=fulfillment,
        contact=contact or "N/A",
    )

    if claim_id is None:
        return False, (
            "⚡ <b>Someone just beat you to it!</b>\n\n"
            f"<i>{item['brand']} {item['title']} ({item['size']})</i> is currently "
            "locked by another buyer. It will free up if they don't pay within 30 minutes."
        )

    fulfillment_display = "🏬 In-Store Pickup" if fulfillment == "pickup" else "🚚 Local Delivery"

    # Notify admin
    if ADMIN_ID:
        try:
            user_tag = f"@{tg_username}" if tg_username else f"id:{tg_user_id}"
            admin_msg = (
                f"🔔 <b>New Claim — Claim #{claim_id}</b>\n\n"
                f"👕 <b>Item:</b> {item['brand']} {item['title']}\n"
                f"📏 <b>Size:</b> {item['size']}\n"
                f"💰 <b>Price:</b> {item['price']}\n"
                f"📦 <b>Fulfillment:</b> {fulfillment_display}\n"
                f"👤 <b>Buyer:</b> {user_tag}\n"
                f"📱 <b>Contact:</b> {contact or 'N/A'}\n\n"
                f"⏱️ <i>30-minute hold is active. Confirm payment to close the sale.</i>"
            )
            await bot.send_message(ADMIN_ID, admin_msg)
        except Exception as exc:
            log.warning("Failed to notify admin: %s", exc)

    success_msg = (
        f"✅ <b>1-of-1 Claim Reserved — #{claim_id}</b>\n\n"
        f"👕 <b>Piece:</b> {item['brand']} {item['title']}\n"
        f"📏 <b>Size:</b> {item['size']}\n"
        f"💰 <b>Price:</b> {item['price']}\n"
        f"📦 <b>Fulfillment:</b> {fulfillment_display}\n\n"
        f"⏱️ <i>This piece is locked for you for <b>30 minutes</b>. "
        f"Our team will reach out to confirm payment shortly!</i>"
    )
    return True, success_msg


async def run_expiry_pass() -> None:
    """Expire stale claims. Called by the APScheduler job."""
    expired = await expire_stale_claims()
    if expired:
        log.info("Expired %d stale claim(s).", expired)
