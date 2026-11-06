import asyncio
import logging
import uvicorn
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from config import BOT_TOKEN, API_HOST, API_PORT
from bot.handlers import start, admin
from db.database import init_db, seed_items
from db.seed_data import INVENTORY
from services.claim_service import run_expiry_pass
from services.api import app as fastapi_app


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

    # Dispatcher with FSM storage (for /add_item conversation)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(admin.router)   # admin first (more specific filters)
    dp.include_router(start.router)

    await bot.delete_webhook(drop_pending_updates=True)

    # Set persistent chat menu button to launch the Mini App
    try:
        from aiogram.types import MenuButtonWebApp, WebAppInfo
        from config import WEBAPP_URL
        await bot.set_chat_menu_button(
            menu_button=MenuButtonWebApp(
                text="🔥 Showroom",
                web_app=WebAppInfo(url=WEBAPP_URL)
            )
        )
    except Exception as e:
        logging.warning("Could not set chat menu button: %s", e)


    # FastAPI runs alongside bot in the same event loop
    api_config = uvicorn.Config(
        fastapi_app,
        host=API_HOST,
        port=API_PORT,
        log_level="warning",
    )
    api_server = uvicorn.Server(api_config)

    try:
        await asyncio.gather(
            dp.start_polling(bot),
            api_server.serve(),
        )
    finally:
        scheduler.shutdown(wait=False)


if __name__ == "__main__":
    asyncio.run(main())
