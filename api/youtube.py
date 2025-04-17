from googleapiclient.discovery import build
import os
from dotenv import load_dotenv
from isodate import parse_duration


load_dotenv()

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)


def search_recent_videos(query: str, max_results=3):
    request = youtube.search().list(
        q=query,
        part="snippet",
        type="video",
        order="date",
        maxResults=max_results
    )
    response = request.execute()
    return [item["id"]["videoId"] for item in response.get("items", [])]


def get_comments(video_id: str, max_comments=10):
    comments = []
    request = youtube.commentThreads().list(
        part="snippet",
        videoId=video_id,
        maxResults=max_comments,
        textFormat="plainText"
    )
    response = request.execute()

    for item in response.get("items", []):
        top_comment = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
        comments.append(top_comment)

    return comments


def get_recent_comments_for_query(query: str, video_count=3, comment_count=5):
    video_ids = search_recent_videos(query, max_results=video_count)
    all_comments = {}

    for vid in video_ids:
        comments = get_comments(vid, max_comments=comment_count)
        all_comments[vid] = comments

    return all_comments


def search_youtube_videos(youtube, query, page_token=None):
    response = youtube.search().list(
        q=query,
        part="id",
        type="video",
        maxResults=50,
        pageToken=page_token,
        regionCode="JP",
        videoDuration="medium",  # < 20 minutes
        relevanceLanguage="ja"
    ).execute()
    video_ids = [item["id"]["videoId"] for item in response.get("items", [])]
    return video_ids, response.get("nextPageToken")


def fetch_video_details(youtube, video_ids):
    response = youtube.videos().list(
        part="snippet,statistics,contentDetails",
        id=",".join(video_ids)
    ).execute()
    return response.get("items", [])


def is_valid_music_video(video, min_views=10000, max_duration_sec=420):
    snippet = video.get("snippet", {})
    stats = video.get("statistics", {})
    content = video.get("contentDetails", {})

    try:
        duration = parse_duration(content["duration"]).total_seconds()
    except Exception:
        return False

    if (
        snippet.get("categoryId") != "10"
        or int(stats.get("viewCount", 0)) < min_views
        or duration > max_duration_sec
    ):
        return False
    return True


def fetch_all_comments(youtube, video_id):
    comments = []
    page_token = None

    while True:
        try:
            response = youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                textFormat="plainText",
                maxResults=100,
                pageToken=page_token
            ).execute()

            for item in response.get("items", []):
                snippet = item["snippet"]["topLevelComment"]["snippet"]
                comments.append({
                    "author": snippet.get("authorDisplayName"),
                    "text": snippet.get("textDisplay"),
                    "published_at": snippet.get("publishedAt"),
                    "like_count": snippet.get("likeCount", 0)
                })

            page_token = response.get("nextPageToken")
            if not page_token:
                break

        except Exception as e:
            print(f"Error fetching comments for {video_id}: {e}")
            break

    return comments


def search_and_fetch_comments(query, max_results=100):
    api_key = os.getenv("YOUTUBE_API_KEY")
    youtube = build("youtube", "v3", developerKey=api_key)

    collected = []
    next_page_token = None
    attempts = 0

    while len(collected) < max_results and attempts < 20:
        video_ids, next_page_token = search_youtube_videos(youtube, query, next_page_token)
        video_items = fetch_video_details(youtube, video_ids)

        for video in video_items:
            if not is_valid_music_video(video):
                continue

            snippet = video["snippet"]
            stats = video["statistics"]
            details = video["contentDetails"]
            duration = parse_duration(details["duration"]).total_seconds()

            video_data = {
                "video_id": video["id"],
                "title": snippet.get("title"),
                "channel_title": snippet.get("channelTitle"),
                "published_at": snippet.get("publishedAt"),
                "view_count": int(stats.get("viewCount", 0)),
                "like_count": int(stats.get("likeCount", 0)),
                "comment_count": int(stats.get("commentCount", 0)),
                "duration_seconds": duration,
                "comments": fetch_all_comments(youtube, video["id"])
            }

            collected.append(video_data)
            if len(collected) >= max_results:
                break

        if not next_page_token:
            break
        attempts += 1

    return collected
