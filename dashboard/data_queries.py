"""
Data queries module for the Japanese Music Trends Dashboard.
Contains all DBT model query functions using pre-built DBT views.
"""

import streamlit as st
import pandas as pd
from urllib.parse import unquote
from database_service import fetch_data

# =============================================================================
# DBT MODEL BASED FUNCTIONS - Simplified queries using pre-built DBT views
# =============================================================================

@st.cache_data
def get_artist_trends():
    """Fetch artist trends from DBT view - replaces complex CTE logic"""
    query = """
    SELECT * FROM analytics.artist_trends_dashboard
    LIMIT 100
    """
    result = fetch_data(query)
    return decode_artist_names(result)

@st.cache_data
def get_genre_trends():
    """Fetch genre trends from DBT view - replaces complex CTE logic"""
    query = """
    SELECT * FROM analytics.genre_trends_dashboard
    LIMIT 25
    """
    return fetch_data(query)

@st.cache_data
def get_platform_data():
    """Fetch platform comparison data from DBT view"""
    query = """
    SELECT * FROM analytics.platform_data_dashboard
    """
    return fetch_data(query)

@st.cache_data(ttl=300)  # Cache for 5 minutes only
def get_temporal_data():
    """Fetch temporal trends data from DBT view"""
    query = """
    SELECT * FROM analytics.temporal_data_dashboard
    """
    return fetch_data(query)

@st.cache_data
def get_wordcloud_data():
    """Fetch word cloud data from DBT view"""
    query = """
    SELECT * FROM analytics.wordcloud_data_dashboard
    """
    return fetch_data(query)

@st.cache_data
def get_overall_stats():
    """Get overall dashboard statistics from DBT view"""
    query = """
    SELECT * FROM analytics.overall_stats_dashboard
    """
    return fetch_data(query)

@st.cache_data
def get_trend_summary_data():
    """Fetch trend summary data from DBT view - simplified from multiple complex queries"""
    try:
        # Use the trend summary artists DBT view
        artists_query = """
        SELECT * FROM analytics.trend_summary_artists_dashboard
        ORDER BY trend_strength DESC, mentions DESC
        LIMIT 50
        """
        artists_data = fetch_data(artists_query)

        # Apply URL decoding to artist names
        artists_data = decode_artist_names(artists_data)

        # Get overview data from flattened tables (keeping original as it's already optimized)
        overview_query = """
        SELECT * FROM analytics.trend_summary_overview
        ORDER BY analysis_timestamp DESC
        LIMIT 1
        """
        overview_data = fetch_data(overview_query)

        # Get top genres data from normalized view
        genres_query = """
        SELECT * FROM analytics.trend_summary_top_genres_normalized
        WHERE analysis_timestamp = (
            SELECT MAX(analysis_timestamp) FROM analytics.trend_summary_top_genres_normalized
        )
        ORDER BY popularity_score DESC
        LIMIT 15
        """
        genres_data = fetch_data(genres_query)

        # Get sentiment patterns
        sentiment_query = """
        SELECT * FROM analytics.trend_summary_sentiment_patterns
        ORDER BY analysis_timestamp DESC
        LIMIT 1
        """
        sentiment_data = fetch_data(sentiment_query)

        # Get engagement levels
        engagement_query = """
        SELECT * FROM analytics.trend_summary_engagement_levels
        ORDER BY analysis_timestamp DESC
        LIMIT 1
        """
        engagement_data = fetch_data(engagement_query)

        return {
            'overview': overview_data,
            'artists': artists_data,
            'genres': genres_data,
            'sentiment': sentiment_data,
            'engagement': engagement_data
        }
    except Exception as e:
        st.error(f"Error fetching trend summary data: {e}")
        return None

