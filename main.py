import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from config import BOT_TOKEN
from bot.handlers import start
from db.database import init_db, seed_items
from db.seed_data import INVENTORY
from services.claim_service import run_expiry_pass


async def main():
    logging.basicConfig(level=logging.INFO)

    # DB setup
    await init_db()
    await seed_items(INVENTORY)

    bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    # Scheduler: expire stale 30-min claims every 5 minutes
    scheduler = AsyncIOScheduler()
    scheduler.add_job(run_expiry_pass, "interval", minutes=5)
    scheduler.start()

    dp = Dispatcher()
    dp.include_router(start.router)

    await bot.delete_webhook(drop_pending_updates=True)
    try:
        await dp.start_polling(bot)
    finally:
        scheduler.shutdown(wait=False)


if __name__ == "__main__":
    asyncio.run(main())
