from http.client import HTTPException
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from .youtube import search_and_fetch_video_data, save_video_snapshot, save_comments_snapshot
from .youtube_quota import quota
from .reddit import fetch_reddit_posts_daily
from .reddit_init import fetch_reddit_posts_full
from .updates_youtube_comments_from_fetched import update_comments_from_fetched_rotating
from .config import SUBREDDIT_KEYWORDS, SEARCH_KEYWORDS

import random
from datetime import datetime, timezone

app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "Welcome to the Social Media Sentiment Tracker API"}


@app.get("/youtube")
def get_youtube_data():
    fetch_date = datetime.now(timezone.utc).date().isoformat()
    all_results = []

    for query in SEARCH_KEYWORDS:
        try:
            video_data, comments = search_and_fetch_video_data(query)
            save_video_snapshot(video_data, query, fetch_date)
            save_comments_snapshot(comments, query, fetch_date)  # Ensures comments are saved
            all_results.append({
                "query": query,
                "videos_fetched": len(video_data),
                "comments_fetched": len(comments),
                "quota_used": quota.used,
                "quota_remaining": quota.remaining()
            })
        except RuntimeError as e:
            all_results.append({"query": query, "error": str(e)})
            continue  # Continue to the next keyword if quota is insufficient

    return {
        "fetched_at": fetch_date,
        "results": all_results
    }

# Reddit API Route for Daily Fetch
@app.get("/reddit/daily")
def get_reddit_daily_data():
    fetch_date = datetime.now(timezone.utc).date().isoformat()
    all_results = []

    for subreddit in SUBREDDIT_KEYWORDS:
        try:
            posts = fetch_reddit_posts_daily(subreddit)
            all_results.append({
                "subreddit": subreddit,
                "posts_fetched": len(posts),
                "fetched_at": fetch_date
            })
        except Exception as e:
            all_results.append({"subreddit": subreddit, "error": str(e)})

    return {
        "fetched_at": fetch_date,
        "results": all_results
    }


# Reddit API Route for Initial Full Load
@app.get("/reddit/full")
def get_reddit_full_data():
    fetch_date = datetime.now(timezone.utc).date().isoformat()
    all_results = []

    for subreddit in SUBREDDIT_KEYWORDS:
        try:
            posts = fetch_reddit_posts_full(subreddit)
            all_results.append({
                "subreddit": subreddit,
                "posts_fetched": len(posts),
                "fetched_at": fetch_date
            })
        except Exception as e:
            all_results.append({"subreddit": subreddit, "error": str(e)})

    return {
        "fetched_at": fetch_date,
        "results": all_results
    }


@app.post("/update_youtube_comments_from_fetched_rotating")
def trigger_update_youtube_comments_from_fetched_rotating():
    return update_comments_from_fetched_rotating()
