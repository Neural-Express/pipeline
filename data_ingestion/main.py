from .arxiv_fetcher import fetch_arxiv_papers
from .reddit_fetcher import fetch_reddit_posts
from .twitter_fetcher import fetch_twitter_posts
from .github_trending_fetcher import fetch_github_trending
from .rss_fetcher import fetch_rss_feeds
from .newsapi_fetcher import fetch_news_ai_articles
from .newsdata_fetcher import fetch_newsdata
from .webzio_fetcher import fetch_webzio
from datetime import datetime
import json
import os

def safe_fetch(fetch_function, *args, **kwargs):
    """
    Wrapper to safely execute a fetch function and catch exceptions.
    """
    try:
        return fetch_function(*args, **kwargs) or []
    except Exception as e:
        print(f"Error during {fetch_function.__name__}: {e}")
        return []

if __name__ == '__main__':
    combined_data = []

    combined_data += safe_fetch(fetch_news_ai_articles)
    combined_data += safe_fetch(fetch_arxiv_papers)
    combined_data += safe_fetch(fetch_reddit_posts)
    combined_data += safe_fetch(fetch_twitter_posts)
    combined_data += safe_fetch(fetch_github_trending, "python")
    combined_data += safe_fetch(fetch_rss_feeds, ["https://www.technologyreview.com/feed/"])
    combined_data += safe_fetch(fetch_newsdata)
    combined_data += safe_fetch(fetch_webzio)

    # Ensure output directory exists
    os.makedirs("data", exist_ok=True)
    filename = f"data/news_{datetime.now().strftime('%Y-%m-%d')}.json"

    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(combined_data, f, indent=2, ensure_ascii=False)
        print(f"Fetched {len(combined_data)} articles. Saved to {filename}.")
    except Exception as e:
        print(f"Failed to save articles to {filename}: {e}")