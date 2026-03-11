import argparse


def main():
    parser = argparse.ArgumentParser(description="AI News Digest")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("collect", help="Collect News from config sources?")
    subparsers.add_parser("summarize", help="Summarize articles collected?")
    subparsers.add_parser("schedule", help = "Run scheduler")

    args = parser.parse_args()

    if args.command == 'collect':
        from pipeline.collectors import run_collect

        articles = run_collect()
        print(f'Collected and saved into db {len(articles)} articles')
        for article in articles:
            print(article)

    if args.command == 'summarize':
        import asyncio as aio
        from pipeline.summarizer import Summarizer
        from pipeline.database import Database
        from pipeline.config import settings

        summarizer = Summarizer()

        with Database(database_url=settings.database_url) as db:
            db.init_tables()
            articles = db.get_todays_articles()

            summary = aio.run(summarizer.summarize("\n\n".join(f"{a['title']}\n {a['content']}" for a in articles)))
            print(summary)

            db.save_digest(summary['text'])

    if args.command == 'schedule':
        from pipeline.scheduler import scheduled_run
        from pipeline.collectors import run_collect
        
        def pipeline_task():
            run_collect()

            import asyncio as aio
            from pipeline.database import Database
            from pipeline.summarizer import Summarizer
            from pipeline.config import Settings
            settings = Settings()
            db = Database(database_url=settings.database_url)
            scheduled_summarizer = Summarizer()
            db.init_tables()
            articles = db.get_todays_articles()
            scheduled_summary = aio.run(scheduled_summarizer.summarize("\n\n".join(f"{a['title']}\n {a['content']}" for a in articles)))
            db.save_digest(scheduled_summary['text'])

        scheduled_run(pipeline_task)
if __name__ == "__main__":
    main()