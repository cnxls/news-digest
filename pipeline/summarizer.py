from openai import AsyncOpenAI, OpenAIError, RateLimitError
from anthropic import AsyncAnthropic, APIError, RateLimitError as AnthropicRateLimitError
from pipeline.config import settings
from typing import Dict, Any

class Summarizer:
    def __init__(self,  provider_name: str = "openai"):
        self.provider, self.client = self.build_client(provider_name)
    
    def build_client(self, provider_name: str = "openai"):
        if provider_name == "openai":
            return "openai", AsyncOpenAI(api_key=settings.openai_api_key)
        elif provider_name == "anthropic":
            return "anthropic", AsyncAnthropic(api_key=settings.anthropic_api_key)

        
    async def ask_openai(self, client: AsyncOpenAI, question: str, model: str) -> Dict[str, Any]:
        async def _call():
            response = await client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are an expert AI news curator. Your job is to produce a concise, informative summary of a news article about artificial intelligence or technology. Write 2-3 sentences that capture the key facts, why it matters, and any notable implications. Be factual, neutral in tone, and avoid marketing language. Output only the summary text with no preamble."},
                    {"role": "user", "content": question}
                ],
                max_tokens=512,
                temperature=0.7
            )
            return response
        
        try:
            response = await _call()       # call_with_retry(_call)
            
            result = {
                "text": response.choices[0].message.content,
                "model": response.model,
                "tokens": {
                    "input": response.usage.prompt_tokens,
                    "output": response.usage.completion_tokens,
                    "total": response.usage.total_tokens
                }
            }
            return result
        
        except OpenAIError as e:
            raise
        except Exception as e:
            raise