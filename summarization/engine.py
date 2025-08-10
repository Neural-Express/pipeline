# pipeline/summarization/engine.py

import os
import json
from transformers import pipeline
import requests
from bs4 import BeautifulSoup

# ─── CONFIGURATION ───────────────────────────────────────────────────
INPUT_PATH   = "deduplication/unique_articles.json"
OUTPUT_PATH  = "summarization/summaries.json"
MODEL_NAME   = "sshleifer/distilbart-cnn-12-6"
TOP_K        = 20
# ─────────────────────────────────────────────────────────────────────

# Ensure output folder exists
os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

print(f"[MODEL] Loading summarization model: {MODEL_NAME}")
summarizer = pipeline("summarization", model=MODEL_NAME)

# 1) Load all deduplicated articles
with open(INPUT_PATH, "r", encoding="utf-8") as f:
    all_articles = json.load(f)
print(f"[LOAD] Loaded {len(all_articles)} total articles from '{INPUT_PATH}'.")

# 2) Sort by date descending and keep top K
all_articles.sort(
    key=lambda a: a.get("published_date", ""), 
    reverse=True
)
articles = all_articles[:TOP_K]
print(f"[SELECT] Processing top {len(articles)} articles by date.")

def fetch_image(url: str) -> str | None:
    """Fetch the Open Graph image URL from the article page, or None."""
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(res.content, "html.parser")
        og = soup.find("meta", property="og:image")
        if og and og.get("content"):
            return og["content"]
    except Exception as e:
        print(f"[IMAGE] Failed to fetch image for {url}: {e}")
    return None

summaries = []
for idx, art in enumerate(articles, start=1):
    title = art.get("title", "").strip()
    content = art.get("content", "").strip()
    url     = art.get("url", "")

    text = title + "\n\n" + content
    print(f"[SUMMARIZE] ({idx}/{len(articles)}) {title[:60]}")

    # 3) Summarize
    try:
        result = summarizer(
            text,
            max_length=100,
            min_length=20,
            do_sample=False
        )[0]
        summary_text = result["summary_text"].strip()
    except Exception as e:
        print(f"[ERROR] Summarization failed for '{title}': {e}")
        summary_text = ""

    # 4) Fetch article image (fallback to None)
    image_url = fetch_image(url) if url else None

    summaries.append({
        "title":           title,
        "url":             url,
        "published_date":  art.get("published_date"),
        "source_platform": art.get("source_platform"),
        "summary":         summary_text,
        "image":           image_url
    })

# 5) Save top-K summaries
with open(OUTPUT_PATH, "w", encoding="utf-8") as outf:
    json.dump(summaries, outf, ensure_ascii=False, indent=2)
print(f"[SAVE] Wrote {len(summaries)} summaries (with images) to '{OUTPUT_PATH}'.")



from pipeline.contracts.checks import load_json_array, ensure_article_fields, ensure_min_count, write_json

OUT = "summarization/summaries.json"

# ... your summarization code that writes OUT ...

# Validate summarization contract:
summaries = load_json_array(OUT)
ensure_article_fields(summaries, ["title","url","published_date","source_platform","summary"])
ensure_min_count(summaries, 5, OUT)
print("[CONTRACT] Summarization output OK.")