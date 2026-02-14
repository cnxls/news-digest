from difflib import SequenceMatcher
from pipeline.models import Article


class Deduplicator:
    SIMILARITY_THRESHOLD = 0.85

    def deduplicate(self, articles: list[Article]) -> list[Article]:   # [4]
        seen_urls = set()
        seen = []

        for article in articles:
            
            if article.link in seen_urls:                              # [7]
                continue

            is_duplicate = False                                       # [8]
            for kept in seen:
                ratio = SequenceMatcher(                               # [9]
                    None,
                    article.title.lower(),
                    kept.title.lower(),
                ).ratio()

                if ratio >= self.SIMILARITY_THRESHOLD:                 # [10]
                    is_duplicate = True
                    break

            if not is_duplicate:                                       # [11]
                seen_urls.add(article.link)
                seen.append(article)

        return seen                                                    # [12]
