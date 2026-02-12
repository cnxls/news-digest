from pipeline.collectors.base import BaseCollector
import requests
from bs4 import BeautifulSoup
import datetime
from pipeline.models import Article

class WebScraper(BaseCollector):

    def __init__(self, url: str, source_name: str, selectors: dict):
        self.url = url
        self.source_name = source_name
        self.selectors = selectors

    def collect(self, max_articles: int = 10) -> list[Article]:

        response = requests.get(self.url, headers={
            "User-Agent": "Mozilla/5.0"  
        })
        response.raise_for_status()

        soup = BeautifulSoup(response.text,"html.parser")
        cards = soup.select(self.selectors['article'])
        results = []

        for card in cards[:max_articles]:
            title = card.select_one(self.selectors['title'])
            link = card.select_one(self.selectors.get('link', 'a'))
            
            if not title:
                continue

            title = title.text.strip()
            link = link['href'] if link else ""
            
            if link and link.startswith("/"):
                from urllib.parse import urljoin
                link = urljoin(self.url,link)

            summary_sel = self.selectors.get('summary')
            summary = card.select_one(summary_sel) if summary_sel else None
            date_sel = self.selectors.get('date')
            date = card.select_one(date_sel) if date_sel else None

            article = Article(
                source=self.source_name,
                title=title,
                link=link,
                published=date.text.strip() if date else "",
                summary=summary.text.strip() if summary else "",
                collected_at=datetime.datetime.now(),
            )
            results.append(article)
        return results