"""
FastAPI server — serves the WebApp UI + live inventory API.
Runs alongside the bot on API_PORT (default 8000).
"""
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from db.database import get_available_items

app = FastAPI(title="BOTZ API", docs_url=None, redoc_url=None)

WEBAPP_DIR = Path(__file__).parent.parent / "webapp"


@app.get("/api/items")
async def api_items(size: str = "ALL"):
    """Return available inventory, optionally filtered by size."""
    items = await get_available_items(size if size != "ALL" else None)
    return JSONResponse(content=items)


@app.get("/api/health")
async def health():
    return {"status": "ok"}


# Serve the WebApp as a static file (must come last — catches all other routes)
app.mount("/", StaticFiles(directory=str(WEBAPP_DIR), html=True), name="webapp")
