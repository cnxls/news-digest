from openai import AsyncOpenAI, OpenAIError, RateLimitError
from anthropic import AsyncAnthropic, APIError, RateLimitError as AnthropicRateLimitError
from pipeline.config import settings
from pipeline.logger import get_logger
from typing import Dict, Any
import asyncio as aio

logger = get_logger()

LANGUAGE_INSTRUCTIONS = {
    'en': '',
    'uk': '\n    IMPORTANT: Write the ENTIRE digest in Ukrainian (Українська). All headlines, body text, TL;DR, and labels must be in Ukrainian.',
}

def build_system_prompt(language='en'):
    lang_instruction = LANGUAGE_INSTRUCTIONS.get(language, '')
    return f"""You are a concise, engaging news analyst. Your job is to summarize ALL provided news articles into ONE cohesive Telegram message. Follow these formatting rules strictly:

    FORMAT RULES:
    - Use Telegram HTML formatting: <b>bold</b>, <i>italic</i>, <blockquote>blockquote</blockquote>
    - Use emojis naturally in the text to make it visually engaging
    - Keep the total summary under 200 words
    - End every response with exactly: <<<END>>>{lang_instruction}

    STRUCTURE (follow this exact order):

    1. HEADLINE — Start with a relevant emoji + <b>bold headline</b> that captures the overall theme of today's news

    2. BODY — 1-2 very short paragraphs that weave ALL the stories together into a flowing narrative. Do NOT separate stories with dividers or individual headlines. Merge related topics. Use <b>bold</b> for key facts, names, numbers. Use <i>italic</i> for analyst commentary or context. Use emojis sparingly within text for visual appeal. Pick only the most important stories — skip minor ones.

    3. TL;DR in a blockquote:
    <blockquote>📌 TL;DR: 1-2 sentences summarizing everything above.</blockquote>

    4. Sources in a blockquote:
    <blockquote>🔗 Sources: source names, comma separated</blockquote>

    STYLE:
    - Write in a neutral, informative but engaging tone
    - No filler, no greetings, no sign-offs
    - Prefer short punchy sentences
    - MERGE all articles into one unified narrative — never list them as separate stories
    - Group related themes together naturally
    - The digest should read like a quick morning briefing, not a list of headlines

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

    async def ask_anthropic(self, client: AsyncAnthropic, question: str, language: str = 'en', model: str = 'claude-haiku-4-5') -> Dict[str, Any]:
        system_prompt = build_system_prompt(language)
        async def _call():
            message = await client.messages.create(
                model=model,
                max_tokens=1024,
                system=system_prompt,
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

    async def ask_openai(self, client: AsyncOpenAI, question: str, language: str = 'en', model: str = 'gpt-4o-mini') -> Dict[str, Any]:
        system_prompt = build_system_prompt(language)
        async def _call():
            message = await client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
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

    async def summarize(self, articles, language='en'):
        logger.info(f"Summarizing with {self.provider} (language={language})")
        if self.provider == 'anthropic':
            return await self.ask_anthropic(self.client, question=articles, language=language)

        elif self.provider == 'openai':
            return await self.ask_openai(self.client, question=articles, language=language)