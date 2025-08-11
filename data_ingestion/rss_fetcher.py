import feedparser
from datetime import datetime, timezone
import time
from .utils import standardize_article
import logging

logger = logging.getLogger(__name__)

def fetch_rss_feeds(urls):
    all_articles = []
    for url in urls:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries:
                published = datetime.now(timezone.utc).isoformat()
                if hasattr(entry, 'published_parsed'):
                    published = datetime.fromtimestamp(time.mktime(entry.published_parsed), tz=timezone.utc).isoformat()
                all_articles.append(standardize_article(
                    getattr(entry, 'title', 'No title'),
                    getattr(entry, 'link', ''),
                    getattr(entry, 'summary', '')[:1000],
                    published,
                    f"RSS - {feed.feed.get('title', url)}"
                ))
        except Exception as e:
            logger.exception(f"RSS Error ({url})")
    return all_articles