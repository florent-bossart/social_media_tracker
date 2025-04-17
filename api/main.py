from fastapi import FastAPI , Query
from .reddit import fetch_reddit_posts
from api.youtube import search_youtube

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Welcome to the Social Media Sentiment Tracker API"}


@app.get("/reddit/{subreddit}")
def get_reddit_posts(subreddit: str):
    posts = fetch_reddit_posts(subreddit)
    return {"subreddit": subreddit, "posts": posts}

@app.get("/youtube/search")
def youtube_search(q: str = Query(..., description="Search query for YouTube")):
    results = search_youtube(q)
    return results
