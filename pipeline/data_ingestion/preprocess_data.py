import re
from datetime import datetime, timezone
from dateutil import parser as date_parser
from bs4 import BeautifulSoup
import os
import json

# 1) A growing list of substrings that commonly appear in “no content” placeholders.
PLACEHOLDER_PATTERNS = [
    r"unavailable",       # catches “unavailable”, “is unavailable”, etc.
    r"paid plan",         # catches “ONLY AVAILABLE IN PAID PLANS”
    r"no preview",        # “NO PREVIEW AVAILABLE”
    r"full text is",      # “Full text is unavailable…”
    r"subscription",      # “subscription required”, etc.
    r"sign in to read",   # “Sign in to read the full article”
    r"read more at",      # “Read more at …” placeholders
    r"content unavailable"
]

# Compile into a single case-insensitive regex:
PLACEHOLDER_REGEX = re.compile(
    r"(" + r"|".join(PLACEHOLDER_PATTERNS) + r")",
    flags=re.IGNORECASE
)

def is_placeholder_content(text: str) -> bool:
    """
    Return True if `text` looks like a placeholder (no real article body).
    - Contains any phrase from PLACEHOLDER_PATTERNS (case-insensitive).
    - OR is extremely short (< 20 chars after stripping).
    """
    if not text:
        return True

    stripped = text.strip()
    # 1) If it matches any known “no content” phrase:
    if PLACEHOLDER_REGEX.search(stripped):
        return True

    # 2) If it’s too short to be a real summary:
    if len(stripped) < 20:
        return True

    return False

# def standardize_iso_date(date_str: str) -> str | None:
#     """
#     Parse date_str into UTC ISO 8601 string (YYYY-MM-DDTHH:MM:SSZ).
#     Returns None if parsing fails.
#     """
#     if not date_str:
#         return None
#     try:
#         dt = date_parser.parse(date_str)
#         if not dt.tzinfo:
#             dt = dt.replace(tzinfo=timezone.utc)
#         return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
#     except Exception:
#         return None

def clean_html(raw_html: str) -> str:
    """
    Remove HTML tags and collapse whitespace.
    """
    text = BeautifulSoup(raw_html or "", "html.parser").get_text()
    return re.sub(r"\s+", " ", text).strip()

def preprocess_articles(raw_articles: list[dict]) -> list[dict]:
    """
    Input: raw_articles = [ { ... }, { ... }, ... ]
    Output: cleaned list where each dict has:
      { "title": str, "url": str, "content": str, 
        "published_date": str (ISO 8601), "source_platform": str }
    """
    cleaned = []
    for a in raw_articles:
        # 1) Extract fields (provide empty defaults)
        title_raw = a.get("title", "")
        url_raw = a.get("url", "")
        content_raw = a.get("content", "") or a.get("text", "")
        date_raw = a.get("published_date", "") or a.get("published", "")
        source = a.get("source_platform", "").strip()

        # Skip if title or URL is missing entirely:
        if not title_raw or not url_raw:
            continue

        # 2) Strip HTML and whitespace
        title = clean_html(title_raw)
        content = clean_html(content_raw)

        # 3) Detect placeholder content and zero it out
        if is_placeholder_content(content):
            content = ""

        # # 4) Normalize date
        # iso_date = date_raw
        # if not iso_date:
        #     # If date parsing fails, set it to current UTC time (or skip)
        #     iso_date = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        # 5) Build final record
        cleaned.append({
            "title": title,
            "url": url_raw.strip(),
            "content": content,
            "published_date": date_raw,
            "source_platform": source
        })

    return cleaned

if __name__ == '__main__':
    
    with open(f"data/news_{datetime.now().strftime('%Y-%m-%d')}", "r", encoding="utf-8") as out_f:
        data = json.load(out_f)

    cleaned_data=preprocess_articles(data)

    filename = f"data/cleaned_news_{datetime.now().strftime('%Y-%m-%d')}.json"

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(cleaned_data, f, indent=2, ensure_ascii=False)

    print(f"Fetched {len(cleaned_data)} articles. Saved to {filename}.")