from abc import ABC,abstractmethod
from pipeline.models import Article
class BaseCollector(ABC):

    @abstractmethod
    def collect(self, max_articles: int = 10) -> list[Article]:
        ...