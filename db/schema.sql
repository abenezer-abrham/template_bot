-- ============================================================
-- BOTZ – Streetwear & Thrift Boutique — Supabase Schema
-- Run once against your Supabase project (SQL Editor tab)
-- ============================================================

CREATE TABLE IF NOT EXISTS items (
    id          TEXT PRIMARY KEY,
    brand       TEXT NOT NULL,
    title       TEXT NOT NULL,
    size        TEXT NOT NULL,
    price       TEXT NOT NULL,
    badge       TEXT NOT NULL,
    badge_class TEXT NOT NULL,          -- 'one-of-one' | 'archive' | 'grail'
    image_url   TEXT,
    available   BOOLEAN NOT NULL DEFAULT TRUE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS claims (
    id           SERIAL PRIMARY KEY,
    item_id      TEXT NOT NULL REFERENCES items(id),
    tg_user_id   BIGINT NOT NULL,
    tg_username  TEXT,
    fulfillment  TEXT NOT NULL DEFAULT 'pickup',  -- 'pickup' | 'delivery'
    contact      TEXT,
    status       TEXT NOT NULL DEFAULT 'pending', -- 'pending' | 'paid' | 'expired'
    claimed_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at   TIMESTAMPTZ NOT NULL DEFAULT (NOW() + INTERVAL '30 minutes'),
    completed_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_claims_item    ON claims(item_id);
CREATE INDEX IF NOT EXISTS idx_claims_expires ON claims(expires_at);
CREATE INDEX IF NOT EXISTS idx_claims_status  ON claims(status);

-- ── Seed Inventory ──────────────────────────────────────────
INSERT INTO items (id, brand, title, size, price, badge, badge_class, image_url) VALUES
  ('botz-001', 'Nike',         'Dunk Low Retro ''Panda''',               'US 10', '$115', 'DEADSTOCK',       'one-of-one', 'https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?w=600&q=85'),
  ('botz-002', 'Vintage 1994', 'Pink Floyd ''Division Bell'' Tour Tee',  'L',     '$140', '1-OF-1 VINTAGE',  'one-of-one', 'https://images.unsplash.com/photo-1521572267360-ee0c2909d518?w=600&q=85'),
  ('botz-003', 'Arc''teryx',   'Beta LT Gore-Tex Shell Jacket',          'M',     '$320', 'GRAIL',           'grail',      'https://images.unsplash.com/photo-1548883354-7622d03aca27?w=600&q=85'),
  ('botz-004', 'Stüssy',       '8-Ball Mohair Knit Sweater',             'L',     '$185', 'ARCHIVE',         'archive',    'https://images.unsplash.com/photo-1620799140408-edc6dcb6d633?w=600&q=85'),
  ('botz-005', 'Carhartt WIP', 'Detroit Jacket Blanket Lined',           'XL',    '$160', '1-OF-1',          'one-of-one', 'https://images.unsplash.com/photo-1551028719-00167b16eac5?w=600&q=85'),
  ('botz-006', 'Air Jordan',   'Jordan 4 Retro ''Military Black''',      'US 11', '$290', 'VERIFIED GRAIL',  'grail',      'https://images.unsplash.com/photo-1584735935682-2f2b69dff9d2?w=600&q=85'),
  ('botz-007', 'Supreme',      'Box Logo Crewneck (FW22)',                'S',     '$210', '1-OF-1',          'archive',    'https://images.unsplash.com/photo-1556905055-8f358a7a47b2?w=600&q=85'),
  ('botz-008', 'New Balance',  '990v3 MiUSA Grey Classic',               'US 9',  '$135', 'CLEAN PAIR',      'one-of-one', 'https://images.unsplash.com/photo-1539185441755-769473a23570?w=600&q=85')
ON CONFLICT (id) DO NOTHING;
