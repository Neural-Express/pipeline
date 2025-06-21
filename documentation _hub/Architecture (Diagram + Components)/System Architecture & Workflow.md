# System Architecture & Workflow

This section outlines the **full end-to-end architecture** of our AI-powered newsletter automation pipeline — from data ingestion to publishing, all orchestrated using modern AI and low-code tools.

---

### 🔧 **High-Level Architecture**

```
[ APIs & RSS ] --> [ Ingestion Scripts ] --> [ Raw Data Staging (DB) ]
                                      ↓
                         [ Deduplication via Embeddings ]
                                      ↓
                           [ LLM-based Summarization ]
                                      ↓
                          [ Newsletter Draft Assembly ]
                                      ↓
          [ Optional QA in Notion ] --> [ Final Publish (Email + Web) ]
                                      ↓
                        [ Social Media Auto Posts ]
                                      ↓
                        [ Analytics & Monitoring Logs ]

```

---

### 🔁 **Automated Workflow – Step-by-Step**

```latex
flowchart TD
  A[1. Scheduler Trigger] --> B[2. Fetch Articles from APIs]
  B --> C[3. Store Raw Data in Notion/MongoDB]
  C --> D[4. Generate Text Embeddings]
  D --> E{5. Duplicate?}
  E -- Yes --> F[6. Archive & Skip]
  E -- No --> G[7. Summarize + Categorize LLMs]
  G --> H[8. Store Summaries in DB]
  H --> I[9. Create HTML Newsletter Draft]
  I --> J{10. QA Enabled?}
  J -- Yes --> K[11. Notion QA Approval]
  J -- No --> L[12. Publish Newsletter] [(Mailchimp/Substack)]
  K --> L
  L --> M[13. Auto-post on Twitter, LinkedIn via Zapier]
  L --> N[14. Store Issue Archive]
  N --> O[15. Send Logs to Sentry + Analytics Dashboard]

```

---

### 🔄 **Module Breakdown**

| **Stage** | **Description** | **Tools Used** |
| --- | --- | --- |
| **1. Trigger** | Weekly scheduled job (e.g., every Wednesday at 10 AM IST) | n8n, Zapier, GitHub Actions |
| **2. Ingestion** | Pull fresh AI-related news, research, tweets | Python scripts, APIs (NewsAPI, ArXiv, Reddit, X/Twitter) |
| **3. Staging DB** | Store unprocessed data for deduplication | Notion DB (starter), MongoDB/Firestore (scalable) |
| **4. Embedding** | Generate semantic vectors for text comparison | OpenAI / SentenceTransformer |
| **5. Deduplication** | Avoid repeating stories by comparing with last week’s | Pinecone or FAISS vector DB |
| **6. Archive** | Store duplicates safely for audit | MongoDB, local CSV |
| **7. Summarization** | Use GPT-4.5 or Claude to summarize key points | Prompt engineering |
| **8. DB Save** | Structured summary, tags, source links | Notion or Airtable |
| **9. Drafting** | Compile summaries into a pre-designed HTML/CSS newsletter layout | GPT-driven + HTML templating |
| **10. QA** | Optional editor review via Notion form or view | Notion form integration |
| **11. Publishing** | Push to subscribers via Mailchimp or Substack API | Email API integration |
| **12. Social Sharing** | Top 3 stories auto-shared to social platforms | Zapier, Buffer |
| **13. Archival & Logs** | Save full issue for archive and emit system logs | Notion, MongoDB, Sentry |
| **14. Analytics** | Open rate, CTR, error rate, feedback | Substack analytics, Google Analytics |

---

### 🧠 **Design Philosophy**

- **Separation of Concerns**: Every task (fetching, deduplication, summarization, QA, publishing) is modular.
- **AI-Native**: Use LLMs not just for summarizing, but also for newsletter layout, social copy, and headlines.
- **Fail-Safe Architecture**: Each stage logs errors and failures for monitoring and retry mechanisms.
- **Scalable Base**: Built to grow from a simple newsletter to full content/media + AI solutions studio.

---