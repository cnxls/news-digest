# AI News Digest Pipeline

Automated pipeline that collects AI/Tech news from multilingual sources and generates concise daily summaries in English using LLMs.

## Status

In active development. Core components built — collectors, processors, and database layer are ready. LLM summarization and delivery are next.

## What's Done

- **Collectors** — three ways to gather articles:
  - RSS feeds (TechCrunch, MIT Tech Review, Wired)
  - NewsAPI integration
  - Web scraper with CSS selectors
- **Processors** — clean and deduplicate articles before summarization:
  - HTML/whitespace cleaner
  - Title-similarity deduplicator (85% threshold)
- **Database** — PostgreSQL storage for articles and digests
- **Config** — centralized settings via `.env` (pydantic-settings)
- **Models** — Article data model with validation (Pydantic)

## What's Next

- [ ] LLM summarization (Claude / OpenAI)
- [ ] Digest generation and formatting
- [ ] Scheduled pipeline runs
- [ ] Delivery (email / Telegram / etc.)

## Project Structure

```
pipeline/
├── collectors/
│   ├── base.py           # abstract collector interface
│   ├── rss_collector.py  # RSS feed parser
│   ├── api_collector.py  # NewsAPI client
│   └── scraper.py        # web scraper (BeautifulSoup)
├── processors/
│   ├── cleaner.py        # HTML & text cleanup
│   └── deduplicator.py   # duplicate detection
├── config.py             # settings from .env
├── database.py           # PostgreSQL connection & schema
├── models.py             # Article model
└── scheduler.py          # (placeholder)
```

## Tech Stack

Python, feedparser, NewsAPI, BeautifulSoup, PostgreSQL, Pydantic, Claude/OpenAI API

## Setup

```bash
git clone https://github.com/your-username/news-digest.git
cd news-digest
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # add your API keys
```

### Required Environment Variables

```
OPENAI_API_KEY=...
ANTHROPIC_API_KEY=...
GOOGLE_API_KEY=...
DATABASE_URL=postgresql://user:pass@localhost:5432/newsdigest
NEWAPI=...
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...
```
