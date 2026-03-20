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

    def add_subscriber(self, chat_id = None):
        sql = """INSERT INTO subscribers (chat_id)
        VALUES (%s)
        ON CONFLICT(chat_id) DO UPDATE
        SET is_active = TRUE"""
        with self.conn.cursor() as cur:
            cur.execute(sql,)
            self.conn.commit()

    def remove_subscriber(self, chat_id):
        sql = """UPDATE subscribers
        SET is_active = FALSE
        WHERE chat_id = (%s)"""
        with self.conn.cursor() as cur:
            cur.execute(sql, (chat_id,))
            self.conn.commit()

    def update_categories(self, categories, chat_id):
        sql = """UPDATE subscribers
         SET categories = %s
         WHERE chat_id = %s
         AND is_active = TRUE"""