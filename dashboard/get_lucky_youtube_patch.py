"""
Patch for adding YouTube integration to Get Lucky page.
This works around the corrupted data_manager.py file.
"""

import streamlit as st
import os
from typing import List, Dict
from youtube_search import search_artist_videos, format_duration, format_view_count

def add_youtube_section_to_get_lucky(artist_name: str):
    """Add YouTube videos section to the Get Lucky page"""
    
    st.subheader("🎥 YouTube Videos")
    
    # Check if YouTube API is available
    api_key = os.getenv('YOUTUBE_API_KEY')
    if not api_key:
        st.warning("🔑 YouTube API key not configured")
        st.info("""
        To enable YouTube video search:
        1. Set your YouTube API key as an environment variable: `YOUTUBE_API_KEY`
        2. Restart the application
        
        For now, you can search manually:
        """)
        search_url = f"https://www.youtube.com/results?search_query={artist_name.replace(' ', '+')}"
        st.markdown(f"🔍 **[Search for {artist_name} on YouTube]({search_url})**")
        return
    
    with st.spinner(f"🔍 Searching for {artist_name} videos on YouTube..."):
        try:
            videos = search_artist_videos(artist_name, max_results=5)
            
            if videos:
                st.success(f"Found {len(videos)} videos for {artist_name}")
                
                # Display videos in a nice format
                for i, video in enumerate(videos, 1):
                    with st.expander(f"🎵 Video #{i}: {video['title'][:60]}{'...' if len(video['title']) > 60 else ''}", expanded=i<=2):
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.markdown(f"**Title:** {video['title']}")
                            st.markdown(f"**Channel:** {video['channel_title']}")
                            st.markdown(f"**Duration:** {format_duration(video['duration_seconds'])}")
                            
                            # YouTube link
                            st.markdown(f"🎬 **[Watch on YouTube]({video['youtube_url']})**")
                        
                        with col2:
                            st.metric("Views", format_view_count(video['view_count']))
                            st.metric("Likes", format_view_count(video['like_count']))
                    
            else:
                st.info(f"No YouTube videos found for {artist_name}. This could be due to:")
                st.markdown("""
                - YouTube API quota limits
                - No recent videos matching the search criteria
                - Network connectivity issues
                """)
                
                # Provide manual search link
                search_url = f"https://www.youtube.com/results?search_query={artist_name.replace(' ', '+')}"
                st.markdown(f"🔍 **[Search manually on YouTube]({search_url})**")
                
        except Exception as e:
            st.error(f"Error searching YouTube: {e}")
            # Provide fallback manual search
            search_url = f"https://www.youtube.com/results?search_query={artist_name.replace(' ', '+')}"
            st.markdown(f"🔍 **[Search manually on YouTube]({search_url})**")
