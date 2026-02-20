from difflib import SequenceMatcher
from pipeline.models import Article


class Deduplicator:
    SIMILARITY_THRESHOLD = 0.85

    def deduplicate(self, articles: list[Article]) -> list[Article]:   
        seen_urls = set()
        seen = []

        for article in articles:
            
            if article.link in seen_urls:
                continue

            is_duplicate = False         
            for kept in seen:
                ratio = SequenceMatcher( 
                    None,
                    article.title.lower(),
                    kept.title.lower(),
                ).ratio()

                if ratio >= self.SIMILARITY_THRESHOLD:
                    is_duplicate = True
                    break

            if not is_duplicate:                      
                seen_urls.add(article.link)
                seen.append(article)

        return seen                                   
