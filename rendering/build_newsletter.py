# pipeline/rendering/build_newsletter.py
# Neural Express — Substack-friendly HTML generator (white theme, refined header, subtle divider, section chips)

import os, json, re, base64
from datetime import datetime, timezone
from html import escape
from typing import List, Dict, Optional
from urllib.parse import urlparse
import os, sys

# add project root to sys.path so "pipeline.*" imports work when running the file directly
HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(HERE)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(HERE)
PARENT_OF_PROJECT = os.path.dirname(PROJECT_ROOT)
if PARENT_OF_PROJECT not in sys.path:
    sys.path.insert(0, PARENT_OF_PROJECT)

# now import from the local package
from pipeline.contracts.checks import load_json_array, ensure_article_fields, ContractError

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(HERE)
SUMMARY_FILE = os.path.join(PROJECT_ROOT, "summarization", "summaries.json")

OUT_FULL = os.path.join(HERE, "newsletter.html")            # web preview
OUT_FRAG = os.path.join(HERE, "newsletter_fragment.html")   # Substack paste

# Logo (public URL or local path -> will be embedded as data URI)
LOGO_PATH_OR_URL = os.getenv("NEWSLETTER_LOGO", os.path.join(HERE, "assets", "logo.png"))

# Logo look
MAX_LOGO_WIDTH_PX  = 560
MAX_LOGO_HEIGHT_PX = 150
LOGO_RADIUS_PX     = 16

# Palette (warmer accent)
ACCENT        = "#1f7aec"  # button/links
ACCENT_SOFT   = "#eaf2ff"  # soft bg chips
ACCENT_LINE   = "#cfe0ff"  # chip border
TEXT_MAIN     = "#171717"
TEXT_SECOND   = "#5f6368"
BG_PAGE       = "#ffffff"
BORDER_SOFT   = "#eaeaea"

# ───────────────────────── helpers ─────────────────────────
def norm_title(t: str) -> str:
    return " ".join((t or "").split())

def first_sentence(text: str, max_chars=180) -> str:
    if not text:
        return ""
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    s = parts[0] if parts else text.strip()
    return (s[:max_chars].rstrip() + "…") if len(s) > max_chars else s

def other_sentences(text: str, limit=3, min_len=25) -> List[str]:
    if not text:
        return []
    parts = re.split(r"(?<=[.!?])\s+", text.strip())[1:]
    return [p.strip() for p in parts if len(p.strip()) >= min_len][:limit]

def guess_category(title: str, source: str) -> str:
    t = f"{(title or '').lower()} {(source or '').lower()}"
    if "github" in t or "open source" in t:
        return "OPEN SOURCE"
    if any(k in t for k in ["paper", "arxiv", "benchmark", "study", "research"]):
        return "AI RESEARCH"
    if any(k in t for k in ["act", "law", "policy", "regulat"]):
        return "POLICY"
    if any(k in t for k in ["launch", "release", "ship", "beta", "announce"]):
        return "PRODUCT"
    return "TOOLS"

EMOJI = {"PRODUCT":"🚀","AI RESEARCH":"🧬","OPEN SOURCE":"📦","POLICY":"🏛️","TOOLS":"🛠️"}

def estimate_read_time(words: int, wpm: int = 220) -> int:
    return max(1, round(words / float(wpm)))

def domain_of(url: Optional[str]) -> Optional[str]:
    if not url: return None
    try:
        return urlparse(url).netloc.lower()
    except Exception:
        return None

# ───────────────────────── logo helpers ─────────────────────────
def resolve_logo_src(path_or_url: str) -> Optional[str]:
    if not path_or_url:
        return None
    low = path_or_url.lower()
    if low.startswith(("http://", "https://")):
        return path_or_url
    if os.path.exists(path_or_url) and os.path.isfile(path_or_url):
        with open(path_or_url, "rb") as f:
            data = f.read()
        ext = os.path.splitext(path_or_url)[1].lower()
        mime = "image/png"
        if ext in (".jpg", ".jpeg"): mime = "image/jpeg"
        elif ext == ".svg": mime = "image/svg+xml"
        return f"data:{mime};base64,{base64.b64encode(data).decode('ascii')}"
    return None

def make_logo_html(path_or_url: str) -> str:
    src = resolve_logo_src(path_or_url)
    if not src:
        return ""
    return (
        f'<img src="{escape(src)}" alt="Neural Express" '
        f'style="display:block;margin:0 auto;padding:0;border:0;'
        f'max-width:{MAX_LOGO_WIDTH_PX}px;height:auto;width:auto;'
        f'max-height:{MAX_LOGO_HEIGHT_PX}px;border-radius:{LOGO_RADIUS_PX}px;">'
    )

