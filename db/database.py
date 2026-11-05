"""
Database layer — asyncpg (Supabase / PostgreSQL).
One connection pool, shared across the bot and API server.
"""
import asyncpg
from config import DATABASE_URL

_pool: asyncpg.Pool | None = None


async def get_pool() -> asyncpg.Pool:
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(DATABASE_URL, min_size=2, max_size=10)
    return _pool


async def init_db() -> None:
    """Create tables if they don't exist."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS items (
                id          TEXT PRIMARY KEY,
                brand       TEXT NOT NULL,
                title       TEXT NOT NULL,
                size        TEXT NOT NULL,
                price       TEXT NOT NULL,
                badge       TEXT NOT NULL,
                badge_class TEXT NOT NULL,
                image_url   TEXT,
                available   BOOLEAN NOT NULL DEFAULT TRUE,
                created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
        """)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS claims (
                id           SERIAL PRIMARY KEY,
                item_id      TEXT NOT NULL REFERENCES items(id),
                tg_user_id   BIGINT NOT NULL,
                tg_username  TEXT,
                fulfillment  TEXT NOT NULL DEFAULT 'pickup',
                contact      TEXT,
                status       TEXT NOT NULL DEFAULT 'pending',
                claimed_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                expires_at   TIMESTAMPTZ NOT NULL DEFAULT (NOW() + INTERVAL '30 minutes'),
                completed_at TIMESTAMPTZ
            )
        """)
        await conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_claims_item ON claims(item_id)"
        )
        await conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_claims_expires ON claims(expires_at)"
        )


# ── Items ────────────────────────────────────────────────────────────────────

async def seed_items(items: list[dict]) -> None:
    """Insert items that don't exist yet. Safe to call on every startup."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.executemany(
            """
            INSERT INTO items (id, brand, title, size, price, badge, badge_class, image_url)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            ON CONFLICT (id) DO NOTHING
            """,
            [
                (
                    i["id"], i["brand"], i["title"], i["size"],
                    i["price"], i["badge"], i["badge_class"], i.get("image"),
                )
                for i in items
            ],
        )


async def get_available_items(size: str | None = None) -> list[dict]:
    """
    Return items that are in stock and not currently locked by an active claim.
    """
    pool = await get_pool()
    sql = """
        SELECT i.*
        FROM items i
        WHERE i.available = TRUE
          AND NOT EXISTS (
              SELECT 1 FROM claims c
              WHERE c.item_id = i.id
                AND c.status = 'pending'
                AND c.expires_at > NOW()
          )
    """
    args: list = []
    if size and size != "ALL":
        sql += " AND i.size = $1"
        args.append(size)
    sql += " ORDER BY i.created_at DESC"

    async with pool.acquire() as conn:
        rows = await conn.fetch(sql, *args)
        return [dict(r) for r in rows]


async def get_item(item_id: str) -> dict | None:
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT * FROM items WHERE id = $1", item_id
        )
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
    Atomically lock an item for 30 minutes.
    Returns the claim id or None if already locked / sold.
    """
    pool = await get_pool()
    async with pool.acquire() as conn:
        async with conn.transaction():
            # Lock-check inside transaction
            available = await conn.fetchval(
                """
                SELECT TRUE FROM items i
                WHERE i.id = $1
                  AND i.available = TRUE
                  AND NOT EXISTS (
                      SELECT 1 FROM claims c
                      WHERE c.item_id = i.id
                        AND c.status = 'pending'
                        AND c.expires_at > NOW()
                  )
                FOR UPDATE
                """,
                item_id,
            )
            if not available:
                return None

            claim_id = await conn.fetchval(
                """
                INSERT INTO claims (item_id, tg_user_id, tg_username, fulfillment, contact)
                VALUES ($1, $2, $3, $4, $5)
                RETURNING id
                """,
                item_id, tg_user_id, tg_username, fulfillment, contact,
            )
            return claim_id


async def mark_claim_paid(claim_id: int) -> bool:
    """Mark claim paid and item sold. Returns True on success."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        async with conn.transaction():
            item_id = await conn.fetchval(
                "SELECT item_id FROM claims WHERE id = $1 AND status = 'pending'",
                claim_id,
            )
            if not item_id:
                return False
            await conn.execute(
                "UPDATE claims SET status='paid', completed_at=NOW() WHERE id=$1",
                claim_id,
            )
            await conn.execute(
                "UPDATE items SET available=FALSE WHERE id=$1", item_id
            )
            return True


async def expire_stale_claims() -> int:
    """Expire all timed-out pending claims. Returns count."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        result = await conn.execute(
            """
            UPDATE claims
            SET status = 'expired', completed_at = NOW()
            WHERE status = 'pending' AND expires_at <= NOW()
            """
        )
        return int(result.split()[-1])  # "UPDATE N"
