import argparse

def main():
    parser = argparse.ArgumentParser(description="AI News Digest")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("collect", help="Collect News from config? sources ")

if __name__ == "__main__":
    main()