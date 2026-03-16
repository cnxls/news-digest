from pipeline.delivery.base import BaseDelivery
from pipeline.config import settings
import re

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
            
            chunks.append(text[:4097])
            text = text[position + 1:]
    
        return chunks
