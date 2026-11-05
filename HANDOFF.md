# Project: Botz - Streetwear & Thrift Boutique Template
Goal: Automated Telegram showroom for second-hand, thrift, and boutique shoe/clothing shops (1-of-1 inventory, "Shop My Size" filter, instant claim/lock, live stock deduction, pickup vs delivery).
Stack: Python, aiogram 3.x, Telegram WebApp (HTML/JS/CSS), SQLite
Run: python main.py
Done:
- Initialized modular structure and Git repositories
- Implemented core aiogram 3.x dispatcher with WebApp launcher and callback handlers
- Finalized business pivot from salon to 1-of-1 boutique/second-hand retail
- Built Streetwear/Thrift WebApp UI (Grailed/StockX dark aesthetic, "Shop My Size" filter tabs, 1-of-1 scarcity badges, 30-min claim modal with pickup vs delivery)
- Updated bot handlers and keyboards to handle showroom navigation and 30-min claim order confirmations
- Added SQLite schema (items + claims tables), seed data, claim service with admin notification, 30-min lock expiry scheduler (APScheduler, every 5 min)
Next: Admin commands — /mark_paid <claim_id> to confirm payment, /stock to list current item status, /expire to manually flush stale claims
Bugs: None
Rules: short answers, don't rewrite working code, keep secrets out of markdown files

