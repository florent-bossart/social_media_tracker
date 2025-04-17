from googleapiclient.discovery import build
import os
from dotenv import load_dotenv

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


def search_and_fetch_comments(query, max_results=100):
    api_key = os.getenv("YOUTUBE_API_KEY")  # Set this in your .env or environment
    youtube = build("youtube", "v3", developerKey=api_key)

    collected_videos = []
    next_page_token = None
    total_collected = 0
    attempts = 0

    while total_collected < max_results and attempts < 10:
        search_response = youtube.search().list(
            q=query,
            part="id",
            type="video",
            maxResults=50,
            pageToken=next_page_token
        ).execute()

        video_ids = [item["id"]["videoId"] for item in search_response.get("items", [])]
        if not video_ids:
            break

        video_response = youtube.videos().list(
            part="snippet,statistics",
            id=",".join(video_ids)
        ).execute()

        for video in video_response.get("items", []):
            stats = video.get("statistics", {})
            snippet = video.get("snippet", {})

            view_count = int(stats.get("viewCount", 0))
            if view_count < 10000:
                continue  # skip low-visibility videos

            video_data = {
                "video_id": video["id"],
                "title": snippet.get("title"),
                "channel_title": snippet.get("channelTitle"),
                "published_at": snippet.get("publishedAt"),
                "view_count": view_count,
                "like_count": int(stats.get("likeCount", 0)),
                "comment_count": int(stats.get("commentCount", 0)),
                "comments": []
            }

            # Fetch top-level comments
            try:
                comment_response = youtube.commentThreads().list(
                    part="snippet",
                    videoId=video["id"],
                    textFormat="plainText",
                    maxResults=20
                ).execute()

                for item in comment_response.get("items", []):
                    comment_snippet = item["snippet"]["topLevelComment"]["snippet"]
                    video_data["comments"].append({
                        "author": comment_snippet.get("authorDisplayName"),
                        "text": comment_snippet.get("textDisplay"),
                        "published_at": comment_snippet.get("publishedAt"),
                        "like_count": comment_snippet.get("likeCount", 0)
                    })
            except Exception as e:
                print(f"Failed to fetch comments for video {video['id']}: {e}")

            collected_videos.append(video_data)
            total_collected += 1

            if total_collected >= max_results:
                break

        next_page_token = search_response.get("nextPageToken")
        if not next_page_token:
            break  # no more pages
        attempts += 1

    return collected_videos
