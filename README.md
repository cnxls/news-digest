# AI News Digest Pipeline

Automated pipeline that collects AI/Tech and Financial news from RSS sources, generates concise daily summaries using LLMs, and delivers digests via Telegram.

## Status

Full pipeline is functional — collect, summarize, deliver, and scheduled runs are working. Category-based separation (tech/finance) is implemented.

## What's Done

- **Collectors** — RSS feed collection with category support:
  - Tech sources (TechCrunch, MIT Tech Review, Hacker News, VentureBeat, The Verge)
  - Finance sources (Bloomberg, Reuters, WSJ)
  - Category-aware collection via `--category` flag
- **Processors** — clean and deduplicate articles before summarization:
  - HTML/whitespace cleaner
  - Title-similarity deduplicator (85% threshold)
- **Database** — PostgreSQL storage for articles and digests, filtered by category
- **Config** — centralized settings via `.env` (pydantic-settings)
- **Models** — Article data model with validation (Pydantic)
- **Summarizer** — LLM summarization via Claude or OpenAI with async retry logic
- **Delivery** — Telegram bot integration for sending digests
- **Scheduler** — automated pipeline runs across all categories

## Usage

```bash
# Collect from all categories
python main.py collect

# Collect only tech or finance
python main.py collect --category tech
python main.py collect --category finance

# Summarize and deliver
python main.py summarize --category tech
python main.py deliver --category tech

# Run full scheduled pipeline
python main.py schedule
```

## Project Structure

```
pipeline/
├── collectors/
│   ├── base.py           # abstract collector interface
│   └── rss_collector.py  # RSS feed parser
├── processors/
│   ├── cleaner.py        # HTML & text cleanup
│   └── deduplicator.py   # duplicate detection
├── delivery/
│   ├── base.py           # abstract delivery interface
│   └── telegram.py       # Telegram bot delivery
├── config.py             # settings from .env
├── database.py           # PostgreSQL connection & schema
├── models.py             # Article model
├── summarizer.py         # LLM summarization (Claude/OpenAI)
├── logger.py             # logging setup
└── scheduler.py          # scheduled pipeline runs
sources.yaml              # RSS feed sources by category
```

## Tech Stack

Python, feedparser, PostgreSQL, Pydantic, Claude/OpenAI API, Telegram Bot API

## Setup

```bash
git clone https://github.com/cnxls/news-digest.git
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
DATABASE_URL=postgresql://user:pass@localhost:5432/newsdigest
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...
```
