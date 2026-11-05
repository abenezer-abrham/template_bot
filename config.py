import os
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN   = os.getenv("BOT_TOKEN")
ADMIN_ID    = int(os.getenv("ADMIN_ID", "0"))
WEBAPP_URL  = os.getenv("WEBAPP_URL", "http://localhost:8000")
DATABASE_URL = os.getenv("DATABASE_URL")       # Supabase postgres:// connection string
API_HOST    = os.getenv("API_HOST", "0.0.0.0")
API_PORT    = int(os.getenv("API_PORT", "8000"))
