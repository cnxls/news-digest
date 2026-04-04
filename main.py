import argparse
from pipeline.logger import get_logger

logger = get_logger()


def main():
    parser = argparse.ArgumentParser(description="AI News Digest")
    subparsers = parser.add_subparsers(dest="command")

    collect_parser = subparsers.add_parser("collect", help="Collect News from config sources?")
    collect_parser.add_argument("--category", default=None)

    summarize_parser = subparsers.add_parser("summarize", help="Summarize articles collected?")
    summarize_parser.add_argument("--category", default=None)
    
    deliver_parser = subparsers.add_parser("deliver", help="Send digest to Telegram")
    deliver_parser.add_argument("--category", default=None)
    
    subparsers.add_parser("schedule", help = "Run scheduler")

    args = parser.parse_args()

    if args.command == 'collect':
        from pipeline.collectors import run_collect

        articles = run_collect(category=args.category)
        logger.info(f"Pipeline complete: {len(articles)} articles collected")

    SUPPORTED_LANGUAGES = ['en', 'uk']

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

    if args.command == 'summarize':
        summarize_all_languages(category=args.category)

    def deliver(categories):
        from pipeline.delivery.telegram import TelegramDelivery
        from pipeline.database import Database
        from pipeline.config import settings

        db = Database(settings.database_url)
        db.connect()

        for category in categories:
            for language in SUPPORTED_LANGUAGES:
                digest = db.get_unsent_digest(category=category, language=language)
                if not digest:
                    continue
                chats = db.get_active_subscribers(category=category, language=language)
                delivery = TelegramDelivery()
                for chat in chats:
                    delivery.chat_id = chat["chat_id"]
                    delivery.deliver(digest["content"])
                    db.record_delivery(digest_id=digest["id"], chat_id=chat["chat_id"])

                
                

    if args.command == 'deliver':
        deliver(categories=[args.category])

    if args.command == 'schedule':
        from pipeline.scheduler import scheduled_run
        from pipeline.collectors import run_collect
        import yaml
        
        def pipeline_task():
            with open("sources.yaml") as f:
                sources = yaml.safe_load(f)
                categories = list(sources["rss"].keys())
            run_collect()
            for cat in categories:
                summarize_all_languages(category=cat)
        scheduled_run(pipeline_task)


if __name__ == "__main__":
    main()