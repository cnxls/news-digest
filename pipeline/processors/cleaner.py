import re                          
from html import unescape          
from bs4 import BeautifulSoup      
from pipeline.models import Article 


class ArticleCleaner:

    def clean(self, articles: list[Article]) -> list[Article]:       
        return [self._clean_article(a) for a in articles]

    def _clean_article(self, article: Article) -> Article:           
        cleaned_summary = self._clean_text(article.summary)          
        cleaned_content = self._clean_text(article.content)          

        return article.model_copy(update={                           
            "summary": cleaned_summary,
            "content": cleaned_content,
        })

    def _clean_text(self, raw: str) -> str:                          
        if not raw:                                                  
            return ""

        text = BeautifulSoup(raw, "html.parser").get_text()          
        text = unescape(text)    
        text = re.sub(r'\s+', ' ', text).strip()                                                         
        return text
