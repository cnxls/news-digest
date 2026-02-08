import feedparser
import json

class RssCollector:
    def __init__(self, title, link, published, summary):
        self.title = title
        self.link = link
        self.published = published
        self.summary = summary

    def to_dict(self):
        return {
            'title': self.title,
            'link': self.link,
            'published': self.published,
            'summary': self.summary
        }


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
        to_json(items_list, filename)    

def to_json(items_list, filename):
    with open(filename, 'w') as file:
        json.dump(items_list, file, indent = 2)
