from pipeline.processors.cleaner import ArticleCleaner
from pipeline.processors.deduplicator import ArticleDeduplicator

def process(articles):
    
    cleaner = ArticleCleaner()
    articles = cleaner.clean(articles)

    deduplicator = ArticleDeduplicator()
    articles = deduplicator.deduplicate(articles)

    return articles 