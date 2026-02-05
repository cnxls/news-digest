import json
import requests
import datetime



class news_api_parser:
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
    

