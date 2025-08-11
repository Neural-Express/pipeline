# pipeline/deduplication/engine.py

import os
import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from deduplication.data_loader import load_texts_from_json

# ─── CONFIGURATION ─────────────────────────────────────────────────────────
# Use this relative path because you’ll run from pipeline/:
RAW_FOLDER    = "data_ingestion/data"

# If you ever run from a different CWD, you could switch to an absolute path:
# RAW_FOLDER = "/Users/ishansrivastava/Desktop/NeuralExpress/Developement/pipeline/data_ingestion/data"

INDEX_PATH    = "dedup.index"
EMBED_MODEL   = "all-MiniLM-L6-v2"
SIM_THRESHOLD = 0.85
# ────────────────────────────────────────────────────────────────────────────

# 1) Load the SBERT model
print(f"[INIT] Loading embedding model: {EMBED_MODEL}")
model = SentenceTransformer(EMBED_MODEL)
dim = model.get_sentence_embedding_dimension()
print(f"[INIT] Embedding dimension: {dim}")

# 2) Create or load the FAISS index
def load_or_create_index(path: str, dim: int):
    if os.path.exists(path):
        idx = faiss.read_index(path)
        print(f"[FAISS] Loaded existing index with {idx.ntotal} vectors.")
    else:
        idx = faiss.IndexFlatIP(dim)
        print("[FAISS] Created new index (IndexFlatIP).")
    return idx

index = load_or_create_index(INDEX_PATH, dim)

# 3) Helper to save the index
def save_index(idx, path: str):
    faiss.write_index(idx, path)
    print(f"[FAISS] Saved index with {idx.ntotal} vectors to '{path}'.")

# 4) Convert texts to normalized embeddings
def encode_texts(texts: list, batch_size: int = 64) -> np.ndarray:
    all_embs = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        embs = model.encode(batch, convert_to_numpy=True, show_progress_bar=False)
        faiss.normalize_L2(embs)  # in-place normalization for cosine similarity
        all_embs.append(embs)
    return np.vstack(all_embs)

# 5) Check duplicates vs. existing index
def filter_duplicates(texts: list, threshold: float):
    embs = encode_texts(texts)
    unique_idxs = []
    duplicate_idxs = []

    if index.ntotal == 0:
        # First run: everything is unique
        unique_idxs = list(range(len(texts)))
    else:
        # Search nearest neighbor (k=1) for each new embedding
        sims, _ = index.search(embs, k=1)
        for i, sim_val in enumerate(sims.flatten()):
            if sim_val < threshold:
                unique_idxs.append(i)
            else:
                duplicate_idxs.append(i)

    # Add only the unique embeddings to the index
    if unique_idxs:
        index.add(embs[unique_idxs])
        print(f"[FAISS] Added {len(unique_idxs)} new embeddings; index size now {index.ntotal}.")

    return unique_idxs, duplicate_idxs

# 6) Main routine: load → dedupe → save index → write uniques
if __name__ == "__main__":
    # A) Load raw texts from JSON
    texts = load_texts_from_json(RAW_FOLDER)
    print(f"[LOAD] Loaded {len(texts)} texts from '{RAW_FOLDER}'.")

    # B) Filter out duplicates
    unique_idxs, duplicate_idxs = filter_duplicates(texts, SIM_THRESHOLD)
    print(f"[RESULT] {len(unique_idxs)} unique, {len(duplicate_idxs)} duplicates filtered.")

    # C) Persist the FAISS index
    save_index(index, INDEX_PATH)

    # D) Write unique articles (full JSON objects) to a new file
    def load_articles(folder_path: str):
        articles_list = []
        for fname in os.listdir(folder_path):
            if not fname.endswith(".json"):
                continue
            path = os.path.join(folder_path, fname)
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                for art in data:
                    articles_list.append(art)
        return articles_list

    all_articles = load_articles(RAW_FOLDER)
    unique_articles = [all_articles[i] for i in unique_idxs]

    OUT_UNIQUE = "deduplication/unique_articles.json"
    os.makedirs(os.path.dirname(OUT_UNIQUE), exist_ok=True)
    with open(OUT_UNIQUE, "w", encoding="utf-8") as outf:
        json.dump(unique_articles, outf, ensure_ascii=False, indent=2)
    print(f"[SAVE] {len(unique_articles)} unique articles written to '{OUT_UNIQUE}'.")


# After dedup writes deduplication/unique_articles.json:
from pipeline.contracts.checks import load_json_array, ensure_article_fields, ensure_min_count

DEDUP_OUT = "deduplication/unique_articles.json"
items = load_json_array(DEDUP_OUT)
ensure_article_fields(items, ["title","url","published_date","source_platform","content"])
ensure_min_count(items, 5, DEDUP_OUT)  # adjust threshold
print("[CONTRACT] Deduplication output OK.")