import argparse


def main():
    parser = argparse.ArgumentParser(description="AI News Digest")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("collect", help="Collect News from config sources?")
    subparsers.add_parser("summarize", help="Summarize articles collected?")

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
            db.connect()
            db.init_tables()
            articles = db.get_todays_articles()
            
            prompt = "\n\n".join(articles)
            summary = aio.run(summarizer.summarize(f"{a['title']}\n {a['content']}" for a in articles))
            print(summary)

            db.save_digest(summary['text'])


if __name__ == "__main__":
    main()