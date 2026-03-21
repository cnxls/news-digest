from pipeline.delivery.base import BaseDelivery
from pipeline.config import settings
from pipeline.logger import get_logger
import requests

logger = get_logger()

class TelegramDelivery(BaseDelivery):
    
    def __init__(self):
        self.token = settings.telegram_bot_token
        self.chat_id = settings.telegram_chat_id
        self.api_url = f"https://api.telegram.org/bot{self.token}/sendMessage"

    def split_message(self,text):
        
        chunks = []
        while text:
            if len(text) <= 4096:
                chunks.append(text)
                break

            position = text.rfind("\n", 0, 4096)
            if position == -1:
                position = 4096

            chunks.append(text[:position])
            text = text[position + 1:]
    
        return chunks

    def deliver(self,digest: str) -> bool:

        chunks = self.split_message(digest)
        for chunk in chunks:
            payload = {
                "chat_id":self.chat_id,
                "text": chunk,
                "parse_mode":"Markdown"
            }
            response = requests.post(self.api_url,json=payload,timeout=20)


            if not response.ok:
                logger.error(f"Tg API error:{response.status_code} - {response.text}")
                return False

        logger.info("Digest delivered to Tg successfully")
        return True