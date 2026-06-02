import os
import yaml
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    model_config = {"env_file": ".env"}
    openai_api_key: str            # reads OPENAI_API_KEY 
    anthropic_api_key: str         # reads ANTHROPIC_API_KEY 
    database_url: str              # reads DATABASE_URL 
    telegram_bot_token: str        # reads TELEGRAM_BOT_TOKEN
    max_articles_per_source: int = 10

settings = Settings()

def _load_sources():
    sources_path = os.path.join(os.path.dirname(__file__), '..', 'sources.yaml')
    with open(sources_path, 'r') as f:
        return yaml.safe_load(f) or {}

def get_valid_categories():
    return list(_load_sources().get('rss', {}).keys())

def get_sources_by_category():
    rss = _load_sources().get('rss', {})
    return {cat: [s['name'] for s in feeds] for cat, feeds in rss.items()}