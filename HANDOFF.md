# Project: Botz - Streetwear & Thrift Boutique Template
Goal: Automated Telegram showroom for second-hand, thrift, and boutique shoe/clothing shops (1-of-1 inventory, "Shop My Size" filter, instant claim/lock, live stock deduction, pickup vs delivery).
Stack: Python, aiogram 3.x, Telegram WebApp (HTML/JS/CSS), FastAPI, asyncpg, Supabase (PostgreSQL)
Run: python main.py
Done:
- Initialized modular structure and Git repositories
- Established 1-of-1 boutique/second-hand retail as the core product model
- Built Streetwear/Thrift WebApp UI (warm editorial dark aesthetic, Shop My Size filters, 1-of-1 badges, 30-min claim modal, pickup vs delivery, GitHub Pages static fallback)
- Bot handlers and keyboards for showroom navigation and 30-min claim confirmation
- Supabase/asyncpg DB layer: items + claims tables, atomic lock check, expiry
- FastAPI server (port 8000): serves /api/items + webapp static files
- APScheduler: auto-expires stale claims every 5 minutes
- schema.sql: run once in Supabase SQL Editor to initialize + seed
- Admin commands: /stock (live table), /mark_paid <id>, /expire (manual flush), /add_item (FSM guided add)
- Pushed to GitHub: https://github.com/abenezer-abrham/template_bot
Next: Set ADMIN_ID in .env, enable GitHub Pages on repo (Settings → Pages → main /docs), connect Supabase DATABASE_URL
Bugs: None
Rules: short answers, don't rewrite working code, keep secrets out of markdown files

