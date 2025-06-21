# pipeline/summarization/engine.py

import os
import json
from transformers import pipeline

# ─── CONFIGURATION ───────────────────────────────────────────────────
# Input: the deduplicated articles from Step 1
INPUT_PATH = "deduplication/unique_articles.json"
# Output: where to write the summaries
OUTPUT_PATH = "summarization/summaries.json"
# Choose a small, fast summarization model from Hugging Face
MODEL_NAME  = "sshleifer/distilbart-cnn-12-6"
# ─────────────────────────────────────────────────────────────────────

# Ensure output folder exists
os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

# 1) Load the summarization pipeline
print(f"[MODEL] Loading summarization model: {MODEL_NAME}")
summarizer = pipeline("summarization", model=MODEL_NAME)

# 2) Load all unique articles
with open(INPUT_PATH, "r", encoding="utf-8") as f:
    articles = json.load(f)
print(f"[LOAD] Loaded {len(articles)} articles from '{INPUT_PATH}'.")

# 3) Summarize each article
summaries = []
for idx, art in enumerate(articles):
    title = art.get("title", "").strip()
    content = art.get("content", "").strip()
    # Combine title + content for context
    text = title + "\n\n" + content

    print(f"[SUMMARIZE] ({idx+1}/{len(articles)}) Summarizing: {title[:50]}...")
    try:
        # Generate a single summary string
        result = summarizer(
            text,
            max_length=100,   # at most 100 tokens
            min_length=20,    # at least 20 tokens
            do_sample=False   # deterministic output
        )[0]
        summary_text = result["summary_text"].strip()
    except Exception as e:
        print(f"[ERROR] Article {idx} summarization failed: {e}")
        summary_text = ""

    summaries.append({
        "title": title,
        "url": art.get("url"),
        "published_date": art.get("published_date"),
        "source_platform": art.get("source_platform"),
        "summary": summary_text
    })

# 4) Save summaries to JSON
with open(OUTPUT_PATH, "w", encoding="utf-8") as outf:
    json.dump(summaries, outf, ensure_ascii=False, indent=2)
print(f"[SAVE] Saved {len(summaries)} summaries to '{OUTPUT_PATH}'.")
