#!/usr/bin/env python3
"""
Test script to verify dashboard data loading functions
"""
import os
import sys
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

# Database connection
PG_USER = os.getenv("WAREHOUSE_USER")
PG_PW = os.getenv("WAREHOUSE_PASSWORD")
PG_HOST = os.getenv("WAREHOUSE_HOST")
PG_PORT = os.getenv("WAREHOUSE_PORT")
PG_DB = os.getenv("WAREHOUSE_DB")

DATABASE_URL = f"postgresql+psycopg2://{PG_USER}:{PG_PW}@{PG_HOST}:{PG_PORT}/{PG_DB}"

def fetch_data(query, params=None):
    engine = create_engine(DATABASE_URL)
    return pd.read_sql_query(query, engine, params=params)

def test_dashboard_functions():
    """Test all the dashboard data functions"""
    print("🧪 Testing Dashboard Data Functions")
    print("=" * 50)

    # Test overall stats
    try:
        stats_query = """
        SELECT
            (SELECT COUNT(*) FROM analytics.entity_extraction) as total_extractions,
            (SELECT COUNT(*) FROM analytics.sentiment_analysis) as total_sentiments,
            (SELECT COUNT(DISTINCT jsonb_array_elements_text(entities_artists))
             FROM analytics.entity_extraction
             WHERE entities_artists IS NOT NULL) as unique_artists,
            (SELECT AVG(sentiment_strength)
             FROM analytics.sentiment_analysis
             WHERE sentiment_strength IS NOT NULL) as avg_sentiment
        """
        stats = fetch_data(stats_query).iloc[0]
        print(f"✅ Overall Stats:")
        print(f"   - Total extractions: {stats['total_extractions']}")
        print(f"   - Total sentiments: {stats['total_sentiments']}")
        print(f"   - Unique artists: {stats['unique_artists']}")
        print(f"   - Average sentiment: {stats['avg_sentiment']:.3f}")
    except Exception as e:
        print(f"❌ Overall stats failed: {e}")

    # Test artist trends
    try:
        artist_query = """
        WITH artist_mentions AS (
            SELECT
                jsonb_array_elements_text(entities_artists) as artist_name,
                source_platform,
                confidence_score
            FROM analytics.entity_extraction
            WHERE entities_artists IS NOT NULL
            AND jsonb_array_length(entities_artists) > 0
        )
        SELECT
            artist_name,
            COUNT(*) as mention_count,
            AVG(confidence_score) as avg_confidence
        FROM artist_mentions
        GROUP BY artist_name
        HAVING COUNT(*) >= 3
        ORDER BY mention_count DESC
        LIMIT 5
        """
        artists = fetch_data(artist_query)
        print(f"\n✅ Artist Trends (top 5):")
        for _, artist in artists.iterrows():
            print(f"   - {artist['artist_name']}: {artist['mention_count']} mentions")
    except Exception as e:
        print(f"❌ Artist trends failed: {e}")

    # Test genre data
    try:
        genre_query = """
        WITH genre_mentions AS (
            SELECT
                jsonb_array_elements_text(entities_genres) as genre,
                confidence_score
            FROM analytics.entity_extraction
            WHERE entities_genres IS NOT NULL
            AND jsonb_array_length(entities_genres) > 0
        )
        SELECT
            genre,
            COUNT(*) as mention_count
        FROM genre_mentions
        GROUP BY genre
        HAVING COUNT(*) >= 5
        ORDER BY mention_count DESC
        LIMIT 5
        """
        genres = fetch_data(genre_query)
        print(f"\n✅ Genre Trends (top 5):")
        for _, genre in genres.iterrows():
            print(f"   - {genre['genre']}: {genre['mention_count']} mentions")
    except Exception as e:
        print(f"❌ Genre trends failed: {e}")

    # Test platform data
    try:
        platform_query = """
        SELECT
            source_platform as platform,
            COUNT(*) as total_mentions
        FROM analytics.entity_extraction
        GROUP BY source_platform
        ORDER BY total_mentions DESC
        """
        platforms = fetch_data(platform_query)
        print(f"\n✅ Platform Data:")
        for _, platform in platforms.iterrows():
            print(f"   - {platform['platform']}: {platform['total_mentions']} mentions")
    except Exception as e:
        print(f"❌ Platform data failed: {e}")

    # Test word cloud data
    try:
        wordcloud_query = """
        SELECT word, frequency
        FROM analytics.wordcloud_data
        ORDER BY frequency DESC
        LIMIT 5
        """
        words = fetch_data(wordcloud_query)
        print(f"\n✅ Word Cloud Data (top 5):")
        for _, word in words.iterrows():
            print(f"   - {word['word']}: {word['frequency']} occurrences")
    except Exception as e:
        print(f"❌ Word cloud data failed: {e}")

    # Test temporal data
    try:
        temporal_query = """
        SELECT
            DATE(extraction_date) as date,
            COUNT(*) as daily_mentions
        FROM analytics.entity_extraction
        WHERE extraction_date >= CURRENT_DATE - INTERVAL '7 days'
        GROUP BY DATE(extraction_date)
        ORDER BY date DESC
        LIMIT 5
        """
        temporal = fetch_data(temporal_query)
        print(f"\n✅ Temporal Data (last 5 days):")
        for _, day in temporal.iterrows():
            print(f"   - {day['date']}: {day['daily_mentions']} mentions")
    except Exception as e:
        print(f"❌ Temporal data failed: {e}")

    print("\n" + "=" * 50)
    print("🎉 Dashboard data test completed!")

if __name__ == "__main__":
    test_dashboard_functions()
