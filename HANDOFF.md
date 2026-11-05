# Project: Botz
Goal: Modular aiogram 3.x Telegram bot template for local business client sales (menus, bookings, FAQs, notifications)
Stack: Python, aiogram 3.x, SQLite
Run: python main.py
Done:
- Configured .env and .env.example with BOT_TOKEN and ADMIN_ID
- Implemented config.py using python-dotenv
- Implemented bot/keyboards.py with InlineKeyboardBuilder for main_menu()
- Implemented bot/handlers/start.py with /start command and callback handlers (prices, info, book)
- Implemented main.py with DefaultBotProperties and polling
Next: Paste real BOT_TOKEN into .env, test /start menu in Telegram, then build booking flow
Bugs: None
Rules: short answers, don't rewrite working code, keep secrets out of markdown files
