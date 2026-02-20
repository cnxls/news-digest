import yaml
import os
from pipeline.collectors.api_collector import ApiCollector
from pipeline.collectors.rss_collector import RssCollector
from pipeline.collectors.scraper import WebScraper

def collect():
    sources_path = os.path.join(os.path.dirname(__file__), '..', '..', 'sources.yaml')

    with open(sources_path, 'r') as f:
        sources = yaml.safe_load(f) or {}

    articles = []

    if 'rss' in sources:
        collector = RssCollector(feeds=sources['rss'])
        articles.extend(collector.collect())

    if 'api' in sources:
        for api_source in sources['api']:
            collector = ApiCollector(
                api_key=api_source['api_key'],
                query=api_source.get('query', 'artificial intelligence')
            )
            articles.extend(collector.collect(max_articles=api_source.get('max_articles', 10)))

    if 'scrape' in sources:
        for scrape_source in sources['scrape']:
            collector = WebScraper(
                url=scrape_source['url'],
                source_name=scrape_source['name'],
                selectors=scrape_source['selectors']
            )
            articles.extend(collector.collect(max_articles=scrape_source.get('max_articles', 10)))

    return articles

if __name__ == '__main__':
    collect()
