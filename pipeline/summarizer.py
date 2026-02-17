from openai import AsyncOpenAI, OpenAIError, RateLimitError
from anthropic import AsyncAnthropic, APIError, RateLimitError as AnthropicRateLimitError
from pipeline.config import settings

def build_client(provider_name: str = "openai"):
    if provider_name == "openai":
        return "openai", AsyncOpenAI(api_key=settings.openai_api_key)
    elif provider_name == "anthropic":
        return "anthropic", AsyncAnthropic(api_key=settings.anthropic_api_key)