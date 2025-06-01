import os
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file safely
try:
    dotenv_path = Path("..") / ".env"
    if dotenv_path.exists():
        load_dotenv(dotenv_path=dotenv_path)
    else:
        print(f"Warning: .env file not found at {dotenv_path}")
except Exception as e:
    print(f"Error loading .env file: {e}")

def get_env_variable(key):
    """
    Safely get an environment variable.
    """
    value = os.getenv(key)
    if not value:
        print(f"Environment variable '{key}' not found.")
    return value

def standardize_article(title, url, content, published_date, source):
    """
    Standardizes article metadata for consistent storage/processing.
    """
    try:
        if published_date:
            published_date = datetime.fromisoformat(
                published_date.replace('Z', '+00:00')
            ).isoformat()
    except Exception as e:
        print(f"Date parsing error for '{published_date}': {e}. Using current UTC time.")
        published_date = datetime.utcnow().isoformat()

    return {
        "title": title or "Untitled",
        "url": url or "",
        "content": content or "",
        "published_date": published_date,
        "source_platform": source or "Unknown"
    }