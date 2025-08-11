import requests
from .utils import get_env_variable, standardize_article
import logging

logger = logging.getLogger(__name__)

def fetch_newsdata():
    api_key = get_env_variable("NEWSDATA_API_KEY")
    if not api_key:
        logger.warning("NEWSDATA_API_KEY not found.")
        return []
    try:
        url = f"https://newsdata.io/api/1/news?apikey={api_key}&q=artificial%20intelligence&language=en"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        articles = response.json().get("results", [])
        return [
            standardize_article(a["title"], a["link"], a.get("content", ""), a["pubDate"], "NewsData.io")
            for a in articles
        ]
    except Exception as e:
        logger.exception("NewsData Error")
        return []