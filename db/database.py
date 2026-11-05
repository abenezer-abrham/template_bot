"""
Database layer: schema init and CRUD for items & claims.
"""
import aiosqlite
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "botz.db"


async def init_db() -> None:
    """Create tables if they don't exist."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS items (
                id          TEXT PRIMARY KEY,
                brand       TEXT NOT NULL,
                title       TEXT NOT NULL,
                size        TEXT NOT NULL,
                price       TEXT NOT NULL,
                badge       TEXT NOT NULL,
                badge_class TEXT NOT NULL,
                image_url   TEXT,
                available   INTEGER NOT NULL DEFAULT 1,  -- 1=in stock, 0=sold
                created_at  TEXT NOT NULL DEFAULT (datetime('now'))
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS claims (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                item_id      TEXT NOT NULL REFERENCES items(id),
                tg_user_id   INTEGER NOT NULL,
                tg_username  TEXT,
                fulfillment  TEXT NOT NULL DEFAULT 'pickup',  -- 'pickup' | 'delivery'
                contact      TEXT,
                status       TEXT NOT NULL DEFAULT 'pending', -- 'pending'|'paid'|'expired'
                claimed_at   TEXT NOT NULL DEFAULT (datetime('now')),
                expires_at   TEXT NOT NULL DEFAULT (datetime('now', '+30 minutes')),
                completed_at TEXT
            )
        """)
        await db.execute(
            "CREATE INDEX IF NOT EXISTS idx_claims_item ON claims(item_id)"
        )
        await db.execute(
            "CREATE INDEX IF NOT EXISTS idx_claims_expires ON claims(expires_at)"
        )
        await db.commit()


# ── Items ────────────────────────────────────────────────────────────────────

async def seed_items(items: list[dict]) -> None:
    """Insert items that don't exist yet (safe to call on every startup)."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executemany(
            """
            INSERT OR IGNORE INTO items
                (id, brand, title, size, price, badge, badge_class, image_url)
            VALUES
                (:id, :brand, :title, :size, :price, :badge, :badge_class, :image)
            """,
            items,
        )
        await db.commit()


async def get_available_items(size: str | None = None) -> list[dict]:
    """Fetch items that are in-stock (available=1) and not actively claimed."""
    sql = """
        SELECT i.*
        FROM items i
        WHERE i.available = 1
          AND NOT EXISTS (
              SELECT 1 FROM claims c
              WHERE c.item_id = i.id
                AND c.status = 'pending'
                AND c.expires_at > datetime('now')
          )
    """
    params: list = []
    if size and size != "ALL":
        sql += " AND i.size = ?"
        params.append(size)
    sql += " ORDER BY i.created_at DESC"

    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(sql, params) as cur:
            rows = await cur.fetchall()
            return [dict(r) for r in rows]


async def get_item(item_id: str) -> dict | None:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM items WHERE id = ?", (item_id,)
        ) as cur:
            row = await cur.fetchone()
            return dict(row) if row else None


# ── Claims ───────────────────────────────────────────────────────────────────

async def create_claim(
    item_id: str,
    tg_user_id: int,
    tg_username: str | None,
    fulfillment: str,
    contact: str | None,
) -> int | None:
    """
    Attempt to create a 30-minute claim.
    Returns the new claim id, or None if item is already locked/sold.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        # Atomically check + insert
        async with db.execute(
            """
            SELECT 1 FROM items i
            WHERE i.id = ?
              AND i.available = 1
              AND NOT EXISTS (
                  SELECT 1 FROM claims c
                  WHERE c.item_id = i.id
                    AND c.status = 'pending'
                    AND c.expires_at > datetime('now')
              )
            """,
            (item_id,),
        ) as cur:
            if not await cur.fetchone():
                return None  # already locked or sold

        await db.execute(
            """
            INSERT INTO claims (item_id, tg_user_id, tg_username, fulfillment, contact)
            VALUES (?, ?, ?, ?, ?)
            """,
            (item_id, tg_user_id, tg_username, fulfillment, contact),
        )
        await db.commit()

        async with db.execute("SELECT last_insert_rowid()") as cur:
            row = await cur.fetchone()
            return row[0] if row else None


async def get_active_claim(item_id: str) -> dict | None:
    """Return the current pending (non-expired) claim for an item."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            """
            SELECT * FROM claims
            WHERE item_id = ?
              AND status = 'pending'
              AND expires_at > datetime('now')
            ORDER BY claimed_at DESC LIMIT 1
            """,
            (item_id,),
        ) as cur:
            row = await cur.fetchone()
            return dict(row) if row else None


async def mark_claim_paid(claim_id: int) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            UPDATE claims
            SET status = 'paid', completed_at = datetime('now')
            WHERE id = ?
            """,
            (claim_id,),
        )
        # Mark item as sold
        await db.execute(
            """
            UPDATE items SET available = 0
            WHERE id = (SELECT item_id FROM claims WHERE id = ?)
            """,
            (claim_id,),
        )
        await db.commit()


async def expire_stale_claims() -> int:
    """
    Flip all timed-out pending claims to 'expired'.
    Returns the number of rows updated.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            """
            UPDATE claims
            SET status = 'expired', completed_at = datetime('now')
            WHERE status = 'pending'
              AND expires_at <= datetime('now')
            """
        )
        await db.commit()
        return cur.rowcount
