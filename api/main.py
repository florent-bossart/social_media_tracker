from fastapi import FastAPI , Query
from .reddit import fetch_reddit_posts
from api.youtube import search_and_fetch_comments
import random


app = FastAPI()

SEARCH_KEYWORDS = [
    "最新曲 日本",
    "新曲 Jpop",
    "Japanese music 2025",
    "Jpop new release",
    "Jpop トレンド",
    "Japanese MV 2025"
]

@app.get("/")
def read_root():
    return {"message": "Welcome to the Social Media Sentiment Tracker API"}

@app.get("/youtube")
def get_youtube_data():
    query = random.choice(SEARCH_KEYWORDS)
    data = search_and_fetch_comments(query)
    return data

@app.get("/reddit/{subreddit}")
def get_reddit_posts(subreddit: str):
    posts = fetch_reddit_posts(subreddit)
    return {"subreddit": subreddit, "posts": posts}
