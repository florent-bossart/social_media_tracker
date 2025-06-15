"""
YouTube search integration for the Get Lucky feature.
Provides functionality to search for artist videos and return formatted results.
"""

import os
import sys
from typing import List, Dict, Optional
from datetime import datetime

# Add the API directory to the path to import YouTube functions
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'api'))

try:
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    YOUTUBE_AVAILABLE = True
except ImportError:
    YOUTUBE_AVAILABLE = False
    HttpError = Exception  # Fallback for error handling
    print("Warning: YouTube API not available. Install required dependencies.")

# Global variables
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
youtube = None

if YOUTUBE_AVAILABLE and YOUTUBE_API_KEY:
    try:
        youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
        print(f"YouTube API client initialized successfully")
    except Exception as e:
        print(f"Failed to initialize YouTube API client: {e}")
        YOUTUBE_AVAILABLE = False
else:
    YOUTUBE_AVAILABLE = False
    if not YOUTUBE_API_KEY:
        print("Warning: YouTube API key not found in environment variables.")

def search_artist_videos(artist_name: str, max_results: int = 5) -> List[Dict]:
    """
    Search for YouTube videos for a specific artist and return top results.
    
    Args:
        artist_name (str): Name of the artist to search for
        max_results (int): Maximum number of results to return (default: 5)
    
    Returns:
        List[Dict]: List of video information dictionaries
    """
    if not YOUTUBE_AVAILABLE or not YOUTUBE_API_KEY or not youtube:
        return []
    
    if not artist_name or not isinstance(artist_name, str):
        return []
    
    try:
        # Try a simple, direct search
        request = youtube.search().list(
            part="id,snippet",
            q=artist_name,  # Simple query with just artist name
            type="video",
            order="relevance",  # Order by relevance for best results
            maxResults=max_results
        )
        response = request.execute()
        
        video_ids = []
        for item in response.get("items", []):
            video_id = item["id"]["videoId"]
            video_ids.append(video_id)
        
        if not video_ids:
            return []
        
        # Get detailed video information
        request = youtube.videos().list(
            part="snippet,statistics,contentDetails",
            id=','.join(video_ids[:max_results])
        )
        response = request.execute()
        
        # Format results for the dashboard
        formatted_results = []
        for video in response.get("items", []):
            snippet = video.get("snippet", {})
            stats = video.get("statistics", {})
            content_details = video.get("contentDetails", {})
            
            # Parse duration
            duration_str = content_details.get("duration", "PT0S")
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
        
    except HttpError as e:
        print(f"YouTube API HttpError: {e}")
        return []
    except Exception as e:
        print(f"YouTube search error: {e}")
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
