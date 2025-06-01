# High-Level Architecture

```flow
st=>start: Weekly Trigger (GitHub Actions / n8n)
op1=>operation: Scrape Sources (ArXiv, NewsAPI, Reddit, Twitter, GitHub)
op2=>operation: Store Raw Items (JSON/DB)
op3=>operation: Deduplicate (Embeddings + FAISS/Pinecone)
op4=>operation: Summarize & Categorize (GPT-4.5 via LangChain)
op5=>operation: Assemble HTML/Markdown Newsletter
op6=>operation: (Optional) Notion QA Review
op7=>operation: Publish via Substack API
e=>end: Analytics Logging & Alerts

st->op1->op2->op3->op4->op5->op6->op7->e
```