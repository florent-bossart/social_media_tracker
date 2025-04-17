import praw
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Reddit API credentials from .env file
REDDIT_CLIENT_ID = os.getenv('REDDIT_CLIENT_ID')
REDDIT_CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET')
REDDIT_USER_AGENT = os.getenv('REDDIT_USER_AGENT')

# Set up Reddit authentication
reddit = praw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_CLIENT_SECRET,
    user_agent=REDDIT_USER_AGENT
)

def fetch_reddit_posts(subreddit: str):
    """Fetch recent posts from a given subreddit."""
    posts = reddit.subreddit(subreddit).new(limit=10)
    post_list = [{"title": post.title, "author": post.author.name, "url": post.url} for post in posts]
    return post_list
