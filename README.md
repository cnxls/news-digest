# AI News Digest

> A fully automated, AI-powered news pipeline that collects articles from 18+ RSS sources, summarizes them using LLMs, and delivers clean daily digests to users via a Telegram bot — with per-user subscriptions, multilingual output, and scheduled delivery every 8 hours.

---

## Screenshots

| Welcome & Subscribe | Category Selection | Digest Delivery |
|---|---|---|
| ![Start](visuals/2.jpg) | ![Subscribe](visuals/13.jpg) | ![Digest](visuals/9.jpg) |

| Language Toggle | Status | Help |
|---|---|---|
| ![Language](visuals/6.jpg) | ![Status](visuals/11.jpg) | ![Help](visuals/10.jpg) |

---

## What It Does

1. **Collects** — pulls articles from 18+ RSS feeds across 6 categories (tech, finance, science, world, crypto, startups)
2. **Processes** — cleans HTML, deduplicates by URL and title similarity (85% threshold)
3. **Summarizes** — generates Telegram-formatted digests via Claude or OpenAI, in English and Ukrainian
4. **Delivers** — sends digests to subscribed users via Telegram bot, tracking delivery per user to avoid duplicates
5. **Schedules** — runs the full pipeline every 8 hours automatically

---

## Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Register and pick topics |
| `/subscribe [categories]` | Subscribe to one or more categories |
| `/unsubscribe [categories]` | Remove categories or unsubscribe fully |
| `/digest [category]` | Get today's digest (all unsent if no category given) |
| `/language [eng\|ukr]` | Set preferred language |
| `/status` | View subscriptions, language, and pending digests |
| `/help` | Show all commands |

**Categories:** tech, finance, science, world, crypto, startups

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.13 |
| RSS Collection | feedparser |
| Text Processing | BeautifulSoup, difflib |
| Summarization | Anthropic Claude / OpenAI |
| Database | PostgreSQL 16 |
| Telegram Bot | python-telegram-bot |
| Scheduling | APScheduler |
| Config | Pydantic Settings |
| Deployment | Docker, docker-compose |

---

## Project Structure

```
pipeline/
├── collectors/
│   ├── base.py           # abstract collector interface
│   └── rss_collector.py  # RSS feed parser (feedparser)
├── processors/
│   ├── cleaner.py        # HTML & whitespace cleanup
│   └── deduplicator.py   # URL + title similarity dedup
├── delivery/
│   └── __init__.py
├── bot.py                # Telegram bot handlers + scheduler
├── config.py             # settings from .env
├── database.py           # PostgreSQL schema & queries
├── models.py             # Article Pydantic model
├── summarizer.py         # LLM summarization (Claude/OpenAI)
├── logger.py             # logging setup
└── scheduler.py          # APScheduler wrapper
main.py                   # CLI entry point
sources.yaml              # RSS feed sources by category
docker-compose.yml        # PostgreSQL + bot services
```

---

## Setup

```bash
git clone https://github.com/cnxls/news-digest.git
cd news-digest
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # fill in your API keys
```

### Environment Variables

```
ANTHROPIC_API_KEY=...
OPENAI_API_KEY=...
DATABASE_URL=postgresql://user:pass@localhost:5432/newsdigest
TELEGRAM_BOT_TOKEN=...
```

When deploying with Docker, also set `DB_PASSWORD` in your `.env` — used by `docker-compose.yml` to configure the PostgreSQL container.

---

## Run with Docker

```bash
docker compose up -d
```

Starts PostgreSQL and the bot. The pipeline runs automatically every 8 hours.

---

## CLI Usage

```bash
python main.py collect                   # collect from all categories
python main.py collect --category tech   # collect specific category
python main.py summarize --category tech # summarize collected articles
```
