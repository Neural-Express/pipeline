import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from utils import standardize_article
import logging

logger = logging.getLogger(__name__)

def fetch_github_trending(language=""):
    url = f"https://github.com/trending/{language}" if language else "https://github.com/trending"
    headers = {"User-Agent": "Mozilla/5.0"}
    repos = []
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        for article in soup.find_all("article", class_="Box-row"):
            a_tag = article.find("h2").find("a")
            repo_url = f"https://github.com{a_tag['href']}"
            name = a_tag.text.strip()
            desc = article.find("p")
            summary = desc.text.strip() if desc else "No description."
            lang = article.find("span", itemprop="programmingLanguage")
            lang_text = lang.text if lang else "N/A"
            repos.append(standardize_article(
                name,
                repo_url,
                f"Language: {lang_text}. {summary}",
                datetime.now(timezone.utc).isoformat(),
                f"GitHub Trending ({language or 'Overall'})"
            ))
    except Exception as e:
        logger.exception("GitHub Trending Error")
    return repos