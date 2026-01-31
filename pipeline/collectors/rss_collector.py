import feedparser
import json


class NewsRssParser:
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

number_of_news = int(input('how many recent news do you want to get?'))

for source in sources:

    
    def rss_feed_parse(url):
        feed = feedparser.parse(url)
        news_items = []
        
        for entry in feed.entries[:number_of_news]:  
            item = NewsRssParser(entry.title, entry.link, entry.published, entry.summary)
            news_items.append(item)
        return news_items


    items = rss_feed_parse(source[0])
    items_list = [item.to_dict() for item in items]
    filename = source[1]
    
    def to_json(items_list, filename):

        with open(filename, 'w') as file:
                json.dump(items_list, file, indent = 2)


    to_json(items_list, filename)