# ───────────────────────── layout ─────────────────────────
BASE_HTML = f"""
<div style="background:{BG_PAGE}; margin:0; padding:28px;">
  <div style="max-width:760px; margin:0 auto; font-family:-apple-system,system-ui,Segoe UI,Roboto,Arial,sans-serif; color:{TEXT_MAIN};">

    <!-- Header: clean logo + edition (no box) -->
    <div style="padding:0;margin:0;text-align:center;">
      <div style="margin-bottom:10px;">{{LOGO_HTML}}</div>
      <div style="display:inline-block;background:{ACCENT_SOFT};border:1px solid {ACCENT_LINE};
                  color:{TEXT_SECOND};font-size:12px;padding:6px 10px;border-radius:999px;">
        Edition: {{DATE}}
      </div>
      <!-- subtle divider under header -->
      <div style="height:1px;margin:18px auto 0 auto;max-width:760px;
                  background:linear-gradient(90deg, rgba(0,0,0,0) 0%, {BORDER_SOFT} 20%, {BORDER_SOFT} 80%, rgba(0,0,0,0) 100%);"></div>
    </div>

    <!-- Issue meta -->
    <div style="text-align:center; color:{TEXT_SECOND}; font-size:12px; margin:10px 0 18px 0;">
      {{ISSUE_META}}
    </div>

    <!-- Quick nav chips -->
    <div style="text-align:center; margin:0 0 14px 0;">
      {{CHIPS}}
    </div>

    <!-- Intro -->
    <div style="background:{BG_PAGE}; border:1px solid {BORDER_SOFT}; border-radius:14px; padding:16px 18px; margin:12px 0 20px 0; color:{TEXT_SECOND};">
      <p style="margin:0; font-size:16px; line-height:1.6;">Your weekly summary of what actually mattered in AI. Grab a coffee ☕️.</p>
    </div>

    <!-- Top bullets -->
    <div style="background:{BG_PAGE}; border:1px solid {BORDER_SOFT}; border-radius:14px; padding:18px; margin:0 0 22px 0;">
      <h2 style="margin:0 0 10px 0; font-size:18px; color:{TEXT_MAIN};">In today’s brief</h2>
      {{BULLETS}}
    </div>

    <!-- Sections -->
    {{SECTIONS}}

    <!-- Footer -->
    <div style="text-align:center; color:{TEXT_SECOND}; font-size:12px; margin-top:28px;">
      <hr style="border:none; border-top:1px solid {BORDER_SOFT}; margin:16px 0;">
      You’re receiving this because you subscribed to <strong>Neural Express</strong>.
    </div>
  </div>
</div>
"""

def build_top_bullets(articles: List[Dict], limit=6) -> str:
    items = []
    for a in articles[:limit]:
        title = escape(norm_title(a.get("title", "Untitled") or ""))
        url   = a.get("url") or "#"
        items.append(f'<li style="margin:6px 0;"><a href="{escape(url)}" style="color:{ACCENT}; text-decoration:underline;">{title}</a></li>')
    return '<ul style="margin:0; padding-left:20px; list-style:square;">' + "".join(items) + '</ul>'

def article_block(a: Dict) -> str:
    title = escape(norm_title(a.get("title", "Untitled") or ""))
    url = a.get("url") or "#"
    source = escape(a.get("source_platform", "") or "")
    date = escape(a.get("published_date", "") or "")
    summary = (a.get("summary", "") or "").strip()

    rundown = first_sentence(summary)
    details = other_sentences(summary)

    details_html = ""
    if details:
        lis = "".join([f'<li style="margin:4px 0; color:{TEXT_SECOND};">{escape(d)}</li>' for d in details])
        details_html = f'<p style="margin:0 0 8px 0; color:{TEXT_SECOND};"><strong>Key points</strong></p><ul style="margin:0; padding-left:18px; list-style:disc;">{lis}</ul>'

    return f"""
    <div style="background:{BG_PAGE}; border:1px solid {BORDER_SOFT}; border-radius:14px; padding:18px; margin:0 0 18px 0;">
      <h3 style="margin:0 0 6px 0; font-size:18px; line-height:1.35; color:{TEXT_MAIN};">
        <a href="{escape(url)}" style="color:{TEXT_MAIN}; text-decoration:none;">{title}</a>
      </h3>
      <div style="color:{TEXT_SECOND}; font-size:12px; margin-bottom:10px;">
        <em>{source}{(" • " + date) if date else ""}</em>
      </div>
      <p style="margin:0 0 10px 0; color:{TEXT_MAIN};">
        <strong style="color:{ACCENT};">The Rundown:</strong> {escape(rundown) if rundown else "Read the full story for details."}
      </p>
      {details_html}
      <div style="margin-top:12px;">
        <a href="{escape(url)}" style="display:inline-block; background:{ACCENT}; color:#ffffff; padding:10px 14px; border-radius:10px; text-decoration:none; font-size:14px;">Read more →</a>
      </div>
    </div>
    """.strip()