@st.cache_data
def get_insights_summary_data():
    """Fetch insights summary data from flattened tables (keeping original as already optimized)"""
    try:
        # Get overview data
        overview_query = """
        SELECT * FROM analytics.insights_summary_overview
        ORDER BY analysis_timestamp DESC
        LIMIT 1
        """
        overview_data = fetch_data(overview_query)

        # Get key findings
        findings_query = """
        SELECT * FROM analytics.insights_summary_key_findings
        WHERE analysis_timestamp = (
            SELECT MAX(analysis_timestamp) FROM analytics.insights_summary_key_findings
        )
        ORDER BY finding_order
        """
        findings_data = fetch_data(findings_query)

        # Get artist insights
        artist_insights_query = """
        SELECT * FROM analytics.insights_summary_artist_insights
        WHERE analysis_timestamp = (
            SELECT MAX(analysis_timestamp) FROM analytics.insights_summary_artist_insights
        )
        ORDER BY artist_name
        """
        artist_insights_data = fetch_data(artist_insights_query)

        # Apply URL decoding to artist names
        artist_insights_data = decode_artist_names(artist_insights_data)

        return {
            'overview': overview_data,
            'findings': findings_data,
            'artist_insights': artist_insights_data
        }
    except Exception as e:
        st.error(f"Error fetching insights summary data: {e}")
        return None

@st.cache_data
def get_genre_artist_diversity():
    """Fetch genre artist diversity data from DBT view"""
    query = """
    SELECT * FROM analytics.genre_artist_diversity_dashboard
    """
    return fetch_data(query)

@st.cache_data
def get_artists_without_genre_count():
    """Count artists without genre assignment from DBT view"""
    query = """
    SELECT artists_without_genre FROM analytics.artists_without_genre_dashboard
    """
    result = fetch_data(query)
    return result['artists_without_genre'].iloc[0] if not result.empty else 0

@st.cache_data
def get_artist_sentiment_data():
    """Fetch artist sentiment data from DBT view - replaces complex CTE in dashboard"""
    query = """
    SELECT * FROM analytics.artist_sentiment_dashboard
    ORDER BY mention_count DESC
    """
    result = fetch_data(query)
    return decode_artist_names(result)

# =============================================================================
# ENRICHED DASHBOARD FUNCTIONS - New views with intermediate schema joins
# =============================================================================

@st.cache_data
def get_artist_trends_enriched():
    """Fetch enriched artist trends with source context from intermediate schema"""
    query = """
    SELECT * FROM analytics.artist_trends_enriched_dashboard
    ORDER BY total_mentions DESC
    LIMIT 100
    """
    try:
        result = fetch_data(query)
        return decode_artist_names(result)
    except Exception as e:
        st.warning(f"Enriched artist trends not available yet: {e}")
        return pd.DataFrame()

@st.cache_data  
def get_url_analysis_data():
    """Fetch URL analysis data showing which URLs are associated with artist mentions"""
    query = """
    SELECT * FROM analytics.url_analysis_dashboard
    ORDER BY mention_count DESC
    LIMIT 50
    """
    try:
        result = fetch_data(query)
        return decode_artist_names(result)
    except Exception as e:
        st.warning(f"URL analysis data not available yet: {e}")
        return pd.DataFrame()

@st.cache_data
def get_video_context_data():
    """Fetch video context data showing YouTube videos with high artist mentions"""
    query = """
    SELECT * FROM analytics.video_context_dashboard
    ORDER BY total_artist_mentions DESC
    LIMIT 30
    """
    try:
        result = fetch_data(query)
        return result
    except Exception as e:
        st.warning(f"Video context data not available yet: {e}")
        return pd.DataFrame()

@st.cache_data
def get_author_influence_data():
    """Fetch author influence data showing most influential users"""
    query = """
    SELECT * FROM analytics.author_influence_dashboard
    ORDER BY total_mentions DESC
    LIMIT 50
    """
    try:
        result = fetch_data(query)
        return decode_artist_names(result)
    except Exception as e:
        st.warning(f"Author influence data not available yet: {e}")
        return pd.DataFrame()

def decode_artist_names(df):
    """Apply URL decoding to artist names in a DataFrame"""
    if not df.empty and 'artist_name' in df.columns:
        df['artist_name'] = df['artist_name'].apply(
            lambda x: unquote(x) if isinstance(x, str) else x
        )
    return df

def decode_genre_names(df):
    """Apply URL decoding to genre names in a DataFrame"""
    if not df.empty and 'genre_name' in df.columns:
        df['genre_name'] = df['genre_name'].apply(
            lambda x: unquote(x) if isinstance(x, str) else x
        )
    return df

def decode_text_fields(df, text_columns):
    """Apply URL decoding to specified text columns in a DataFrame"""
    if not df.empty:
        for column in text_columns:
            if column in df.columns:
                df[column] = df[column].apply(
                    lambda x: unquote(x) if isinstance(x, str) else x
                )
    return df
