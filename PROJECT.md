# Project: Botz (Telegram Bot Template)

## Stack
- Python 3.12+
- Framework: aiogram 3.x
- Database: SQLite (async with aiosqlite)
- Scheduling: APScheduler
- Deployment: Docker / systemd

## Architecture & Layout
- `main.py`: Bot entrypoint & dispatcher startup
- `config.py`: Environment configuration via pydantic-settings
- `bot/handlers/`: Modular routers (start, booking, faq, admin)
- `bot/keyboards.py`: Button and inline markup factories
- `bot/texts/`: Client-specific copy and translations (en.json)
- `services/`: Business logic (booking_service, notifications, reminders)
- `db/`: Database initialization and SQL queries

## Key Decisions
- Zero hardcoded texts: all UI strings live in `bot/texts/en.json`
- Zero hardcoded secrets: all credentials loaded from `.env`
- Polling for local dev, webhooks / containerized for production
