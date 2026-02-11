import feedparser
import json
from pipeline.models import Article

class RssCollector:
    def __init__(self, feeds):
        self.feeds = feeds 

    def collect(self, max_articles : int = 10) -> list[Article]:
        for feed in self.feeds:
            feedparser.parse(feed['url'])

sources = [
       ('https://techcrunch.com/category/artificial-intelligence/feed/', 'TCRssNews.json'),
       ('https://www.technologyreview.com/feed/', 'MitRssNews.json'),
       ('https://www.wired.com/feed/tag/ai/latest/rss', 'WiredRssNews.json')
        ]

def rss_feed_parse(url : str, number_of_news : int):
        feed = feedparser.parse(url)
        news_items = []
        
        for entry in feed.entries[:number_of_news]:  
            item = RssCollector(entry.title, entry.link, entry.published, entry.summary)
            news_items.append(item)
        return news_items


def parse_sources(sources : list):
    for source in sources:
        items = rss_feed_parse(source[0])
        items_list = [item.to_dict() for item in items]
        filename = source[1]
        Article.to_dict(items_list, filename)    
