"""
YouTube search integration for the Get Lucky feature.
Provides functionality to search for artist videos and return formatted results.
"""

import os
import requests
from typing import List, Dict
import streamlit as st

# Get YouTube API key from environment or Streamlit secrets
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

# Try Hugging Face secrets if environment variable is not found
if not YOUTUBE_API_KEY:
    try:
        if hasattr(st, 'secrets') and 'YOUTUBE_API_KEY' in st.secrets:
            YOUTUBE_API_KEY = st.secrets['YOUTUBE_API_KEY']
    except:
        pass

def search_artist_videos(artist_name: str, max_results: int = 5) -> List[Dict]:
    """
    Search for YouTube videos for a specific artist and return top results.
    Uses direct HTTP requests to YouTube API for compatibility with Hugging Face Spaces.

    Args:
        artist_name (str): Name of the artist to search for
        max_results (int): Maximum number of results to return (default: 5)

    Returns:
        List[Dict]: List of video information dictionaries
    """
    if not YOUTUBE_API_KEY or not artist_name or not isinstance(artist_name, str):
        return []

    try:
        # Step 1: Search for videos
        search_url = "https://www.googleapis.com/youtube/v3/search"
        search_params = {
            'part': 'id,snippet',
            'q': artist_name,
            'type': 'video',
            'order': 'relevance',
            'maxResults': max_results,
            'key': YOUTUBE_API_KEY
        }
        
        search_response = requests.get(search_url, params=search_params, timeout=10)
        
        if search_response.status_code != 200:
            return []
        
        search_data = search_response.json()
        items = search_data.get('items', [])
        
        if not items:
            return []
        
        # Extract video IDs
        video_ids = [item['id']['videoId'] for item in items if 'videoId' in item['id']]
        
        if not video_ids:
            return []
        
        # Step 2: Get video details
        details_url = "https://www.googleapis.com/youtube/v3/videos"
        details_params = {
            'part': 'snippet,statistics,contentDetails',
            'id': ','.join(video_ids),
            'key': YOUTUBE_API_KEY
        }
        
        details_response = requests.get(details_url, params=details_params, timeout=10)
        
        if details_response.status_code != 200:
            return []
        
        details_data = details_response.json()
        video_items = details_data.get('items', [])
        
        # Format results
        formatted_results = []
        for video in video_items:
            snippet = video.get('snippet', {})
            stats = video.get('statistics', {})
            content_details = video.get('contentDetails', {})
            
            # Parse duration
            duration_str = content_details.get('duration', 'PT0S')
            duration_seconds = parse_duration(duration_str)
            
            video_info = {
                'video_id': video['id'],
                'title': snippet.get('title', 'Unknown Title'),
                'channel_title': snippet.get('channelTitle', 'Unknown Channel'),
                'description': snippet.get('description', '')[:200] + '...' if len(snippet.get('description', '')) > 200 else snippet.get('description', ''),
                'view_count': int(stats.get('viewCount', 0)),
                'like_count': int(stats.get('likeCount', 0)),
                'duration_seconds': duration_seconds,
                'youtube_url': f"https://www.youtube.com/watch?v={video['id']}",
                'published_at': snippet.get('publishedAt', ''),
                'thumbnail_url': snippet.get('thumbnails', {}).get('medium', {}).get('url', '')
            }
            formatted_results.append(video_info)
        
        return formatted_results
        
    except Exception:
        return []

def parse_duration(duration_str: str) -> int:
    """
    Parse YouTube duration format (PT4M13S) to seconds
    """
    try:
        # Remove PT prefix
        duration_str = duration_str.replace('PT', '')

        total_seconds = 0

        # Parse hours
        if 'H' in duration_str:
            hours_str, duration_str = duration_str.split('H')
            total_seconds += int(hours_str) * 3600

        # Parse minutes
        if 'M' in duration_str:
            minutes_str, duration_str = duration_str.split('M')
            total_seconds += int(minutes_str) * 60

        # Parse seconds
        if 'S' in duration_str:
            seconds_str = duration_str.replace('S', '')
            if seconds_str:
                total_seconds += int(seconds_str)

        return total_seconds
    except:
        return 0

def format_duration(duration_seconds: int) -> str:
    """Convert duration in seconds to readable format (MM:SS or HH:MM:SS)"""
    if duration_seconds < 3600:  # Less than 1 hour
        minutes = duration_seconds // 60
        seconds = duration_seconds % 60
        return f"{minutes}:{seconds:02d}"
    else:  # 1 hour or more
        hours = duration_seconds // 3600
        minutes = (duration_seconds % 3600) // 60
        seconds = duration_seconds % 60
        return f"{hours}:{minutes:02d}:{seconds:02d}"

def format_view_count(view_count: int) -> str:
    """Format view count to readable format (1.2K, 1.2M, etc.)"""
    if view_count >= 1_000_000:
        return f"{view_count / 1_000_000:.1f}M"
    elif view_count >= 1_000:
        return f"{view_count / 1_000:.1f}K"
    else:
        return str(view_count)
