# pipeline/deduplication/data_loader.py

import os
import json

def load_texts_from_json(folder_path: str):
    """
    Read all JSON files in folder_path, extract and return a list of texts
    (title + content) for embedding.
    """
    texts = []
    for fname in os.listdir(folder_path):
        if not fname.endswith(".json"):
            continue
        path = os.path.join(folder_path, fname)
        with open(path, "r", encoding="utf-8") as f:
            articles = json.load(f)
            for art in articles:
                title = art.get("title", "").strip()
                content = art.get("content", "").strip()
                text = title
                if content:
                    text += "  " + content
                texts.append(text)
    return texts
