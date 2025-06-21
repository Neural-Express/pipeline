# 🧠 Autonomous AI Newsletter & Services Pipeline

> An end-to-end automated pipeline to ingest, deduplicate, summarize, and publish weekly AI news content—scalable, reliable, and powered by LLMs.

---

## 🚀 Overview

This project is designed to solve the problem of manual AI news curation by building a fully automated system that:
- Gathers AI news from APIs and RSS feeds
- Deduplicates using embeddings + vector similarity
- Summarizes content with GPT-4.5 or Claude
- Publishes to Substack/Mailchimp
- Shares highlights on social media
- Tracks metrics in real time

---

## 👥 Team

This project is built and maintained by:
- Ishan2036924
- kshitizverma1220@gmail.com

Organization: https://github.com/Neural-Express


## 📁 Project Structure

/ingestion → APIs, scraping, and feed collection
/deduplication → Embeddings, Pinecone/FAISS integration
/summarization → LLM prompt logic + API calls
/publishing → HTML email templating + Substack/Mailchimp integration
/social → Auto-generate X/LinkedIn snippets
/monitoring → Logging, analytics, error handling
/notion → QA review, editor forms, task boards
/docs → Documentation, flowcharts, prompts



-------------------------------------------------------------------------

## 🧱 Tech Stack

| Layer         | Tool/Service                          |
|--------------|----------------------------------------|
| Ingestion     | Python, NewsAPI, ArXiv, Reddit, X API |
| Storage       | Notion DB, MongoDB                    |
| Embeddings    | OpenAI or SentenceTransformers        |
| Vector DB     | Pinecone or FAISS                     |
| Summarization | GPT-4.5, Claude                       |
| Orchestration | n8n, Zapier                           |
| Publishing    | Substack API, Mailchimp API           |
| Monitoring    | Sentry, Google Analytics              |
| Hosting       | GitHub Pages, Render, Vercel          |

---

| Module           | Description                                   |
| ---------------- | --------------------------------------------- |
| `ingest.py`      | Collects articles from APIs                   |
| `deduplicate.py` | Embeds + checks similarity via Pinecone/FAISS |
| `summarize.py`   | Summarizes articles using GPT/Claude          |
| `template.html`  | Newsletter layout                             |
| `publish.py`     | Pushes HTML to Substack                       |
| `social.py`      | Generates post snippets                       |



