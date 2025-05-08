import os
import time
import json
import random
from datetime import datetime, timezone, timedelta

from pathlib import Path
from typing import List, Tuple

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from .youtube_quota import quota
from .track_fetched_data import (
    add_fetched_video,
    add_fetched_comment_ids,
    get_fetched_videos,
    get_fetched_comment_ids
)


YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

DATA_DIR = Path("/app/data/youtube")
DATA_DIR.mkdir(parents=True, exist_ok=True)

LOGS_DIR = Path("../logs")  # Directory for request logs
LOGS_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOGS_DIR / f"{datetime.now().date()}_requests.txt"


# Function to log the number of requests made
def log_requests(count: int):
    if LOG_FILE.exists():
        with open(LOG_FILE, "r") as f:
            try:
                current_count = int(f.read().strip())
            except ValueError:
                current_count = 0
    else:
        current_count = 0

    new_count = current_count + count
    with open(LOG_FILE, "w") as f:
        f.write(str(new_count))


# Function to randomize sleep intervals
def random_sleep():
    sleep_time = random.uniform(0.5, 1.5)
    time.sleep(sleep_time)


# Function to search for YouTube videos based on a query
# and return a list of video IDs.
def search_youtube_videos(query: str, max_results: int = 10) -> List[str]:
    if not quota.can_use(100):
        raise RuntimeError("Not enough quota left for YouTube search")
    if not query:
        raise ValueError("Query cannot be empty")
    if not isinstance(query, str):
        raise ValueError("Query must be a string")
    if not isinstance(max_results, int) or max_results <= 0:
        raise ValueError("max_results must be a positive integer")
    if max_results > 50:
        raise ValueError("max_results cannot exceed 50")

    # Random sleep to avoid hitting the quota limit too quickly
    random_sleep()

    # Optimize and use quota
    max_cost_per_request = 100
    suggested_cost = quota.optimize_usage(max_cost_per_request)
    if quota.can_use(suggested_cost):
        quota.use(suggested_cost)
        log_requests(suggested_cost)
    else:
        raise RuntimeError("Quota exceeded or not enough quota left for this request.")

    now = datetime.now(timezone.utc)
    one_month_ago = now - timedelta(days=30)
    # Perform the search using the YouTube Data API
    request = youtube.search().list(
        order="date",
        publishedAfter=one_month_ago.strftime("%Y-%m-%dT%H:%M:%SZ"),
        publishedBefore= now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        q=query,
        part="id",
        type="video",
        maxResults=max_results,
        regionCode="JP",
        videoDuration="medium",
        relevanceLanguage="ja"
    )
    response = request.execute()
    video_ids = [item["id"]["videoId"] for item in response.get("items", [])]
    return video_ids


# Function to fetch video details for a list of video IDs
# and return a list of dictionaries containing the details.
def fetch_video_details(video_ids: List[str], query: str, fetch_date: str) -> List[dict]:
    max_cost_per_request = len(video_ids)
    suggested_cost = quota.optimize_usage(max_cost_per_request)
    if not quota.can_use(suggested_cost):
        raise RuntimeError("Not enough quota left for video detail fetch")

    quota.use(suggested_cost)
    log_requests(suggested_cost)
    request = youtube.videos().list(
        part="snippet,statistics,contentDetails",
        id=','.join(video_ids)
    )
    response = request.execute()

    video_data = []
    for video in response.get("items", []):
        snippet = video.get("snippet", {})
        stats = video.get("statistics", {})
        content_details = video.get("contentDetails", {})
        duration = parse_duration_to_seconds(content_details.get("duration", "PT0S"))

        video_data.append({
            "video_id": video["id"],
            "title": snippet.get("title"),
            "channel_title": snippet.get("channelTitle"),
            "published_at": snippet.get("publishedAt"),
            "view_count": int(stats.get("viewCount", 0)),
            "like_count": int(stats.get("likeCount", 0)),
            "comment_count": int(stats.get("commentCount", 0)),
            "duration_seconds": duration,
            "keyword": query,
            "fetch_date": fetch_date
        })
    return video_data


