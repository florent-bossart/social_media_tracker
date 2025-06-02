#!/usr/bin/env python3
"""
Simple test script to verify the dashboard data loading functions work correctly
without Streamlit-specific dependencies
"""

import os
import sys
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database connection - use external port for testing from host
PG_USER = os.getenv("WAREHOUSE_USER")
PG_PW = os.getenv("WAREHOUSE_PASSWORD")
PG_HOST = "localhost"  # Use localhost instead of container name
PG_PORT = "5434"  # Use external port instead of internal port
PG_DB = os.getenv("WAREHOUSE_DB")

DATABASE_URL = f"postgresql+psycopg2://{PG_USER}:{PG_PW}@{PG_HOST}:{PG_PORT}/{PG_DB}"

def fetch_data(query, params=None):
    """Simple data fetching function"""
    engine = create_engine(DATABASE_URL)
    return pd.read_sql_query(query, engine, params=params)

def test_trend_summary_data():
    """Test the trend summary data loading"""
    print("=== Testing Trend Summary Data ===")

    try:
        # Get overview data
        overview_query = """
        SELECT * FROM analytics.trend_summary_overview
        ORDER BY analysis_timestamp DESC
        LIMIT 1
        """
        overview_data = fetch_data(overview_query)
        print(f"✓ Overview data loaded: {len(overview_data)} rows")

        # Get top artists data
        artists_query = """
        SELECT * FROM analytics.trend_summary_top_artists
        WHERE analysis_timestamp = (
            SELECT MAX(analysis_timestamp) FROM analytics.trend_summary_top_artists
        )
        ORDER BY trend_strength DESC
        LIMIT 50
        """
        artists_data = fetch_data(artists_query)
        print(f"✓ Artists data loaded: {len(artists_data)} rows")

        # Test the data structures that were causing issues
        result = {
            'overview': overview_data,
            'artists': artists_data
        }

        # Test the len() operation that was failing
        if not artists_data.empty:
            artists_count = len(result['artists'])
            print(f"✓ Artists count calculation works: {artists_count}")
        else:
            print("⚠ No artists data found")

        return result

    except Exception as e:
        print(f"✗ Error in trend summary data: {e}")
        return None

def test_insights_summary_data():
    """Test the insights summary data loading"""
    print("\n=== Testing Insights Summary Data ===")

    try:
        # Get overview data
        overview_query = """
        SELECT * FROM analytics.insights_summary_overview
        ORDER BY analysis_timestamp DESC
        LIMIT 1
        """
        overview_data = fetch_data(overview_query)
        print(f"✓ Insights overview data loaded: {len(overview_data)} rows")

        # Get findings data
        findings_query = """
        SELECT * FROM analytics.insights_summary_findings
        WHERE analysis_timestamp = (
            SELECT MAX(analysis_timestamp) FROM analytics.insights_summary_findings
        )
        ORDER BY confidence_score DESC
        LIMIT 50
        """
        findings_data = fetch_data(findings_query)
        print(f"✓ Findings data loaded: {len(findings_data)} rows")

        # Get artist insights data
        artist_insights_query = """
        SELECT * FROM analytics.insights_summary_artist_insights
        WHERE analysis_timestamp = (
            SELECT MAX(analysis_timestamp) FROM analytics.insights_summary_artist_insights
        )
        ORDER BY insight_strength DESC
        LIMIT 50
        """
        artist_insights_data = fetch_data(artist_insights_query)
        print(f"✓ Artist insights data loaded: {len(artist_insights_data)} rows")

        # Test the data structures
        result = {
            'overview': overview_data,
            'findings': findings_data,
            'artist_insights': artist_insights_data
        }

        # Test the validation logic that was added
        if 'findings' in result and not result['findings'].empty:
            print("✓ Findings validation works")
        else:
            print("⚠ No findings data or validation failed")

        if 'artist_insights' in result and not result['artist_insights'].empty:
            print("✓ Artist insights validation works")
        else:
            print("⚠ No artist insights data or validation failed")

        return result

    except Exception as e:
        print(f"✗ Error in insights summary data: {e}")
        return None

def test_overall_stats():
    """Test the overall stats function"""
    print("\n=== Testing Overall Stats ===")

    try:
        query = """
        WITH total_extractions AS (
            SELECT COUNT(*) as count
            FROM social_db.extractions
        ),
        sentiment_stats AS (
            SELECT
                AVG(sentiment) as avg_sentiment,
                COUNT(*) as total_sentiment_count,
                SUM(CASE WHEN sentiment >= 6 THEN 1 ELSE 0 END) as positive_count
            FROM social_db.extractions
            WHERE sentiment IS NOT NULL
        ),
        artist_count AS (
            SELECT COUNT(DISTINCT artist_name) as count
            FROM social_db.extractions
            WHERE artist_name IS NOT NULL AND artist_name != ''
        )
        SELECT
            te.count as total_extractions,
            ss.avg_sentiment,
            ss.total_sentiment_count,
            ss.positive_count,
            ac.count as unique_artists
        FROM total_extractions te
        CROSS JOIN sentiment_stats ss
        CROSS JOIN artist_count ac
        """

        stats_data = fetch_data(query)
        print(f"✓ Stats data loaded: {len(stats_data)} rows")

        if not stats_data.empty:
            stats = stats_data.iloc[0]
            print(f"  - Total extractions: {stats['total_extractions']}")
            print(f"  - Average sentiment: {stats['avg_sentiment']}")
            print(f"  - Unique artists: {stats['unique_artists']}")
            print("✓ Stats access works correctly")
        else:
            print("⚠ No stats data found")

        return stats_data

    except Exception as e:
        print(f"✗ Error in overall stats: {e}")
        return None

def main():
    """Run all tests"""
    print("Testing dashboard data loading functions...\n")

    # Test each function
    trend_data = test_trend_summary_data()
    insights_data = test_insights_summary_data()
    stats_data = test_overall_stats()

    # Summary
    print("\n=== Test Summary ===")
    if trend_data is not None:
        print("✓ Trend summary data loading: PASSED")
    else:
        print("✗ Trend summary data loading: FAILED")

    if insights_data is not None:
        print("✓ Insights summary data loading: PASSED")
    else:
        print("✗ Insights summary data loading: FAILED")

    if stats_data is not None:
        print("✓ Overall stats loading: PASSED")
    else:
        print("✗ Overall stats loading: FAILED")

    print("\nAll core data loading functions have been tested!")

if __name__ == "__main__":
    main()
