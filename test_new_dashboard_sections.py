#!/usr/bin/env python3
"""
Test script to verify the new dashboard sections can access the summarization data
"""

import os
import sys
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Add dashboard to path
sys.path.append('dashboard')

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

def test_trend_summary_data():
    """Test trend summary data fetching"""
    print("=== Testing Trend Summary Data ===")

    try:
        # Get overview data
        overview_query = """
        SELECT * FROM analytics.trend_summary_overview
        ORDER BY analysis_timestamp DESC
        LIMIT 1
        """
        overview_data = fetch_data(overview_query)
        print(f"✓ Overview data: {len(overview_data)} records")

        # Get top artists data
        artists_query = """
        SELECT * FROM analytics.trend_summary_top_artists
        WHERE analysis_timestamp = (
            SELECT MAX(analysis_timestamp) FROM analytics.trend_summary_top_artists
        )
        ORDER BY trend_strength DESC
        LIMIT 10
        """
        artists_data = fetch_data(artists_query)
        print(f"✓ Top artists data: {len(artists_data)} records")

        if not artists_data.empty:
            print("  Top 3 artists:")
            for _, row in artists_data.head(3).iterrows():
                print(f"    - {row['artist_name']}: {row['trend_strength']}")

        # Get sentiment data
        sentiment_query = """
        SELECT * FROM analytics.trend_summary_sentiment_patterns
        ORDER BY analysis_timestamp DESC
        LIMIT 1
        """
        sentiment_data = fetch_data(sentiment_query)
        print(f"✓ Sentiment patterns data: {len(sentiment_data)} records")

        return {
            'overview': overview_data,
            'artists': artists_data,
            'sentiment': sentiment_data
        }

    except Exception as e:
        print(f"✗ Error fetching trend summary data: {e}")
        return None

def test_insights_summary_data():
    """Test insights summary data fetching"""
    print("\n=== Testing Insights Summary Data ===")

    try:
        # Get overview data
        overview_query = """
        SELECT * FROM analytics.insights_summary_overview
        ORDER BY analysis_timestamp DESC
        LIMIT 1
        """
        overview_data = fetch_data(overview_query)
        print(f"✓ Insights overview data: {len(overview_data)} records")

        # Get key findings
        findings_query = """
        SELECT * FROM analytics.insights_summary_key_findings
        WHERE analysis_timestamp = (
            SELECT MAX(analysis_timestamp) FROM analytics.insights_summary_key_findings
        )
        ORDER BY finding_order
        """
        findings_data = fetch_data(findings_query)
        print(f"✓ Key findings data: {len(findings_data)} records")

        # Get artist insights
        artist_insights_query = """
        SELECT COUNT(*) as total FROM analytics.insights_summary_artist_insights
        WHERE analysis_timestamp = (
            SELECT MAX(analysis_timestamp) FROM analytics.insights_summary_artist_insights
        )
        """
        artist_insights_count = fetch_data(artist_insights_query)
        print(f"✓ Artist insights data: {artist_insights_count.iloc[0]['total']} records")

        return {
            'overview': overview_data,
            'findings': findings_data,
            'artist_insights_count': artist_insights_count.iloc[0]['total']
        }

    except Exception as e:
        print(f"✗ Error fetching insights summary data: {e}")
        return None

if __name__ == "__main__":
    print("Testing New Dashboard Sections Data Access")
    print("=" * 50)

    # Test trend summary data
    trend_data = test_trend_summary_data()

    # Test insights summary data
    insights_data = test_insights_summary_data()

    print("\n=== Summary ===")
    if trend_data:
        print("✓ Trend Summary section: Data accessible")
    else:
        print("✗ Trend Summary section: Data NOT accessible")

    if insights_data:
        print("✓ AI Insights section: Data accessible")
    else:
        print("✗ AI Insights section: Data NOT accessible")

    print("\nThe new dashboard sections should now be working!")
    print("Navigate to http://localhost:8501 and check:")
    print("  - 📈 Trend Summary")
    print("  - 🔍 AI Insights")
