# AI News Digest

> A fully automated, AI-powered news pipeline that collects articles from **35 RSS sources**, deduplicates and summarizes them with LLMs, and delivers clean daily digests through a Telegram bot — with per-user subscriptions, multilingual output (EN / UA), and scheduled delivery every 8 hours.

<p>
  <img alt="Python" src="https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white">
  <img alt="PostgreSQL" src="https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql&logoColor=white">
  <img alt="Docker" src="https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white">
  <img alt="Telegram" src="https://img.shields.io/badge/Telegram-Bot-26A5E4?logo=telegram&logoColor=white">
  <img alt="License" src="https://img.shields.io/badge/License-MIT-3fb950">
</p>

**Try it live:** [@ainewdigestbot](https://t.me/ainewdigestbot)

![AI News Digest](visuals/thumbnail.png)

---

## ✨ Features

- 📡 **35 RSS feeds** across **6 categories** — tech, finance, science, world, crypto, startups
- 🔎 **Smart deduplication** — drops repeat URLs and titles that are ≥ 85% similar (`difflib`)
- 🤖 **LLM summarization** — merges the day's stories into one briefing via Claude or OpenAI
- 🌍 **Multilingual** — every digest generated in **English and Ukrainian**
- 👤 **Per-user subscriptions** — each user picks categories and language; delivery is tracked per user so nobody gets the same digest twice
- ♻️ **Resilient** — automatic retries with exponential backoff on API rate limits
- ⏱️ **Fully automated** — the whole pipeline reruns every 8 hours via APScheduler
- 🐳 **One-command deploy** — PostgreSQL + bot ship together in Docker Compose

---

## Screenshots

| Onboarding & Topics | Daily Digest | Multilingual (EN / UA) |
|---|---|---|
| ![Onboarding](visuals/2.jpg) | ![Digest](visuals/9.jpg) | ![Language](visuals/6.jpg) |

---

## How It Works

![Pipeline architecture](visuals/architecture.png)

1. **Collect** — pulls articles from 35 RSS feeds across 6 categories (`feedparser`)
2. **Clean** — strips HTML tags and normalizes whitespace to plain text (`BeautifulSoup`)
3. **Deduplicate** — drops repeat URLs and titles that are ≥ 85% similar (`SequenceMatcher`)
4. **Store** — persists only new articles in PostgreSQL, tracking what's been sent
5. **Summarize** — an LLM merges everything into one digest — **EN + UA**, with TL;DR and sources
6. **Deliver** — sends to subscribers by category and language, with per-user delivery tracking to avoid duplicates

The full flow is orchestrated by **APScheduler** and reruns **automatically every 8 hours**.

---

## Live Run

A single collect + summarize cycle — 35 feeds in, one clean digest out:

![Terminal run](visuals/terminal.png)

The deduplication step keeps only the first occurrence of each unique story:

![Deduplicator](visuals/code-snippet.png)

---

## Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Register and pick topics |
| `/subscribe [categories]` | Subscribe to one or more categories |
| `/unsubscribe [categories]` | Remove categories or unsubscribe fully |
| `/digest [category]` | Get today's digest (all unsent if no category given) |
| `/language [eng\|ukr]` | Set preferred language |
| `/sources [category]` | See which feeds a category pulls from |
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
├── config.py             # settings + source loading
├── database.py           # PostgreSQL schema & queries
├── models.py             # Article Pydantic model
├── summarizer.py         # LLM summarization (Claude/OpenAI)
├── logger.py             # logging setup
└── scheduler.py          # APScheduler wrapper
main.py                   # CLI entry point
sources.yaml              # 35 RSS feeds grouped by category
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
python main.py collect --category tech   # collect a specific category
python main.py summarize --category tech # summarize collected articles
```

---

## License

Released under the [MIT License](LICENSE).
