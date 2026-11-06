"""
Database layer — asyncpg (Supabase / PostgreSQL) with in-memory fallback.
One connection pool, shared across the bot and API server.
"""
import logging
import asyncpg
from config import DATABASE_URL
from db.seed_data import INVENTORY

log = logging.getLogger(__name__)

_pool: asyncpg.Pool | None = None
_in_memory_items: list[dict] = []
_in_memory_claims: dict[int, dict] = {}
_claim_counter = 1


async def get_pool() -> asyncpg.Pool | None:
    global _pool
    if not DATABASE_URL:
        return None
    if _pool is None:
        try:
            _pool = await asyncpg.create_pool(DATABASE_URL, min_size=2, max_size=10)
        except Exception as e:
            log.warning("Could not connect to PostgreSQL (%s). Running with in-memory data.", e)
            return None
    return _pool


async def init_db() -> None:
    """Create tables if they don't exist."""
    pool = await get_pool()
    if not pool:
        log.info("DATABASE_URL not set or unreachable. Initialized in-memory inventory (%d items).", len(INVENTORY))
        global _in_memory_items
        _in_memory_items = [dict(i, available=True) for i in INVENTORY]
        return

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
    pool = await get_pool()
    if not pool:
        global _in_memory_items
        if not _in_memory_items:
            _in_memory_items = [dict(i, available=True) for i in items]
        return

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
    pool = await get_pool()
    if not pool:
        res = [i for i in _in_memory_items if i.get("available", True)]
        if size and size != "ALL":
            res = [i for i in res if i.get("size") == size]
        return res

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
    if not pool:
        for i in _in_memory_items:
            if i["id"] == item_id:
                return i
        return None

    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT * FROM items WHERE id = $1", item_id
        )
        return dict(row) if row else None


async def get_all_items_stock() -> list[dict]:
    """Return all items with live status for admin /stock view."""
    pool = await get_pool()
    if not pool:
        return [
            dict(
                i,
                claim_id=None,
                tg_username=None,
                fulfillment=None,
                claim_status=None,
                expires_at=None,
            )
            for i in _in_memory_items
        ]

    async with pool.acquire() as conn:
        rows = await conn.fetch("""
            SELECT
                i.id, i.brand, i.title, i.size, i.price, i.available,
                c.id        AS claim_id,
                c.tg_username,
                c.fulfillment,
                c.status    AS claim_status,
                c.expires_at
            FROM items i
            LEFT JOIN LATERAL (
                SELECT * FROM claims
                WHERE item_id = i.id
                  AND status = 'pending'
                  AND expires_at > NOW()
                ORDER BY claimed_at DESC LIMIT 1
            ) c ON TRUE
            ORDER BY i.created_at DESC
        """)
        return [dict(r) for r in rows]


async def add_item(item: dict) -> None:
    """Insert a new item (admin /add_item)."""
    pool = await get_pool()
    if not pool:
        _in_memory_items.insert(0, dict(item, available=True))
        return

    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO items (id, brand, title, size, price, badge, badge_class, image_url)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            ON CONFLICT (id) DO NOTHING
            """,
            item["id"], item["brand"], item["title"], item["size"],
            item["price"], item["badge"], item.get("badge_class", "one-of-one"),
            item.get("image_url"),
        )


# ── Claims ────────────────────────────────────────────────────────────────────

async def create_claim(
    item_id: str,
    tg_user_id: int,
    tg_username: str | None,
    fulfillment: str,
    contact: str | None,
) -> int | None:
    pool = await get_pool()
    if not pool:
        global _claim_counter
        cid = _claim_counter
        _claim_counter += 1
        _in_memory_claims[cid] = {
            "id": cid,
            "item_id": item_id,
            "tg_user_id": tg_user_id,
            "tg_username": tg_username,
            "fulfillment": fulfillment,
            "contact": contact,
            "status": "pending",
        }
        return cid

    async with pool.acquire() as conn:
        async with conn.transaction():
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


async def get_claim(claim_id: int) -> dict | None:
    pool = await get_pool()
    if not pool:
        return _in_memory_claims.get(claim_id)

    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT * FROM claims WHERE id = $1", claim_id
        )
        return dict(row) if row else None


async def mark_claim_paid(claim_id: int) -> bool:
    pool = await get_pool()
    if not pool:
        c = _in_memory_claims.get(claim_id)
        if c and c["status"] == "pending":
            c["status"] = "paid"
            for i in _in_memory_items:
                if i["id"] == c["item_id"]:
                    i["available"] = False
            return True
        return False

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
    pool = await get_pool()
    if not pool:
        return 0

    async with pool.acquire() as conn:
        result = await conn.execute(
            """
            UPDATE claims
            SET status = 'expired', completed_at = NOW()
            WHERE status = 'pending' AND expires_at <= NOW()
            """
        )
        return int(result.split()[-1])

