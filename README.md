# Telegram Bot Template (Botz)

Production-ready modular Telegram bot template built with `aiogram 3.x` and `SQLite` for local business services.

## Quick Start

1. **Clone & Set Up Environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Configure Settings**
   ```bash
   cp .env.example .env
   # Edit .env with your actual Telegram BOT_TOKEN and ADMIN_ID
   ```

3. **Run the Bot**
   ```bash
   python main.py
   ```

## Directory Structure
- `bot/`: Handlers, keyboards, states, middleware, and localization strings
- `services/`: Business logic, notifications, and scheduled reminders
- `db/`: Database connection and data access layer
- `deploy/`: Dockerfile and systemd service files
- `HANDOFF.md`: Context handoff file between development sessions
