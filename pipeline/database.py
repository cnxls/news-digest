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
