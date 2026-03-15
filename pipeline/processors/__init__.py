from pipeline.processors.cleaner import ArticleCleaner
from pipeline.processors.deduplicator import ArticleDeduplicator
from pipeline.logger import get_logger

logger = get_logger()

def process(articles):
    cleaner = ArticleCleaner()
    articles = cleaner.clean(articles)
    logger.info(f"Cleaned {len(articles)} articles")

    deduplicator = ArticleDeduplicator()
    articles = deduplicator.deduplicate(articles)
    logger.info(f"After deduplication: {len(articles)} articles")

    return articles