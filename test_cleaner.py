from pipeline.models import Article
from pipeline.processors.cleaner import ArticleCleaner

dirty_articles = [
    Article(
        title="Test Article 1",
        link="https://example.com/1",
        source="test",
        summary='<p>AI &amp; ML are <b>growing</b> fast.</p>  <br/>  More info &lt;here&gt;.',
        content='<div class="post"><h1>Big News</h1><p>Paragraph   with   extra   spaces.</p></div>',
    ),
    Article(
        title="Test Article 2",
        link="https://example.com/2",
        source="test",
        summary="Already clean text, no HTML here.",
        content="",
    )
]

cleaner = ArticleCleaner()
cleaned = cleaner.clean(dirty_articles)

for i, (before, after) in enumerate(zip(dirty_articles, cleaned), 1):
    print(f"  BEFORE summary: {before.summary!r}")
    print(f"  AFTER  summary: {after.summary!r}")
    print(f"  BEFORE content: {before.content!r}")
    print(f"  AFTER  content: {after.content!r}")
    print()
