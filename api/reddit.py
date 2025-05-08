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

DATA_DIR = "data/reddit"
os.makedirs(DATA_DIR, exist_ok=True)

def fetch_reddit_posts_daily(subreddit: str):
    """
    Fetch posts and their top-level comments for a given subreddit from the previous day.

    :param subreddit: Name of the subreddit
    """
    # Calculate the date range for the previous day
    today = datetime.now(timezone.utc)
    yesterday = today - timedelta(days=1)
    start_time = int(yesterday.replace(hour=0, minute=0, second=0, microsecond=0).timestamp())
    end_time = int(today.replace(hour=0, minute=0, second=0, microsecond=0).timestamp())
    date_folder = today.date()  # e.g., 2025-05-08

    posts = reddit.subreddit(subreddit).new(limit=100)
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


    # Create the directory path with the date
    date_directory = os.path.join(DATA_DIR, str(date_folder))
    os.makedirs(date_directory, exist_ok=True)  # Ensure the directory exists

    # Save data to JSON file
    file_path = os.path.join(date_directory, f"daily_{subreddit}_{yesterday.date()}.json")
    with open(file_path, "w", encoding="utf-8") as f:
        import json
        json.dump(filtered_posts, f, ensure_ascii=False, indent=2)

    return filtered_posts
