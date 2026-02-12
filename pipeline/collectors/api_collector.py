from base import BaseCollector
import requests
import datetime
class ApiCollector(BaseCollector):
    
    BASE_URL = "https://newsapi.org/v2/everything"
    
    def __init__(self, api_key: str, query: str = "artificial intelligence"):
        self.api_key = api_key
        self.query = query

    def collect(self, ):
        collector = ApiCollector()
        params = {"q": self.query,
                 "pageSize": self.max_articles,
                 "sortBy": "publishedAt",
                 "language": "en",
                 "apiKey": self.api_key}
    
        response = requests.get(self.BASE_URL, params=params)   
        response.raise_for_status()


