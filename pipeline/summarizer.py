from openai import AsyncOpenAI, OpenAIError, RateLimitError
from anthropic import AsyncAnthropic, APIError, RateLimitError as AnthropicRateLimitError
from pipeline.config import settings
from pipeline.logger import get_logger
from typing import Dict, Any
import asyncio as aio

logger = get_logger()

SYSTEM_PROMPT = """You are a concise, engaging news analyst. Your job is to summarize news articles into a single Telegram message. Follow these formatting rules strictly:

    FORMAT RULES:
    - Use Telegram MarkdownV2-compatible formatting
    - Use *bold* for key terms, names, and numbers
    - Use _italic_ for context, commentary, or background info
    - Use emojis as section markers (not excessively)
    - Keep the total summary under 300 words
    - End every response with exactly: <<<END>>>

    STRUCTURE (follow this order):
    1. 📰 *Headline* — a single bold sentence capturing the main story
    2. Body — 2-4 short paragraphs summarizing the key points. Bold important facts. Use italic for analyst context or background.
    3. 🔗 *Sources:* — list the source names (not URLs) as a compact citation line

    STYLE:
    - Write in a neutral, informative tone
    - No filler, no greetings, no sign-offs
    - Prefer short punchy sentences over long compound ones
    - If multiple articles cover the same event, merge them into one coherent summary
    - If articles cover different topics, separate them with a --- divider

    OUTPUT MUST end with <<<END>>> on its own line. Do not write anything after it."""

class Summarizer:
    def __init__(self,  provider_name: str = "anthropic"):
        self.provider, self.client = self.build_client(provider_name)
    
    async def call_with_retry(self,
                              func,
                              retries: int = 3,
                              time_interval: int = 2) -> None:
        
            for attempt in range(retries):
                try:
                    return await func()
                
                except (RateLimitError, AnthropicRateLimitError):
                    if attempt < retries-1:
                        logger.warning(f"Rate limited, retrying in {time_interval ** attempt}s (attempt {attempt+1}/{retries})")
                        await aio.sleep(time_interval ** attempt)
                        continue
                    else:
                        raise
                    

    def build_client(self, provider_name: str = "openai"):
        if provider_name == "anthropic":
            return "anthropic", AsyncAnthropic(api_key=settings.anthropic_api_key)
        
        elif provider_name == "openai":
            return "openai", AsyncOpenAI(api_key=settings.openai_api_key)

    async def ask_anthropic(self, client: AsyncAnthropic, question: str, model: str = 'claude-haiku-4-5') -> Dict[str, Any]:
        async def _call():
            message = await client.messages.create(
                model=model,
                max_tokens=1024,
                system= SYSTEM_PROMPT,
                stop_sequences=["<<<END>>>"],
                messages=[{"role": "user", 
                           "content": f"Summarize the following news articles for a Telegram digest:\n\n---\n\n{question}\n\n---"}]
            )

            return message
        try:
            message = await self.call_with_retry(_call)       
            
            result = {
                "text": message.content[0].text.replace("<<<END>>>", "").strip(),
                "model": message.model,
                "tokens": {
                    "input": message.usage.input_tokens,
                    "output": message.usage.output_tokens,
                    "total": message.usage.input_tokens + message.usage.output_tokens
                }
            }
            return result
        
        except AnthropicRateLimitError as e:
            raise
        except APIError as e:
            raise

    async def ask_openai(self, client: AsyncOpenAI, question: str, model: str = 'gpt-4o-mini') -> Dict[str, Any]:
        async def _call():
            message = await client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": question}],
                max_tokens=1024,
                temperature=0.7
            )
            return message
        
        try:
            message = await self.call_with_retry(_call)
            
            result = {
                "text": message.choices[0].message.content,
                "model": message.model,
                "tokens": {
                    "input": message.usage.prompt_tokens,
                    "output": message.usage.completion_tokens,
                    "total": message.usage.completion_tokens + message.usage.prompt_tokens
                }
            }
            return result
        
        except OpenAIError as e:
            raise
        except RateLimitError as e:
            raise

    async def summarize(self, articles):
        logger.info(f"Summarizing with {self.provider}")
        if self.provider == 'anthropic':
            return await self.ask_anthropic(self.client, question=articles)

        elif self.provider == 'openai':
            return await self.ask_openai(self.client, question=articles)