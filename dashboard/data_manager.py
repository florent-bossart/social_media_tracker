"""
Unified Data Manager for Japanese Music Trends Dashboard.
Centralizes all data fetching, caching, and transformation logic.
"""

import streamlit as st
import pandas as pd
from urllib.parse import unquote
from database_service import fetch_data
from typing import Dict, Optional, Any, List

class DataManager:
    """Centralized data management with consistent caching and transformations"""

    # Static cache TTL for semi-static data (1 hour)
    STATIC_TTL = 3600
    # Standard cache TTL for dynamic data (5 minutes) - not used directly
    DYNAMIC_TTL = 300

    @staticmethod
    def decode_url_field(text: str) -> str:
        """Decode URL-encoded text safely"""
        if pd.isna(text) or not isinstance(text, str):
            return text
        try:
            return unquote(text, errors='ignore')
        except Exception:
            return text

    @staticmethod
    def decode_artist_names(df: pd.DataFrame) -> pd.DataFrame:
        """Decode artist names in DataFrame"""
        if df.empty:
            return df

        df = df.copy()
        artist_columns = ['artist_name', 'artist', 'artists', 'entity_name']

        for col in artist_columns:
            if col in df.columns:
                df[col] = df[col].apply(DataManager.decode_url_field)

        return df

    @staticmethod
    def decode_genre_names(df: pd.DataFrame) -> pd.DataFrame:
        """Decode genre names in DataFrame"""
        if df.empty:
            return df

        df = df.copy()
        genre_columns = ['genre_name', 'genre', 'genres']

        for col in genre_columns:
            if col in df.columns:
                df[col] = df[col].apply(DataManager.decode_url_field)

        return df

    @staticmethod
    def decode_text_fields(df: pd.DataFrame, columns: list) -> pd.DataFrame:
        """Decode specified text columns in DataFrame"""
        if df.empty:
            return df

        df = df.copy()
        for col in columns:
            if col in df.columns:
                df[col] = df[col].apply(DataManager.decode_url_field)

        return df

    @staticmethod
    def safe_convert_numeric(value, default=0):
        """Safely convert value to numeric, handling 'None' strings and NaN values."""
        if pd.isna(value) or value is None:
            return default
        if isinstance(value, str):
            if value.lower() == 'none' or value.strip() == '':
                return default
            try:
                return int(float(value))  # Convert via float first to handle decimal strings
            except (ValueError, TypeError):
                return default
        try:
            return int(value)
        except (ValueError, TypeError):
            return default

    # === CORE DATA FETCHING METHODS ===

    @staticmethod
    @st.cache_data
    def get_artist_trends() -> pd.DataFrame:
        """Fetch artist trends from DBT view (Babymetal adjustment already applied in DBT)"""
        query = """
        SELECT
            artist_name,
            mention_count,
            sentiment_score,
            trend_strength,
            trend_direction,
            engagement_level,
            platform_count
        FROM analytics.artist_trends_dashboard
        WHERE artist_name IS NOT NULL AND artist_name != ''
        ORDER BY mention_count DESC
        LIMIT 100
        """
        result = fetch_data(query)
        return DataManager.decode_artist_names(result)

    @staticmethod
    @st.cache_data
    def get_genre_trends() -> pd.DataFrame:
        """Fetch genre trends from DBT view"""
        query = "SELECT * FROM analytics.genre_trends_dashboard LIMIT 25"
        return fetch_data(query)

    @staticmethod
    @st.cache_data
    def get_genre_artists(genre_name: str = None) -> pd.DataFrame:
        """Fetch artists by genre from the genre_artists_dashboard view"""
        if genre_name:
            query = """
            SELECT
                genre_name,
                artist_name,
                mention_count,
                avg_confidence,
                sentiment_score,
                platform_count,
                artist_rank
            FROM analytics.genre_artists_dashboard
            WHERE genre_name = %s
            ORDER BY mention_count DESC
            LIMIT 50
            """
            result = fetch_data(query, params=(genre_name,))
        else:
            query = """
            SELECT
                genre_name,
                artist_name,
                mention_count,
                avg_confidence,
                sentiment_score,
                platform_count,
                artist_rank
            FROM analytics.genre_artists_dashboard
            ORDER BY genre_name, mention_count DESC
            LIMIT 500
            """
            result = fetch_data(query)

        return DataManager.decode_artist_names(result)

    @staticmethod
    @st.cache_data
    def get_platform_data() -> pd.DataFrame:
        """Fetch platform comparison data"""
        query = "SELECT * FROM analytics.platform_data_dashboard"
        return fetch_data(query)

    @staticmethod
    @st.cache_data(ttl=300)
    def get_temporal_data() -> pd.DataFrame:
        """Fetch temporal trends data"""
        query = "SELECT * FROM analytics.temporal_data_dashboard"
        return fetch_data(query)

    @staticmethod
    @st.cache_data
    def get_wordcloud_data() -> pd.DataFrame:
        """Fetch word cloud data"""
        query = "SELECT * FROM analytics.wordcloud_data_dashboard"
        return fetch_data(query)

    @staticmethod
    @st.cache_data(ttl=300)
    def get_overall_stats() -> Dict[str, Any]:
        """Get overall dashboard statistics"""
        query = "SELECT * FROM analytics.overall_stats_dashboard"
        result = fetch_data(query)
        return result.iloc[0].to_dict() if not result.empty else {}

    # === AI & INSIGHTS DATA ===

    @staticmethod
    @st.cache_data(ttl=300)
    def get_trend_summary_data() -> Dict[str, pd.DataFrame]:
        """Fetch AI trend summary data"""
        try:
            # Artists data
            artists_query = """
            SELECT * FROM analytics.trend_summary_artists_dashboard
            ORDER BY trend_strength DESC, mentions DESC
            LIMIT 50
            """
            artists_data = fetch_data(artists_query)
            artists_data = DataManager.decode_artist_names(artists_data)

            # Overview data
            overview_query = """
            SELECT * FROM analytics.trend_summary_overview
            ORDER BY analysis_timestamp DESC
            LIMIT 1
            """
            overview_data = fetch_data(overview_query)

            # Genres data from normalized view
            genres_query = """
            SELECT * FROM analytics.trend_summary_top_genres_normalized
            WHERE analysis_timestamp = (
                SELECT MAX(analysis_timestamp) FROM analytics.trend_summary_top_genres_normalized
            )
            ORDER BY popularity_score DESC
            LIMIT 15
            """
            genres_data = fetch_data(genres_query)

            # Sentiment patterns
            sentiment_query = """
            SELECT * FROM analytics.trend_summary_sentiment_patterns
            ORDER BY analysis_timestamp DESC
            LIMIT 1
            """
            sentiment_data = fetch_data(sentiment_query)

            # Engagement levels
            engagement_query = """
            SELECT * FROM analytics.trend_summary_engagement_levels
            ORDER BY analysis_timestamp DESC
            LIMIT 1
            """
            engagement_data = fetch_data(engagement_query)

            return {
                'artists': artists_data,
                'overview': overview_data,
                'genres': genres_data,
                'sentiment_patterns': sentiment_data,
                'engagement_levels': engagement_data
            }
        except Exception as e:
            st.warning(f"AI trend summary not available: {e}")
            return {
                'artists': pd.DataFrame(),
                'overview': pd.DataFrame(),
                'genres': pd.DataFrame(),
                'sentiment_patterns': pd.DataFrame(),
                'engagement_levels': pd.DataFrame()
            }

    @staticmethod
    @st.cache_data(ttl=300)
    def get_insights_summary_data() -> Dict[str, pd.DataFrame]:
        """Fetch AI insights summary data"""
        try:
            # Overview insights
            overview_query = """
            SELECT * FROM analytics.insights_summary_overview
            ORDER BY analysis_timestamp DESC
            LIMIT 1
            """
            overview_data = fetch_data(overview_query)

            # Key findings
            findings_query = """
            SELECT * FROM analytics.insights_summary_key_findings
            ORDER BY analysis_timestamp DESC
            LIMIT 1
            """
            findings_data = fetch_data(findings_query)

            # Artist insights
            artist_insights_query = """
            SELECT * FROM analytics.insights_summary_artist_insights_dashboard
            ORDER BY analysis_timestamp DESC
            """
            artist_insights_data = fetch_data(artist_insights_query)
            artist_insights_data = DataManager.decode_artist_names(artist_insights_data)

            return {
                'overview': overview_data,
                'findings': findings_data,
                'artist_insights': artist_insights_data
            }
        except Exception as e:
            st.warning(f"AI insights not available: {e}")
            return {
                'overview': pd.DataFrame(),
                'findings': pd.DataFrame(),
                'artist_insights': pd.DataFrame()
            }

    # === ENRICHED DATA ===

    @staticmethod
    @st.cache_data
    def get_artist_analytics_hub_data() -> Dict[str, pd.DataFrame]:
        """Fetch all data for the unified Artist Analytics Hub"""
        try:
            data = {}

            # Core artist trends
            data['trends'] = DataManager.get_artist_trends()

            # Sentiment analysis
            sentiment_query = """
            SELECT
                artist_name,
                overall_sentiment,
                avg_sentiment_score as sentiment_score,
                mention_count
            FROM analytics.artist_sentiment_dashboard
            ORDER BY mention_count DESC
            """
            data['sentiment'] = DataManager.decode_artist_names(fetch_data(sentiment_query))

            # Enriched artist data
            enriched_query = """
            SELECT * FROM analytics.artist_trends_enriched_dashboard
            ORDER BY total_mentions DESC
            LIMIT 100
            """
            data['enriched'] = DataManager.decode_artist_names(fetch_data(enriched_query))

            # URL analysis
            url_query = """
            SELECT * FROM analytics.url_analysis_dashboard
            ORDER BY mention_count DESC
            LIMIT 50
            """
            data['url_analysis'] = DataManager.decode_artist_names(fetch_data(url_query))

            # Author influence
            author_query = """
            SELECT * FROM analytics.author_influence_dashboard
            ORDER BY total_mentions DESC
            LIMIT 50
            """
            data['author_influence'] = fetch_data(author_query)

            return data

        except Exception as e:
            st.error(f"Error loading artist analytics data: {e}")
            return {
                'trends': pd.DataFrame(),
                'sentiment': pd.DataFrame(),
                'enriched': pd.DataFrame(),
                'url_analysis': pd.DataFrame(),
                'author_influence': pd.DataFrame()
            }

    # === SPECIALIZED DATA ===

    @staticmethod
    @st.cache_data
    def get_genre_artist_diversity() -> pd.DataFrame:
        """Fetch genre artist diversity data"""
        query = "SELECT * FROM analytics.genre_artist_diversity_dashboard"
        return fetch_data(query)

    @staticmethod
    @st.cache_data
    def get_artists_without_genre_count() -> int:
        """Get count of artists without genre assignment"""
        query = "SELECT artists_without_genre FROM analytics.artists_without_genre_dashboard"
        result = fetch_data(query)
        return result.iloc[0]['artists_without_genre'] if not result.empty else 0

    @staticmethod
    @st.cache_data
    def get_video_context_data() -> pd.DataFrame:
        """Fetch video context data"""
        query = """
        SELECT * FROM analytics.video_context_dashboard
        ORDER BY total_artist_mentions DESC
        LIMIT 100
        """
        try:
            return DataManager.decode_artist_names(fetch_data(query))
        except Exception as e:
            st.warning(f"Video context data not available: {e}")
            return pd.DataFrame()

    # === DATA VALIDATION ===

    @staticmethod
    def validate_dataframe(df: pd.DataFrame, expected_columns: list = None) -> bool:
        """Validate DataFrame structure and content"""
        if df is None or df.empty:
            return False

        if expected_columns:
            missing_cols = set(expected_columns) - set(df.columns)
            if missing_cols:
                st.warning(f"Missing expected columns: {missing_cols}")
                return False

        return True

    @staticmethod
    def safe_get_data(func, fallback=None):
        """Safely execute data fetching function with fallback"""
        try:
            result = func()
            return result if result is not None else fallback
        except Exception as e:
            st.warning(f"Data loading error: {e}")
            return fallback or pd.DataFrame()

    # === GET LUCKY FEATURE ===

    @staticmethod
    @st.cache_data(ttl=300)  # Cache for 5 minutes since YouTube API has quota limits
    def get_artist_youtube_videos(artist_name: str) -> List[Dict[str, Any]]:
        """Get YouTube videos for an artist using the YouTube API"""
        try:
            from youtube_search import search_artist_videos
            return search_artist_videos(artist_name, max_results=5)
        except ImportError:
            st.warning("YouTube API not available. Please check API configuration.")
            return []
        except Exception as e:
            st.error(f"Error fetching YouTube videos: {e}")
            return []

    @staticmethod
    @st.cache_data(ttl=60)  # Cache for 1 minute to allow quick re-rolls
    def get_random_artist_profile() -> Dict[str, Any]:
        """Get a comprehensive profile for a randomly selected artist"""
        try:
            # First, get a random artist from the main artist trends
            random_query = """
            SELECT
                artist_name,
                mention_count,
                sentiment_score,
                trend_strength,
                trend_direction,
                engagement_level,
                platform_count
            FROM analytics.artist_trends_dashboard
            ORDER BY RANDOM()
            LIMIT 1
            """

            basic_info = fetch_data(random_query)
            if basic_info.empty:
                return {}

            artist_name = basic_info.iloc[0]['artist_name']

            # Get comprehensive artist data across all tables
            profile = {
                'basic_info': {
                    'name': artist_name,
                    'mention_count': int(basic_info.iloc[0]['mention_count']),
                    'sentiment_score': float(basic_info.iloc[0]['sentiment_score']),
                    'trend_strength': float(basic_info.iloc[0]['trend_strength']),
                    'trend_direction': basic_info.iloc[0]['trend_direction'],
                    'engagement_level': basic_info.iloc[0]['engagement_level'],
                    'platform_count': int(basic_info.iloc[0]['platform_count'])
                }
            }

            # Get artist rankings across different metrics
            profile['rankings'] = DataManager._get_artist_rankings(artist_name)

            # Get genre associations
            profile['genres'] = DataManager._get_artist_genres(artist_name)

            # Get platform presence
            profile['platforms'] = DataManager._get_artist_platforms(artist_name)

            # Get sentiment details
            profile['sentiment_details'] = DataManager._get_artist_sentiment_details(artist_name)

            # Get AI insights if available
            profile['ai_insights'] = DataManager._get_artist_ai_insights(artist_name)

            return profile

        except Exception as e:
            st.error(f"Error getting random artist profile: {e}")
            return {}

    @staticmethod
    def _get_artist_rankings(artist_name: str) -> Dict[str, Any]:
        """Get artist rankings across different metrics"""
        try:
            ranking_query = f"""
            WITH artist_ranks AS (
                SELECT
                    artist_name,
                    ROW_NUMBER() OVER (ORDER BY mention_count DESC) as mention_rank,
                    ROW_NUMBER() OVER (ORDER BY sentiment_score DESC) as sentiment_rank,
                    ROW_NUMBER() OVER (ORDER BY trend_strength DESC) as trend_rank,
                    ROW_NUMBER() OVER (ORDER BY platform_count DESC) as platform_rank,
                    COUNT(*) OVER () as total_artists
                FROM analytics.artist_trends_dashboard
            )
            SELECT
                mention_rank,
                sentiment_rank,
                trend_rank,
                platform_rank,
                total_artists
            FROM artist_ranks
            WHERE artist_name = '{artist_name}'
            """
            rankings = fetch_data(ranking_query)
            if not rankings.empty:
                row = rankings.iloc[0]
                return {
                    'mention_rank': int(row['mention_rank']),
                    'sentiment_rank': int(row['sentiment_rank']),
                    'trend_rank': int(row['trend_rank']),
                    'platform_rank': int(row['platform_rank']),
                    'total_artists': int(row['total_artists'])
                }
            return {}
        except Exception:
            return {}

    @staticmethod
    def _get_artist_genres(artist_name: str) -> list:
        """Get genres associated with the artist"""
        try:
            genre_query = f"""
            SELECT DISTINCT genre_name
            FROM analytics.genre_artists_dashboard
            WHERE artist_name = '{artist_name}'
            ORDER BY mention_count DESC
            LIMIT 5
            """

            genres = fetch_data(genre_query)
            return genres['genre_name'].tolist() if not genres.empty else []
        except Exception:
            return []

    @staticmethod
    def _get_artist_platforms(artist_name: str) -> Dict[str, Any]:
        """Get platform-specific data for the artist"""
        try:
            # Try to get enriched data first
            platform_query = f"""
            SELECT
                youtube_mentions,
                reddit_mentions,
                total_mentions,
                unique_videos_mentioned,
                unique_posts_mentioned,
                unique_channels,
                unique_subreddits
            FROM analytics.artist_trends_enriched_dashboard
            WHERE artist_name = '{artist_name}'
            """

            platforms = fetch_data(platform_query)
            if not platforms.empty:
                row = platforms.iloc[0]
                return {
                    'youtube_mentions': int(row['youtube_mentions']) if pd.notna(row['youtube_mentions']) else 0,
                    'reddit_mentions': int(row['reddit_mentions']) if pd.notna(row['reddit_mentions']) else 0,
                    'total_mentions': int(row['total_mentions']) if pd.notna(row['total_mentions']) else 0,
                    'unique_videos': int(row['unique_videos_mentioned']) if pd.notna(row['unique_videos_mentioned']) else 0,
                    'unique_posts': int(row['unique_posts_mentioned']) if pd.notna(row['unique_posts_mentioned']) else 0,
                    'unique_channels': int(row['unique_channels']) if pd.notna(row['unique_channels']) else 0,
                    'unique_subreddits': int(row['unique_subreddits']) if pd.notna(row['unique_subreddits']) else 0
                }
            return {}
        except Exception:
            return {}

    @staticmethod
    def _get_artist_sentiment_details(artist_name: str) -> Dict[str, Any]:
        """Get detailed sentiment information for the artist"""
        try:
            sentiment_query = f"""
            SELECT
                overall_sentiment,
                avg_sentiment_score as sentiment_score,
                mention_count
            FROM analytics.artist_sentiment_dashboard
            WHERE artist_name = '{artist_name}'
            """

            sentiment = fetch_data(sentiment_query)
            if not sentiment.empty:
                row = sentiment.iloc[0]
                return {
                    'overall_sentiment': row['overall_sentiment'],
                    'sentiment_score': float(row['sentiment_score']),
                    'mention_count': int(row['mention_count'])
                }
            return {}
        except Exception:
            return {}

    @staticmethod
    def _get_artist_ai_insights(artist_name: str) -> list:
        """Get AI-generated insights for the artist"""
        try:
            insights_query = f"""
            SELECT insight_text
            FROM analytics.artist_insights_dashboard
            WHERE artist_name = '{artist_name}'
            ORDER BY RANDOM()
            LIMIT 3
            """

            insights = fetch_data(insights_query)
            return insights['insight_text'].tolist() if not insights.empty else []
        except Exception:
            return []
