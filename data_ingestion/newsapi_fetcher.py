import requests
from datetime import datetime, timezone
from utils import get_env_variable, standardize_article
import logging

logger = logging.getLogger(__name__)

NEWS_API_KEY = get_env_variable("NEWS_API_KEY")

def fetch_news_ai_articles():
    if not NEWS_API_KEY:
        logger.warning("NEWS_API_KEY not found. Skipping NewsAPI.")
        return []

    query = "AI"
    url = (
        f"https://newsapi.org/v2/top-headlines?"
        f"q={query}&"
        "language=en&"
        "category=technology&"
        f"apiKey={NEWS_API_KEY}"
    )

    articles_processed = []
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        articles = response.json().get("articles", [])

        for article in articles:
            if article.get("title") and article.get("url") and article.get("publishedAt"):
                articles_processed.append(standardize_article(
                    article["title"],
                    article["url"],
                    article.get("description", "")[:500],
                    article["publishedAt"],
                    f"NewsAPI - {article.get('source', {}).get('name', 'Unknown')}"
                ))
    except Exception as e:
        logger.exception("NewsAPI Error")
    return articles_processed