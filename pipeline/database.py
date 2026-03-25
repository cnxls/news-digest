import psycopg2
from psycopg2.extras import RealDictCursor
from pipeline.models import Article

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS articles (
    id           SERIAL PRIMARY KEY,
    title        TEXT NOT NULL,
    link         TEXT UNIQUE NOT NULL,
    source       VARCHAR(50) NOT NULL,
    published    TEXT,
    content      TEXT,
    summary      TEXT,
    collected_at TIMESTAMP DEFAULT NOW(),
    is_sent      BOOLEAN DEFAULT FALSE,
    category     TEXT
);

CREATE INDEX IF NOT EXISTS idx_articles_collected
    ON articles(collected_at DESC);
CREATE INDEX IF NOT EXISTS idx_articles_source
    ON articles(source);
CREATE INDEX IF NOT EXISTS idx_articles_is_sent
    ON articles(is_sent);

CREATE TABLE IF NOT EXISTS digests (
    id            SERIAL PRIMARY KEY,
    content       TEXT NOT NULL,
    created_at    TIMESTAMP DEFAULT NOW(),
    sent_at       TIMESTAMP,
    category      TEXT
);

CREATE TABLE IF NOT EXISTS subscribers (
    id            SERIAL PRIMARY KEY,
    chat_id       BIGINT UNIQUE,
    categories    TEXT[],
    is_active     BOOLEAN DEFAULT TRUE,
    created_at    TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS digest_deliveries (
    id          SERIAL PRIMARY KEY,
    digest_id   INTEGER REFERENCES digests(id),
    chat_id     BIGINT REFERENCES subscribers(chat_id),
    sent_at     TIMESTAMP DEFAULT NOW(),
    UNIQUE(digest_id, chat_id)
);
"""


class Database:

    def __init__(self, database_url: str):
        self.database_url = database_url
        self.conn = None


    def __enter__(self):                                 
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def connect(self):
        self.conn = psycopg2.connect(self.database_url)

    def close(self):
        if self.conn:
            self.conn.close()


    def init_tables(self):
        with self.conn.cursor() as cur:
            cur.execute(SCHEMA_SQL)
            self.conn.commit()
            

    def save_articles(self, articles: list[Article]) -> int:
        sql = """INSERT INTO articles (title, link, source, published, content, summary, category)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT DO NOTHING"""
        saved = 0
        with self.conn.cursor() as cur:
            for article in articles:
                cur.execute(sql, (article.title, article.link, article.source, article.published, article.content, article.summary, article.category))
                saved += cur.rowcount
            self.conn.commit()
        return saved
    
    def get_unsent(self, category: str) -> list[dict]:
        sql = """SELECT * 
        FROM articles
        WHERE is_sent IS FALSE
        AND category = (%s)
        ORDER BY collected_at DESC"""
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, (category,))
            return cur.fetchall()
        
    def mark_as_sent(self, category: str):
        sql = """UPDATE articles
        SET is_sent = TRUE
        WHERE summary IS NOT NULL
        AND category = (%s)"""
        with self.conn.cursor() as cur:
            cur.execute(sql, (category,))
            self.conn.commit()
        
    def save_digest(self, content: str, category: str) -> int:
        sql = """INSERT INTO digests (content, category)
        VALUES (%s, %s)
        RETURNING id"""
        with self.conn.cursor() as cur:
            cur.execute(sql, (content, category,))
            digest_id = cur.fetchone()[0]
            self.conn.commit()
        return digest_id
    
    def get_todays_articles(self):
        sql = """SELECT * 
        FROM articles 
        WHERE collected_at >= CURRENT_DATE
        AND collected_at < CURRENT_DATE + INTERVAL '1 day'"""
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql)
            return cur.fetchall()

    def get_unsent_digest(self, category: str):
        sql="""SELECT id, content, created_at
        FROM digests
        WHERE sent_at IS NULL
        AND category = (%s)
        ORDER BY created_at DESC"""
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, (category,))
            return cur.fetchone()

    def mark_digest_sent(self, digest_id):
        sql = """UPDATE digests
        SET sent_at = NOW()
        WHERE id = %s"""
        with self.conn.cursor() as cur:
            cur.execute(sql, (digest_id,))
            self.conn.commit()

    def add_subscriber(self, chat_id):
        sql = """INSERT INTO subscribers (chat_id)
        VALUES (%s)
        ON CONFLICT(chat_id) DO UPDATE
        SET is_active = TRUE"""
        with self.conn.cursor() as cur:
            cur.execute(sql,(chat_id,))
            self.conn.commit()

    def remove_subscriber(self, chat_id):
        sql = """UPDATE subscribers
        SET is_active = FALSE, categories = '{}'
        WHERE chat_id = (%s)"""
        with self.conn.cursor() as cur:
            cur.execute(sql, (chat_id,))
            self.conn.commit()

    def update_categories(self, categories, chat_id):
        sql = """INSERT INTO subscribers (categories, chat_id, is_active)
        VALUES (%s, %s, TRUE)
        ON CONFLICT (chat_id) DO UPDATE
        SET categories = EXCLUDED.categories,
        is_active = TRUE"""
        with self.conn.cursor() as cur:
            cur.execute(sql, (categories, chat_id,))
            self.conn.commit()

    def get_categories(self, chat_id):
        sql = """SELECT categories
        FROM subscribers
        WHERE chat_id = (%s)
        AND is_active = TRUE"""
        with self.conn.cursor() as cur:
            cur.execute(sql, (chat_id,))
            row = cur.fetchone()
            return row[0] if row else None

    def record_delivery(self, digest_id, chat_id):
        sql = """INSERT INTO digest_deliveries (digest_id, chat_id)
        VALUES (%s, %s)
        ON CONFLICT(digest_id, chat_id) DO NOTHING"""
        with self.conn.cursor() as cur:
            cur.execute(sql, (digest_id, chat_id, ))
            self.conn.commit()

    def get_unsent_digest_for_user(self, categories, chat_id):
        sql = """SELECT DISTINCT ON (d.category) d.id, d.content, d.category
        FROM digests d
        WHERE d.category = ANY(%s)
        AND d.id NOT IN (
            SELECT digest_id FROM digest_deliveries
            WHERE chat_id = %s)
        ORDER BY d.category, d.created_at DESC """
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, (categories, chat_id, ))
            return cur.fetchall()
        
    def get_todays_digest_by_category(self, category):
        sql = """SELECT id, content, category, created_at
        FROM digests
        WHERE category = %s
        AND created_at >= CURRENT_DATE
        AND created_at < CURRENT_DATE + INTERVAL '1 day'
        ORDER BY created_at DESC
        LIMIT 1"""
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, (category,))
            return cur.fetchone()

    def get_active_subscribers(self, category):
        sql = """SELECT chat_id 
        FROM subscribers
        WHERE %s = ANY(categories) 
        AND is_active = TRUE"""
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, (category, ))
            return cur.fetchall()