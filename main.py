import argparse
from pipeline.logger import get_logger

logger = get_logger()


def main():
    parser = argparse.ArgumentParser(description="AI News Digest")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("collect", help="Collect News from config sources?")
    subparsers.add_parser("summarize", help="Summarize articles collected?")
    subparsers.add_parser("deliver", help="Send digest to Telegram")
    subparsers.add_parser("schedule", help = "Run scheduler")

    args = parser.parse_args()

    if args.command == 'collect':
        from pipeline.collectors import run_collect

        articles = run_collect()
        logger.info(f"Pipeline complete: {len(articles)} articles collected")

    def summarize():
        import asyncio as aio
        from pipeline.summarizer import Summarizer
        from pipeline.database import Database
        from pipeline.config import settings

        summarizer = Summarizer()

        with Database(database_url=settings.database_url) as db:
            db.init_tables()
            articles = db.get_unsent()

            summary = aio.run(summarizer.summarize("\n\n".join(f"{a['title']}\n {a['summary']}" for a in articles)))
            logger.info(f"Summarized {len(articles)} articles — {summary['tokens']['total']} tokens used")

            db.save_digest(summary['text'])
            db.mark_as_sent()
            logger.info("Digest saved and articles marked as sent")


    if args.command == 'summarize':
        summarize()
                

    if args.command == 'deliver':
        from pipeline.delivery.telegram import TelegramDelivery
        from pipeline.database import Database
        from pipeline.config import settings

        delivery = TelegramDelivery()
        with Database(database_url=settings.database_url) as db:
            db.init_tables()
            digest = db.get_unsent_digest()
            if not digest:
                logger.info("No unsent digest found")
                return
            if delivery.deliver(digest['content']):
                db.mark_digest_sent(digest['id'])

    if args.command == 'schedule':
        from pipeline.scheduler import scheduled_run
        from pipeline.collectors import run_collect
        
        def pipeline_task():
            run_collect()
            summarize()
            
        scheduled_run(pipeline_task)


if __name__ == "__main__":
    main()