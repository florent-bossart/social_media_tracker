from fastapi import FastAPI , Query
from .reddit import fetch_reddit_posts
from api.youtube import get_recent_comments_for_query
from api.youtube import search_and_fetch_comments

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Welcome to the Social Media Sentiment Tracker API"}


@app.get("/reddit/{subreddit}")
def get_reddit_posts(subreddit: str):
    posts = fetch_reddit_posts(subreddit)
    return {"subreddit": subreddit, "posts": posts}

@app.get("/youtube-comments/")
def youtube_comments(query: str):
    return get_recent_comments_for_query(query)


@app.get("/youtube")
def get_youtube_data(query: str = "japanese music"):
    data = search_and_fetch_comments(query)
    return data
