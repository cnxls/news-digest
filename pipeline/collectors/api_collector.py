from pipeline.collectors.base import BaseCollector
import requests
from pipeline.models import Article
import datetime

class ApiCollector(BaseCollector):
    
    BASE_URL = "https://newsapi.org/v2/everything"
    
    def __init__(self, api_key: str, query: str = "artificial intelligence"):
        self.api_key = api_key
        self.query = query

    def collect(self, max_articles: int = 10) -> list[Article]:
        params = {"q": self.query,
                 "pageSize": self.max_articles,
                 "sortBy": "publishedAt",
                 "language": "en",
                 "apiKey": self.api_key}
    
        response = requests.get(self.BASE_URL, params=params)   
        response.raise_for_status()

        data = response.json()
        results = []
        for new in data['articles']:
            article = Article(
                    source='NewsApi',
                    title=new['title'],
                    link=new['url'],
                    collected_at=datetime.datetime.now(),
                    published=new['publishedAt'],
                    content= new['content'],
                    summary=new.get("description", "")) 
            
            results.append(article)
        return results