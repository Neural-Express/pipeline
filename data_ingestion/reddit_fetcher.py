import praw
from datetime import datetime, timezone
from .utils import get_env_variable, standardize_article
import logging

logger = logging.getLogger(__name__)

def fetch_reddit_posts(subreddits=["MachineLearning", "singularity", "artificial", "LocalLLaMA"], limit=5):
    client_id = get_env_variable("REDDIT_CLIENT_ID")
    client_secret = get_env_variable("REDDIT_CLIENT_SECRET")
    user_agent = get_env_variable("REDDIT_USER_AGENT")

    if not all([client_id, client_secret, user_agent]):
        logger.warning("Missing Reddit API credentials.")
        return []

    reddit = praw.Reddit(client_id=client_id, client_secret=client_secret, user_agent=user_agent)
    posts = []
    for sub in subreddits:
        try:
            for post in reddit.subreddit(sub).new(limit=limit):
                posts.append(standardize_article(
                    post.title,
                    f"https://www.reddit.com{post.permalink}",
                    post.selftext if post.is_self else post.url,
                    datetime.fromtimestamp(post.created_utc, tz=timezone.utc).isoformat(),
                    f"Reddit - r/{sub}"
                ))
        except Exception as e:
            logger.exception(f"Reddit r/{sub} Error")
    return posts