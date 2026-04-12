import argparse
from pipeline.logger import get_logger

logger = get_logger()
SUPPORTED_LANGUAGES = ['en', 'uk']


def main():
    parser = argparse.ArgumentParser(description="AI News Digest")
    subparsers = parser.add_subparsers(dest="command")

    collect_parser = subparsers.add_parser("collect", help="Collect news from configured sources")
    collect_parser.add_argument("--category", default=None)

    summarize_parser = subparsers.add_parser("summarize", help="Summarize collected articles")
    summarize_parser.add_argument("--category", default=None)

    args = parser.parse_args()

    if args.command == 'collect':
        from pipeline.collectors import run_collect
        articles = run_collect(category=args.category)
        logger.info(f"Pipeline complete: {len(articles)} articles collected")

    if args.command == 'summarize':
        summarize_all_languages(category=args.category)


def summarize_all_languages(category):
    import asyncio as aio
    from pipeline.summarizer import Summarizer
    from pipeline.database import Database
    from pipeline.config import settings

    summarizer = Summarizer()

    with Database(database_url=settings.database_url) as db:
        db.init_tables()
        articles = db.get_unsent(category=category)
        if not articles:
            logger.info("No new articles collected.")
            return

        article_text = "\n\n".join(f"{a['title']}\n {a['summary']}" for a in articles)
        for lang in SUPPORTED_LANGUAGES:
            summary = aio.run(summarizer.summarize(article_text, language=lang))
            logger.info(f"Summarized {len(articles)} articles ({lang}) — {summary['tokens']['total']} tokens used")
            db.save_digest(summary['text'], category=category, language=lang)
            logger.info(f"Digest saved ({lang})")
        db.mark_as_sent(category=category)
        logger.info("Articles marked as sent")


if __name__ == "__main__":
    main()