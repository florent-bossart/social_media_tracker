import praw
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone

# Load environment variables
load_dotenv()

# Reddit API credentials from .env file
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT")

# Set up Reddit authentication
reddit = praw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_CLIENT_SECRET,
    user_agent=REDDIT_USER_AGENT
)

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

def fetch_reddit_posts_full(subreddit: str):
    """
    Fetch posts and their top-level comments from the past rolling year for a given subreddit.

    :param subreddit: Name of the subreddit
    """
    today = datetime.now(timezone.utc)
    one_year_ago = today - timedelta(days=365)
    start_time = int(one_year_ago.timestamp())
    end_time = int(today.timestamp())

    posts = reddit.subreddit(subreddit).new(limit=1000)
    filtered_posts = []

    for post in posts:
        if start_time <= post.created_utc < end_time:
            # Fetch top-level comments
            post.comments.replace_more(limit=0)  # Fetch all comments
            top_level_comments = [
                {
                    "author": comment.author.name if comment.author else None,
                    "body": comment.body,
                    "created_utc": comment.created_utc
                }
                for comment in post.comments.list()
            ]

            # Add post data along with comments
            filtered_posts.append({
                "title": post.title,
                "author": post.author.name if post.author else None,
                "url": post.url,
                "selftext": post.selftext,  # Content of the post
                "created_utc": post.created_utc,
                "comments": top_level_comments
            })

    # Save data to JSON file
    file_path = os.path.join(DATA_DIR, f"full_{subreddit}_{today.date()}.json")
    with open(file_path, "w", encoding="utf-8") as f:
        import json
        json.dump(filtered_posts, f, ensure_ascii=False, indent=2)

    return filtered_posts