# Function to fetch comments for a given video ID
# and return a list of dictionaries containing the comments.
def fetch_video_comments(video_id: str) -> List[dict]:
    max_cost_per_request = 1  # Each comment request costs 1
    suggested_cost = quota.optimize_usage(max_cost_per_request)
    if not quota.can_use(suggested_cost):
        raise RuntimeError("Not enough quota left for comments fetch")

    quota.use(suggested_cost)
    log_requests(suggested_cost)
    try:
        request = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=100,
            order="time"
        )
        response = request.execute()

        # Extract comment IDs and full comment details
        comment_details = [
            {
                "id": item["snippet"]["topLevelComment"]["id"],
                "text": item["snippet"]["topLevelComment"]["snippet"]["textDisplay"],
                "author": item["snippet"]["topLevelComment"]["snippet"].get("authorDisplayName"),
                "published_at": item["snippet"]["topLevelComment"]["snippet"]["publishedAt"]
            }
            for item in response.get("items", [])
        ]
        comment_ids = [comment["id"] for comment in comment_details]

        # Track only comment IDs
        existing_comment_ids = get_fetched_comment_ids(video_id)
        new_comment_ids = [cid for cid in comment_ids if cid not in existing_comment_ids]
        add_fetched_comment_ids(video_id, new_comment_ids)

        # Return full details for processing (e.g., saving snapshots)
        return [comment for comment in comment_details if comment["id"] in new_comment_ids]
    except HttpError as e:
        print(f"Failed to fetch comments for video {video_id}: {e}")
        return []


# Function to search for YouTube videos based on a query,
# fetch their details, and retrieve comments.
def search_and_fetch_video_data(query: str):
    fetch_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    video_ids = search_youtube_videos(query)

    # Filter out already fetched videos
    video_ids = [id for id in video_ids if id not in get_fetched_videos()]

    video_data = fetch_video_details(video_ids, query, fetch_date)
    all_comments = []

    for video in video_data:
        video_id = video["video_id"]
        comments = fetch_video_comments(video_id)
        comment_ids = [comment["id"] for comment in comments]  # Extract comment IDs
        add_fetched_video(video_id)  # Add to fetched videos
        add_fetched_comment_ids(video_id, comment_ids)  # Add fetched comment IDs
        all_comments.extend([{"video_id": video_id, **comment} for comment in comments])

    return video_data, all_comments


# Function to save video data and comments to JSON files.
# The function creates a directory for the fetch date
def save_video_snapshot(video_data: List[dict], query: str, fetch_date: str):
    sanitized_query = query.replace(" ", "_").replace("/", "-")
    snapshot_dir = DATA_DIR / fetch_date
    snapshot_dir.mkdir(parents=True, exist_ok=True)

    videos_path = snapshot_dir / f"videos_{sanitized_query}.json"
    with open(videos_path, "w", encoding="utf-8") as f:
        json.dump(video_data, f, ensure_ascii=False, indent=2)


# Function to save comments data to JSON files.
# The function creates a directory for the fetch date
def save_comments_snapshot(comments: List[dict], query: str, fetch_date: str):
    sanitized_query = query.replace(" ", "_").replace("/", "-")
    snapshot_dir = DATA_DIR / fetch_date
    snapshot_dir.mkdir(parents=True, exist_ok=True)

    comments_path = snapshot_dir / f"comments_{sanitized_query}.json"
    with open(comments_path, "w", encoding="utf-8") as f:
        json.dump(comments, f, ensure_ascii=False, indent=2)


# Function to parse ISO 8601 duration strings
# and convert them to seconds.
def parse_duration_to_seconds(duration_str: str) -> int:
    import isodate
    try:
        duration = isodate.parse_duration(duration_str)
        return int(duration.total_seconds())
    except Exception:
        return 0
