from pydantic_settings import BaseSettings
from pydantic import Field
import datetime 

class Article(BaseSettings):
    title: str         
    link: str  

    source: str
    published: str = ""     
    
    summary: str = ""
    collected_at: datetime = Field(default_factory=datetime.utcnow)   
