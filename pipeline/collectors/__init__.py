import yaml
import os
from pipeline.collectors.rss_collector import RssCollector
from pipeline.processors import process
from pipeline.database import Database
from pipeline.config import settings
from pipeline.logger import get_logger

logger = get_logger()

def run_collect(category = None):
    sources_path = os.path.join(os.path.dirname(__file__), '..', '..', 'sources.yaml')

    with open(sources_path, 'r') as f:
        sources = yaml.safe_load(f) or {}

    articles = []

    if 'rss' in sources:
        logger.info("Collecting from RSS feeds")
        for cat, feeds in sources['rss'].items():
            if category and category != cat:
                continue
            logger.info(f"Collecting from RSS feeds: {cat}")
            collector = RssCollector(category=cat, feeds=feeds)
            articles.extend(collector.collect())

    logger.info(f"Collected {len(articles)} articles before processing")
    articles = process(articles)
    logger.info(f"After processing: {len(articles)} articles")

    with Database(settings.database_url) as db:
        db.init_tables()
        saved = db.save_articles(articles)
        logger.info(f"Saved {saved} new articles to database")

    return articles

if __name__ == '__main__':
    run_collect()
