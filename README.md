# AI News Digest Pipeline

Automated pipeline that collects AI/Tech news from multilingual sources and generates concise daily summaries in English using LLMs.

## Status

Early development. Currently implementing core news collectors.

## Tech Stack

Python, feedparser, NewsAPI, PostgreSQL, Claude/OpenAI API

## Setup

```bash
git clone https://github.com/your-username/news-digest.git
cd news-digest
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # add your API keys
```