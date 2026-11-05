# Project: Botz
Goal: Modular aiogram 3.x Telegram bot template for local business client sales (menus, bookings, FAQs, notifications)
Stack: Python, aiogram 3.x, Telegram WebApp (HTML/JS)
Run: python main.py
Done:
- Created webapp/index.html with auto-date min limit and tg.close() on confirm
- Added WEBAPP_URL to .env, .env.example, and config.py
- Added booking_keyboard() with WebAppInfo in bot/keyboards.py
- Updated bot/handlers/start.py with book callback and F.web_app_data receiver
- Prepared standalone repository at ~/Documents/botz/salon-webapp ready for GitHub Pages
Next: Push salon-webapp to GitHub and enable Pages, set real WEBAPP_URL in .env, then connect SQLite database for storing bookings
Bugs: None
Rules: short answers, don't rewrite working code, keep secrets out of markdown files
