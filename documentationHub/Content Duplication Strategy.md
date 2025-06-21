# Content Duplication Strategy

## ✅  Content Deduplication Strategy

Ensuring that your newsletter delivers **fresh, unique content** every week is crucial for subscriber engagement and credibility. This step details how to identify and filter out duplicate or repeated news items effectively.

---

### **1. Embeddings Generation**

- For each newly fetched article or news item, generate a vector embedding representing its content using:
    - **OpenAI Embedding API** (e.g., `text-embedding-ada-002` model), or
    - **SentenceTransformers** (an open-source alternative).
- Input for embedding: Combine **title + summary/abstract** or first 100–200 words of the article.

---

### **2. Vector Storage**

- Store these embeddings in a **vector database** optimized for similarity search:
    - Options: **Pinecone**, **FAISS**, or **Weaviate**.
- Keep embeddings for at least the past **7 days** (or longer if preferred).

---

### **3. Similarity Check**

- When a new article embedding is created, run a similarity query against the stored embeddings.
- Use **cosine similarity** as the metric.
- Define a threshold (e.g., **≥ 0.85 similarity**) to consider two articles duplicates or near-duplicates.

---

### **4. Additional Metadata Checks**

- Compare URLs and publication timestamps to prevent false positives.
- Consider small content changes but identical URLs as duplicates.
- Flag potential duplicates for manual review if unsure.

---

### **5. Action on Duplicates**

- **If duplicate:** Archive the new article; do not include it in the newsletter.
- **If unique:** Mark as eligible for summarization and inclusion.

---

### **6. Archive Management**

- Maintain an archive database with all published and filtered articles for audit and analysis.
- This supports improving deduplication logic and tracing content sources.

---

### **7. Continuous Improvement**

- Periodically review edge cases where duplicates were missed or false positives occurred.
- Adjust similarity threshold and embedding input accordingly.
- Allow editors to manually override duplicates in the Notion dashboard.

---

**Summary:**

This strategy balances automation with precision, ensuring your newsletter remains engaging by sending unique, up-to-date AI news every week without unnecessary repetition.

---