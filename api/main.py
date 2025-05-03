from fastapi import FastAPI
from fastapi.responses import JSONResponse

from api.youtube import search_and_fetch_video_data, save_video_snapshot
from api.youtube_quota import quota
from .reddit import fetch_reddit_posts

import random
import datetime


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
    try:
        video_data, comments = search_and_fetch_video_data(query)
        fetch_date = datetime.utcnow().date().isoformat()
        save_video_snapshot(video_data, query, fetch_date)
    except RuntimeError as e:
        raise HTTPException(status_code=429, detail=str(e))

    return {
        "query": query,
        "fetched_at": fetch_date,
        "videos_fetched": len(video_data),
        "quota_used": quota.used,
        "quota_remaining": quota.remaining()
    }



@app.get("/reddit/{subreddit}")
def get_reddit_posts(subreddit: str):
    try:
        posts = fetch_reddit_posts(subreddit)
        return {"subreddit": subreddit, "posts": posts}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
