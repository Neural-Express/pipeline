import arxiv
from utils import standardize_article
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def fetch_arxiv_papers(query="LLM OR 'Large Language Model' OR 'Artificial Intelligence'", max_results=10):
    results = []
    try:
        client = arxiv.Client()
        search = arxiv.Search(query=query, max_results=max_results, sort_by=arxiv.SortCriterion.SubmittedDate)
        for r in client.results(search):
            results.append(standardize_article(
                r.title,
                r.entry_id,
                r.summary,
                r.published.isoformat(),
                "arXiv"
            ))
    except Exception as e:
        logger.exception("arXiv Error")
    return results