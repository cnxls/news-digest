from pipeline.collectors.base import BaseCollector


class WebScraper(BaseCollector):

    def __init__(self, url: str, source_name: str, selectors: dict):
        self.url = url
        self.source_name = source_name
        self.selectors = selectors

    def collect():
        ...