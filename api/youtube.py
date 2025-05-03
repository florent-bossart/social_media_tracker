import os
import json
import random
from datetime import datetime
from pathlib import Path
from typing import List, Tuple

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from .youtube_quota import quota

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

DATA_DIR = Path("/app/data")
DATA_DIR.mkdir(parents=True, exist_ok=True)

def search_youtube_videos(query: str, max_results: int = 10) -> List[str]:
    if not quota.can_use(100):
        raise RuntimeError("Not enough quota left for YouTube search")

    quota.use(100)
    request = youtube.search().list(
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

def fetch_video_details(video_ids: List[str], query: str, fetch_date: str) -> List[dict]:
    if not quota.can_use(len(video_ids)):
        raise RuntimeError("Not enough quota left for video detail fetch")

    quota.use(len(video_ids))
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

def fetch_video_comments(video_id: str) -> List[dict]:
    if not quota.can_use(1):
        raise RuntimeError("Not enough quota left for comments fetch")

    quota.use(1)
    try:
        request = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=100,
            order="time"
        )
        response = request.execute()
        comments = [
            {
                "text": item["snippet"]["topLevelComment"]["snippet"]["textDisplay"],
                "author": item["snippet"]["topLevelComment"]["snippet"].get("authorDisplayName"),
                "published_at": item["snippet"]["topLevelComment"]["snippet"]["publishedAt"]
            }
            for item in response.get("items", [])
        ]
        return comments
    except HttpError as e:
        print(f"Failed to fetch comments for video {video_id}: {e}")
        return []

def search_and_fetch_video_data(query: str) -> Tuple[List[dict], List[dict]]:
    fetch_date = datetime.utcnow().strftime("%Y-%m-%d")
    video_ids = search_youtube_videos(query)
    video_data = fetch_video_details(video_ids, query, fetch_date)

    all_comments = []
    for video in video_data:
        video_id = video["video_id"]
        comments = fetch_video_comments(video_id)
        for comment in comments:
            comment["video_id"] = video_id
        all_comments.extend(comments)

    return video_data, all_comments

def save_video_snapshot(video_data: List[dict], query: str, fetch_date: str):
    sanitized_query = query.replace(" ", "_").replace("/", "-")
    snapshot_dir = DATA_DIR / fetch_date
    snapshot_dir.mkdir(parents=True, exist_ok=True)

    videos_path = snapshot_dir / f"videos_{sanitized_query}.json"
    with open(videos_path, "w", encoding="utf-8") as f:
        json.dump(video_data, f, ensure_ascii=False, indent=2)

def save_comments_snapshot(comments: List[dict], query: str, fetch_date: str):
    sanitized_query = query.replace(" ", "_").replace("/", "-")
    snapshot_dir = DATA_DIR / fetch_date
    snapshot_dir.mkdir(parents=True, exist_ok=True)

    comments_path = snapshot_dir / f"comments_{sanitized_query}.json"
    with open(comments_path, "w", encoding="utf-8") as f:
        json.dump(comments, f, ensure_ascii=False, indent=2)

def parse_duration_to_seconds(duration_str: str) -> int:
    import isodate
    try:
        duration = isodate.parse_duration(duration_str)
        return int(duration.total_seconds())
    except Exception:
        return 0
