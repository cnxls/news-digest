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

    def summarize(category):
        import asyncio as aio
        from pipeline.summarizer import Summarizer
        from pipeline.database import Database
        from pipeline.config import settings

        summarizer = Summarizer()

        with Database(database_url=settings.database_url) as db:
            db.init_tables()
            articles = db.get_unsent(category=category)

            summary = aio.run(summarizer.summarize("\n\n".join(f"{a['title']}\n {a['summary']}" for a in articles)))
            logger.info(f"Summarized {len(articles)} articles — {summary['tokens']['total']} tokens used")

            db.save_digest(summary['text'], category=category)
            db.mark_as_sent(category=category)
            logger.info("Digest saved and articles marked as sent")


    if args.command == 'summarize':
        summarize(category=args.category)

    def deliver(category):
        from pipeline.delivery.telegram import TelegramDelivery
        from pipeline.database import Database
        from pipeline.config import settings

        delivery = TelegramDelivery()
        with Database(database_url=settings.database_url) as db:
            db.init_tables()
            digest = db.get_unsent_digest(category=category)
            if not digest:
                logger.info("No unsent digest found")
                return
            if delivery.deliver(digest['content']):
                db.mark_digest_sent(digest['id'])

    if args.command == 'deliver':
        deliver(category=args.category )

    if args.command == 'schedule':
        from pipeline.scheduler import scheduled_run
        from pipeline.collectors import run_collect

        def pipeline_task():
            run_collect()
            for cat in ['tech', 'finance']:
                summarize(category=cat)
                deliver(category=cat)

        scheduled_run(pipeline_task)


if __name__ == "__main__":
    main()