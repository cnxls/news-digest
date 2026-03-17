from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    model_config = {"env_file": ".env"}

    openai_api_key: str            # reads OPENAI_API_KEY 
    anthropic_api_key: str         # reads ANTHROPIC_API_KEY 
    database_url: str              # reads DATABASE_URL 
    telegram_bot_token: str        # reads TELEGRAM_BOT_TOKEN
    telegram_chat_id: str          # reads TELEGRAM_CHAT_ID

    rss_feeds: list[dict] = [
    {"name": "techcrunch", "url": "https://techcrunch.com/category/artificial-intelligence/feed/"},
    {"name": "mit", "url": "https://www.technologyreview.com/feed/"},
    {"name": "wired", "url": "https://www.wired.com/feed/tag/ai/latest/rss"},
    ]

    max_articles_per_source: int = 10

settings = Settings()   