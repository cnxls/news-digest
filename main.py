import argparse

def main():
    parser = argparse.ArgumentParser(description="AI News Digest")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("collect", help="Collect News from config sources?")

    args = parser.parse_args()

    if args.command == 'collect':
        from pipeline.collectors import run_collect

        articles = run_collect()
        print(f'Collected and saved into db {len(articles)} articles')
        for article in articles:
            print(article)


if __name__ == "__main__":
    main()