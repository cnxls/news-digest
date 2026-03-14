import yaml
import os
from pipeline.collectors.rss_collector import RssCollector
from pipeline.processors import process
from pipeline.database import Database
from pipeline.config import settings
from pipeline.collectors.scraper import WebScraper 

def run_collect():
    sources_path = os.path.join(os.path.dirname(__file__), '..', '..', 'sources.yaml')

    with open(sources_path, 'r') as f:
        sources = yaml.safe_load(f) or {}

    articles = []

    if 'rss' in sources:
        collector = RssCollector(feeds=sources['rss'])
        articles.extend(collector.collect())

    if 'scrape' in sources:
        for scrape_source in sources['scrape']:
            collector = WebScraper(
                url=scrape_source['url'],
                source_name=scrape_source['name'],
                selectors=scrape_source['selectors']
            )
            articles.extend(collector.collect(max_articles=scrape_source.get('max_articles', 10)))

    articles = process(articles)
    
    with Database(settings.database_url) as db:
        db.init_tables()
        saved = db.save_articles(articles)
        print(f"Saved {saved} new articles")
    
    return articles

if __name__ == '__main__':
    run_collect()
