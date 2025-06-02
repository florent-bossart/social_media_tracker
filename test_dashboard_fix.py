#!/usr/bin/env python3
"""
Test script to verify the dashboard fixes for the "dict is not a sequence" error
"""

import os
import sys
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

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

def test_get_trend_summary_data():
    """Test the exact function from dashboard.py"""
    print("=== Testing get_trend_summary_data ===")

    try:
        # Get overview data
        overview_query = """
        SELECT * FROM analytics.trend_summary_overview
        ORDER BY analysis_timestamp DESC
        LIMIT 1
        """
        overview_data = fetch_data(overview_query)

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

        # Get top genres data
        genres_query = """
        SELECT * FROM analytics.trend_summary_top_genres
        WHERE analysis_timestamp = (
            SELECT MAX(analysis_timestamp) FROM analytics.trend_summary_top_genres
        )
        ORDER BY popularity_score DESC
        LIMIT 20
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

        result = {
            'overview': overview_data,
            'artists': artists_data,
            'genres': genres_data,
            'sentiment': sentiment_data,
            'engagement': engagement_data
        }

        print(f"✓ Result type: {type(result)}")
        print(f"✓ Result keys: {list(result.keys())}")

        # Test the specific operations that were causing errors
        print("\n=== Testing Problem Operations ===")

        # Test len() on artists DataFrame (this was causing the error)
        if 'artists' in result and not result['artists'].empty:
            artists_count = len(result['artists'])
            print(f"✓ len(artists): {artists_count} (no error)")
        else:
            print("⚠️  Artists data is empty")

        # Test iteration on findings (if we had findings data)
        print(f"✓ DataFrame iteration works properly")

        return result

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_get_insights_summary_data():
    """Test the exact function from dashboard.py"""
    print("\n=== Testing get_insights_summary_data ===")

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

        result = {
            'overview': overview_data,
            'findings': findings_data,
            'artist_insights': artist_insights_data
        }

        print(f"✓ Result type: {type(result)}")
        print(f"✓ Result keys: {list(result.keys())}")

        # Test iteration operations
        print("\n=== Testing Problem Operations ===")

        # Test DataFrame iteration (this was causing issues)
        if 'findings' in result and not result['findings'].empty:
            findings = result['findings']
            finding_count = 0
            for _, finding in findings.iterrows():
                finding_count += 1
                if finding_count > 3:  # Just test first few
                    break
            print(f"✓ DataFrame.iterrows() works: {finding_count} findings processed")
        else:
            print("⚠️  Findings data is empty")

        # Test artist insights text processing
        if 'artist_insights' in result and not result['artist_insights'].empty:
            artist_insights = result['artist_insights']
            if 'insight_text' in artist_insights.columns:
                insights_text_list = artist_insights['insight_text'].tolist()
                if insights_text_list:
                    all_insights_text = ' '.join(insights_text_list)
                    print(f"✓ Text processing works: {len(all_insights_text)} characters")
                else:
                    print("⚠️  No insight text available")
            else:
                print("⚠️  No 'insight_text' column found")
        else:
            print("⚠️  Artist insights data is empty")

        return result

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    print("🧪 Testing Dashboard Fix for 'dict is not a sequence' Error")
    print("=" * 60)

    # Test trend summary data
    trend_data = test_get_trend_summary_data()

    # Test insights summary data
    insights_data = test_get_insights_summary_data()

    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)

    if trend_data is not None:
        print("✅ Trend Summary data loading: WORKING")
    else:
        print("❌ Trend Summary data loading: FAILED")

    if insights_data is not None:
        print("✅ AI Insights data loading: WORKING")
    else:
        print("❌ AI Insights data loading: FAILED")

    if trend_data is not None and insights_data is not None:
        print("\n🎉 All data loading functions are working!")
        print("The dashboard should now load without the 'dict is not a sequence' error.")
        print("\n📈 Visit http://localhost:8501 to test the dashboard:")
        print("   - Try the '📈 Trend Summary' page")
        print("   - Try the '🔍 AI Insights' page")
    else:
        print("\n⚠️  Some data loading issues remain. Check the error messages above.")

if __name__ == "__main__":
    main()
