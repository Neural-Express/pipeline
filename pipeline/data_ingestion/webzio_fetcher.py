import requests
from utils import get_env_variable, standardize_article
import logging

logger = logging.getLogger(__name__)

def fetch_webzio():
    api_key = get_env_variable("WEBZIO_API_KEY")
    if not api_key:
        logger.warning("WEBZIO_API_KEY not found.")
        return []

    try:
        url = f"https://api.webz.io/newsApiLite?token={api_key}&q=AI&size=5&sort=desc&from=3d"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        posts = data.get("posts", [])
        if not posts:
            logger.info("No posts found in Webz.io response.")
            return []

        articles = []
        for post in posts:
            title = post.get("title") or post.get("thread", {}).get("title") or "No title"
            url = post.get("url") or post.get("thread", {}).get("url") or ""
            content = post.get("text", "")
            published = post.get("published") or post.get("thread", {}).get("published") or ""

            try:
                article = standardize_article(title, url, content, published[:19], "webjio.io")
                articles.append(article)
            except Exception as e:
                logger.exception("Error standardizing article")

        return articles
    except Exception as e:
        logger.exception("Webz.io Error")
        return []