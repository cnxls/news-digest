from openai import AsyncOpenAI, OpenAIError, RateLimitError
from anthropic import AsyncAnthropic, APIError, RateLimitError as AnthropicRateLimitError
from ... import load_api_key

def build_client(self, provider_name:str = 'openai'):

    provider_name = self.provider_name
    try:
        if provider_name == "openai":
            api_key = load_api_key("openai")
            return "openai", AsyncOpenAI(api_key=api_key)
        
        elif provider_name == "anthropic":
            api_key = load_api_key("anthropic")
            return "anthropic", AsyncAnthropic(api_key=api_key)
    except:
        ...   