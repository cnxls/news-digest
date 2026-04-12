from pydantic import BaseModel, Field
from datetime import datetime
import json


class Article(BaseModel):
    category: str
    title: str
    link: str
    source: str
    published: str = ""
    content: str = ""
    summary: str = ""
    collected_at: datetime = Field(default_factory=datetime.now)
