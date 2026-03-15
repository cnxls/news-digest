import yaml
import os
from pipeline.collectors.rss_collector import RssCollector
from pipeline.processors import process
from pipeline.database import Database
from pipeline.config import settings
from pipeline.logger import get_logger

logger = get_logger()

def run_collect():
    sources_path = os.path.join(os.path.dirname(__file__), '..', '..', 'sources.yaml')

    with open(sources_path, 'r') as f:
        sources = yaml.safe_load(f) or {}

    articles = []

    if 'rss' in sources:
        logger.info("Collecting from RSS feeds")
        collector = RssCollector(feeds=sources['rss'])
        articles.extend(collector.collect())

    if 'scrape' in sources:
        for scrape_source in sources['scrape']:
            logger.info(f"Scraping {scrape_source['name']}")
            collector = WebScraper(
                url=scrape_source['url'],
                source_name=scrape_source['name'],
                selectors=scrape_source['selectors']
            )
            articles.extend(collector.collect(max_articles=scrape_source.get('max_articles', 10)))

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
