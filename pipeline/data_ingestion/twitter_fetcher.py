import tweepy
from datetime import timezone
from utils import get_env_variable, standardize_article
import logging

logger = logging.getLogger(__name__)

BEARER_TOKEN = get_env_variable("TWITTER_BEARER_TOKEN")

def fetch_twitter_posts(query="AI OR #ArtificialIntelligence OR #LLM -is:retweet lang:en", max_results=10):
    if not BEARER_TOKEN:
        logger.warning("Missing Twitter Bearer Token.")
        return []
    try:
        client = tweepy.Client(bearer_token=BEARER_TOKEN)
        response = client.search_recent_tweets(query=query, max_results=max_results, tweet_fields=["created_at", "author_id", "text"])
        tweets = []
        for tweet in response.data or []:
            tweets.append(standardize_article(
                f"Tweet by {tweet.author_id}: {tweet.text[:70]}...",
                f"https://twitter.com/{tweet.author_id}/status/{tweet.id}",
                tweet.text,
                tweet.created_at.replace(tzinfo=timezone.utc).isoformat(),
                "Twitter/X"
            ))
        return tweets
    except Exception as e:
        logger.exception("Twitter Error")
        return []