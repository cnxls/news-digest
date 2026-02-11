from pydantic import BaseModel, Field
from datetime import datetime
import json


class Article(BaseModel):
    title: str
    link: str
    source: str
    published: str = ""
    summary: str = ""
    collected_at: datetime = Field(default_factory=datetime.now)

    @staticmethod
    def to_dict(items_list, filename):
        with open(filename, 'w') as file:
            json.dump(items_list, file, indent = 2)