def section_block(section_name: str, articles: List[Dict], anchor: str) -> str:
    emoji = EMOJI.get(section_name, "📌")
    header = (
        f'<div id="{anchor}" style="display:flex; align-items:center; gap:10px; margin:24px 0 12px 0;">'
        f'  <div style="flex:0 0 auto; font-size:22px">{emoji}</div>'
        f'  <div style="background:{ACCENT_SOFT}; color:{ACCENT}; border:1px solid {ACCENT_LINE}; padding:6px 10px; border-radius:999px; font-weight:600; font-size:12px; letter-spacing:0.4px;">{escape(section_name.title())}</div>'
        '</div>'
    )
    return header + "\n".join(article_block(a) for a in articles)

def chips_nav(available_sections: List[str]) -> str:
    parts = []
    for sec in available_sections:
        anchor = sec.lower().replace(" ", "-")
        parts.append(
            f'<a href="#{anchor}" style="display:inline-block;margin:4px; padding:6px 10px; '
            f'background:{ACCENT_SOFT}; border:1px solid {ACCENT_LINE}; color:{ACCENT}; '
            f'border-radius:999px; font-size:12px; text-decoration:none;">{escape(sec.title())}</a>'
        )
    return "".join(parts)

# ───────────────────────── main ─────────────────────────
def main(limit_total: int = 15) -> None:
    if not os.path.exists(SUMMARY_FILE):
        raise FileNotFoundError(f"Not found: {SUMMARY_FILE}")
    try:
        items = load_json_array(SUMMARY_FILE)
        ensure_article_fields(items, ["title","url","published_date","source_platform","summary"])
        print("[CONTRACT] Summaries OK.")
    except ContractError as e:
        print(str(e))
        raise

    # dedupe + sort
    seen = set()
    cleaned: List[Dict] = []
    for a in items:
        key = (a.get("url"), norm_title(a.get("title") or ""))
        if key in seen: continue
        seen.add(key)
        cleaned.append(a)
    cleaned.sort(key=lambda x: x.get("published_date", ""), reverse=True)
    articles = cleaned[:limit_total]

    # meta
    total_words = sum(len((a.get("summary") or "").split()) for a in articles)
    read_min = estimate_read_time(total_words)
    unique_sources = sorted({domain_of(a.get("url")) for a in articles if domain_of(a.get("url"))})
    issue_meta = f"{len(articles)} stories • {len(unique_sources)} sources • {read_min} min read"

    # group by category
    grouped: Dict[str, List[Dict]] = {"PRODUCT": [], "AI RESEARCH": [], "OPEN SOURCE": [], "POLICY": [], "TOOLS": []}
    for a in articles:
        cat = a.get("category") or guess_category(a.get("title", ""), a.get("source_platform", ""))
        grouped.setdefault(cat, [])
        grouped[cat].append(a)

    order = ["PRODUCT", "AI RESEARCH", "OPEN SOURCE", "POLICY", "TOOLS"]
    available = [sec for sec in order if grouped.get(sec)]
    sections_html = "\n".join(
        section_block(sec, grouped[sec], anchor=sec.lower().replace(" ", "-")) for sec in order if grouped.get(sec)
    )
    chips = chips_nav(available)

    bullets = build_top_bullets(articles)
    issue_date = datetime.now(timezone.utc).strftime("%b %d, %Y (UTC)")
    logo_html = make_logo_html(LOGO_PATH_OR_URL)

    html_body = (BASE_HTML
                 .replace("{DATE}", issue_date)
                 .replace("{BULLETS}", bullets)
                 .replace("{SECTIONS}", sections_html)
                 .replace("{LOGO_HTML}", logo_html)
                 .replace("{ISSUE_META}", escape(issue_meta))
                 .replace("{CHIPS}", chips))

    full_html = (
        f"<!DOCTYPE html><html lang='en'><meta charset='utf-8'>"
        f"<meta name='viewport' content='width=device-width, initial-scale=1'>"
        f"<title>Neural Express — Weekly AI Brief</title>"
        f"<body style='margin:0;background:{BG_PAGE};'>{html_body}</body></html>"
    )

    with open(OUT_FULL, "w", encoding="utf-8") as out: out.write(full_html)
    with open(OUT_FRAG, "w", encoding="utf-8") as out: out.write(html_body)
    print(f"[BUILD] {OUT_FULL} generated for {issue_date}")
    print(f"[BUILD] {OUT_FRAG} generated (Substack paste)")

if __name__ == "__main__":
    main()