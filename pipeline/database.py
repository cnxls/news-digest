import psycopg2
from psycopg2.extras import RealDictCursor
from models import Article

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
    is_sent      BOOLEAN DEFAULT FALSE
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
    article_count INTEGER,
    created_at    TIMESTAMP DEFAULT NOW(),
    sent_at       TIMESTAMP
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
        sql = """INSERT INTO articles (title, link, source, published, summary)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT DO NOTHING"""
        saved = 0
        with self.conn.cursor() as cur:
            for article in articles:
                cur.execute(sql, (article.title, article.link, article.source, article.published, article.summary))
                saved += cur.rowcount
            self.conn.commit()
        return saved
    
    def get_unsent(self) -> list[dict]:
        sql = """SELECT * 
        FROM articles
        WHERE is_sent IS FALSE
        ORDER BY collected_at DESC"""
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql)
            return cur.fetchall()
        
    def mark_as_sent(self):
        sql = """UPDATE articles 
        SET is_sent = TRUE 
        WHERE id IN
        (SELECT id 
        FROM articles
        WHERE summary IS NOT NULL """
        with self.conn.cursor() as cur:
            cur.execute(sql)
        
    def save_digest(self, content: str, article_count: int) -> int:
        sql = """INSERT INTO digests (content, article_count)
        VALUES (%s, %s)
        RETURNING id"""
        with self.conn.cursor() as cur:
            cur.execute(sql, (content, article_count))
            digest_id = cur.fetchone()[0]
        self.conn.commit()
        return digest_id