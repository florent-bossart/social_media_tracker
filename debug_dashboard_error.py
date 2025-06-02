#!/usr/bin/env python3
"""
Debug dashboard error - Test the specific functions causing the "dict is not a sequence" error
"""

import pandas as pd
from sqlalchemy import create_engine

# Use the correct database connection for Docker
DATABASE_URL = "postgresql+psycopg2://dbt:bossart@localhost:5434/social_db"

def fetch_data(query, params=None):
    engine = create_engine(DATABASE_URL)
    return pd.read_sql_query(query, engine, params=params)

def test_get_trend_summary_data():
    """Test the get_trend_summary_data function directly"""
    print("=== Testing get_trend_summary_data ===")

    try:
        # Get overview data
        overview_query = """
        SELECT * FROM analytics.trend_summary_overview
        ORDER BY analysis_timestamp DESC
        LIMIT 1
        """
        overview_data = fetch_data(overview_query)
        print(f"✓ Overview data type: {type(overview_data)}")
        print(f"✓ Overview data shape: {overview_data.shape}")
        print(f"✓ Overview data columns: {list(overview_data.columns)}")
        print(f"✓ Overview data content sample:")
        print(overview_data.head())

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
        print(f"\n✓ Artists data type: {type(artists_data)}")
        print(f"✓ Artists data shape: {artists_data.shape}")
        print(f"✓ Artists data columns: {list(artists_data.columns)}")

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
        print(f"\n✓ Genres data type: {type(genres_data)}")
        print(f"✓ Genres data shape: {genres_data.shape}")

        # Get sentiment patterns
        sentiment_query = """
        SELECT * FROM analytics.trend_summary_sentiment_patterns
        ORDER BY analysis_timestamp DESC
        LIMIT 1
        """
        sentiment_data = fetch_data(sentiment_query)
        print(f"\n✓ Sentiment data type: {type(sentiment_data)}")
        print(f"✓ Sentiment data shape: {sentiment_data.shape}")

        # Get engagement levels
        engagement_query = """
        SELECT * FROM analytics.trend_summary_engagement_levels
        ORDER BY analysis_timestamp DESC
        LIMIT 1
        """
        engagement_data = fetch_data(engagement_query)
        print(f"\n✓ Engagement data type: {type(engagement_data)}")
        print(f"✓ Engagement data shape: {engagement_data.shape}")

        # Create the return dictionary like the dashboard function
        result = {
            'overview': overview_data,
            'artists': artists_data,
            'genres': genres_data,
            'sentiment': sentiment_data,
            'engagement': engagement_data
        }

        print(f"\n✓ Result type: {type(result)}")
        print(f"✓ Result keys: {list(result.keys())}")

        # Test iteration like Streamlit might do
        print("\n=== Testing iteration behavior ===")
        for key, value in result.items():
            print(f"  {key}: type={type(value)}, is_dataframe={isinstance(value, pd.DataFrame)}")
            if hasattr(value, 'empty'):
                print(f"    empty={value.empty}")

        return result

    except Exception as e:
        print(f"✗ Error in get_trend_summary_data: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_get_insights_summary_data():
    """Test the get_insights_summary_data function directly"""
    print("\n=== Testing get_insights_summary_data ===")

    try:
        # Get overview data
        overview_query = """
        SELECT * FROM analytics.insights_summary_overview
        ORDER BY analysis_timestamp DESC
        LIMIT 1
        """
        overview_data = fetch_data(overview_query)
        print(f"✓ Overview data type: {type(overview_data)}")
        print(f"✓ Overview data shape: {overview_data.shape}")

        # Get key findings
        findings_query = """
        SELECT * FROM analytics.insights_summary_key_findings
        WHERE analysis_timestamp = (
            SELECT MAX(analysis_timestamp) FROM analytics.insights_summary_key_findings
        )
        ORDER BY finding_order
        """
        findings_data = fetch_data(findings_query)
        print(f"\n✓ Findings data type: {type(findings_data)}")
        print(f"✓ Findings data shape: {findings_data.shape}")

        # Get artist insights
        artist_insights_query = """
        SELECT * FROM analytics.insights_summary_artist_insights
        WHERE analysis_timestamp = (
            SELECT MAX(analysis_timestamp) FROM analytics.insights_summary_artist_insights
        )
        ORDER BY artist_name
        """
        artist_insights_data = fetch_data(artist_insights_query)
        print(f"\n✓ Artist insights data type: {type(artist_insights_data)}")
        print(f"✓ Artist insights data shape: {artist_insights_data.shape}")

        # Create the return dictionary like the dashboard function
        result = {
            'overview': overview_data,
            'findings': findings_data,
            'artist_insights': artist_insights_data
        }

        print(f"\n✓ Result type: {type(result)}")
        print(f"✓ Result keys: {list(result.keys())}")

        # Test iteration like Streamlit might do
        print("\n=== Testing iteration behavior ===")
        for key, value in result.items():
            print(f"  {key}: type={type(value)}, is_dataframe={isinstance(value, pd.DataFrame)}")
            if hasattr(value, 'empty'):
                print(f"    empty={value.empty}")

        return result

    except Exception as e:
        print(f"✗ Error in get_insights_summary_data: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_simulated_streamlit_usage():
    """Test how Streamlit might use the data"""
    print("\n=== Testing simulated Streamlit usage ===")

    # Get both data sets
    trend_data = test_get_trend_summary_data()
    insights_data = test_get_insights_summary_data()

    if trend_data:
        print("\n--- Testing trend_data access patterns ---")
        try:
            # Simulate common Streamlit operations
            if not trend_data['overview'].empty:
                overview = trend_data['overview'].iloc[0]
                print(f"✓ Can access overview.iloc[0]: {type(overview)}")

            # Test if this causes the "dict is not a sequence" error
            for key, df in trend_data.items():
                if isinstance(df, pd.DataFrame) and not df.empty:
                    print(f"✓ {key} DataFrame iteration works")

        except Exception as e:
            print(f"✗ Error in trend_data simulation: {e}")
            import traceback
            traceback.print_exc()

    if insights_data:
        print("\n--- Testing insights_data access patterns ---")
        try:
            # Simulate common Streamlit operations
            if not insights_data['overview'].empty:
                overview = insights_data['overview'].iloc[0]
                print(f"✓ Can access overview.iloc[0]: {type(overview)}")

            # Test if this causes the "dict is not a sequence" error
            for key, df in insights_data.items():
                if isinstance(df, pd.DataFrame) and not df.empty:
                    print(f"✓ {key} DataFrame iteration works")

        except Exception as e:
            print(f"✗ Error in insights_data simulation: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    print("🔍 Debugging Dashboard 'dict is not a sequence' Error")
    print("=" * 60)

    # Test the individual functions
    test_get_trend_summary_data()
    test_get_insights_summary_data()

    # Test simulated Streamlit usage
    test_simulated_streamlit_usage()

    print("\n🎯 Debug complete!")
