# Project: Botz - Streetwear & Thrift Boutique Template
Goal: Automated Telegram showroom for second-hand, thrift, and boutique shoe/clothing shops (1-of-1 inventory, "Shop My Size" filter, instant claim/lock, live stock deduction, pickup vs delivery).
Stack: Python, aiogram 3.x, Telegram WebApp (HTML/JS/CSS), FastAPI, asyncpg, Supabase (PostgreSQL)
Run: python main.py
Done:
- Initialized modular structure and Git repositories
- Implemented core aiogram 3.x dispatcher with WebApp launcher and callback handlers
- Finalized business pivot from salon to 1-of-1 boutique/second-hand retail
- Built Streetwear/Thrift WebApp UI (Grailed/StockX dark aesthetic, "Shop My Size" filter tabs, 1-of-1 scarcity badges, 30-min claim modal with pickup vs delivery)
- Updated bot handlers and keyboards to handle showroom navigation and 30-min claim order confirmations
- Added SQLite-first DB layer, then upgraded to asyncpg / Supabase PostgreSQL
- Added FastAPI server (port 8000) serving live /api/items + webapp static files
- Full UI redesign: warm editorial dark aesthetic, lazy-load images, live fetch from API, smooth bottom sheet, skeleton loading
- schema.sql in db/ — run once in Supabase SQL Editor to initialize tables + seed
Next: Admin bot commands — /mark_paid <claim_id>, /stock (live inventory table), /expire (flush stale claims)
Bugs: None
Rules: short answers, don't rewrite working code, keep secrets out of markdown files

