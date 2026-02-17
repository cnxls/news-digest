from openai import AsyncOpenAI, OpenAIError, RateLimitError
from anthropic import AsyncAnthropic, APIError, RateLimitError as AnthropicRateLimitError
from pipeline.config import settings

class Summarizer:
    def __init__(self,  provider_name: str = "openai"):
        self.provider, self.client = self.build_client(provider_name)
    
    def build_client(self, provider_name: str = "openai"):
        if provider_name == "openai":
            return "openai", AsyncOpenAI(api_key=settings.openai_api_key)
        elif provider_name == "anthropic":
            return "anthropic", AsyncAnthropic(api_key=settings.anthropic_api_key)