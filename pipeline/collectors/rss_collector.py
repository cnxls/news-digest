import feedparser
from pipeline.models import Article
from pipeline.config import settings
class RssCollector:
    def __init__(self, feeds: list[dict]):
        self.feeds = feeds 

    def collect(self, max_articles : int = 10) -> list[Article]:
        articles = []
        for feed in self.feeds:
            art = RssCollector.rss_feed_parse(feed['url'], max_articles)
            articles.extend(art)
        return articles 

    @staticmethod
    def rss_feed_parse(url : str, number_of_news : int = 50):
        feed = feedparser.parse(url)
        news_items = []
        
        for entry in feed.entries[:number_of_news]:  
            item = Article(title=entry.title, link=entry.link, source=url, published=getattr(entry, 'published', ''), summary=getattr(entry, 'summary', ''))
            news_items.append(item)
        return news_items

if __name__ == "__main__":
    collector = RssCollector(feeds=settings.rss_feeds)
    articles = collector.collect()
    for article in articles:
        print(article.model_dump())