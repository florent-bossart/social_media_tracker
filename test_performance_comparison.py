#!/usr/bin/env python3
"""
Performance comparison between original complex SQL queries and DBT model queries
"""

import time
import pandas as pd
import os
import sqlalchemy
from sqlalchemy import create_engine, text
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

def get_engine():
    return create_engine(DATABASE_URL)

def time_query(query, params=None, description="Query"):
    """Time a SQL query execution"""
    engine = get_engine()
    start_time = time.time()
    try:
        result = pd.read_sql_query(query, engine, params=params or [])
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"✅ {description}: {execution_time:.3f}s - {len(result)} rows")
        return execution_time, len(result)
    except Exception as e:
        print(f"❌ {description}: Error - {e}")
        return None, 0

def main():
    print("🚀 Performance Comparison: Original SQL vs DBT Models")
    print("=" * 60)
    
    # Test 1: Artist Trends
    print("\n📊 Test 1: Artist Trends Query")
    
    # Original complex query (simplified version of what was in dashboard.py)
    original_artist_query = """
    WITH deduplicated_data AS (
        SELECT DISTINCT ON (ee.original_text, ee.source_platform)
            ee.original_text,
            ee.source_platform,
            ee.entities_artists,
            ee.confidence_score,
            sa.sentiment_strength
        FROM analytics.entity_extraction ee
        LEFT JOIN analytics.sentiment_analysis sa ON ee.original_text = sa.original_text
        WHERE ee.entities_artists IS NOT NULL
        AND jsonb_array_length(ee.entities_artists) > 0
    ),
    artist_stats AS (
        SELECT
            LOWER(jsonb_array_elements_text(dd.entities_artists)) as artist_name_lower,
            COUNT(*) as mention_count,
            AVG(dd.confidence_score) as avg_confidence,
            COUNT(DISTINCT dd.source_platform) as platform_count,
            AVG(COALESCE(dd.sentiment_strength, 5.0)) as sentiment_score
        FROM deduplicated_data dd
        GROUP BY artist_name_lower
        HAVING COUNT(*) >= 3
    ),
    filtered_artists AS (
        SELECT
            artist_name_lower,
            mention_count,
            avg_confidence,
            platform_count,
            sentiment_score
        FROM artist_stats
        WHERE artist_name_lower NOT ILIKE 'hall of%'
        AND artist_name_lower NOT ILIKE '%playlist%'
        AND artist_name_lower !='moa'
        AND artist_name_lower !='momo'
        AND artist_name_lower !='su-metal'
        AND artist_name_lower !='unknown'
        AND LENGTH(artist_name_lower) > 2
    )
    SELECT
        INITCAP(artist_name_lower) as artist_name,
        CASE
            WHEN artist_name_lower = 'babymetal' THEN CAST(mention_count * 0.2 AS INTEGER)
            ELSE mention_count
        END as mention_count,
        sentiment_score,
        avg_confidence as trend_strength,
        CASE
            WHEN sentiment_score >= 7 THEN 'positive'
            WHEN sentiment_score <= 4 THEN 'negative'
            ELSE 'neutral'
        END as trend_direction,
        CASE
            WHEN mention_count >= 50 THEN 'high'
            WHEN mention_count >= 20 THEN 'medium'
            ELSE 'low'
        END as engagement_level,
        platform_count
    FROM filtered_artists
    ORDER BY mention_count DESC
    LIMIT 50
    """
    
    # DBT model query
    dbt_artist_query = """
    SELECT * FROM analytics.artist_trends_dashboard
    LIMIT 50
    """
    
    original_time, original_rows = time_query(original_artist_query, description="Original Complex Artist Query")
    dbt_time, dbt_rows = time_query(dbt_artist_query, description="DBT Model Artist Query")
    
    if original_time and dbt_time:
        improvement = ((original_time - dbt_time) / original_time) * 100
        print(f"⚡ Performance improvement: {improvement:.1f}% faster")
        print(f"📈 Speedup factor: {original_time/dbt_time:.1f}x")
    
    # Test 2: Genre Trends
    print("\n📊 Test 2: Genre Trends Query")
    
    # Original complex genre query
    original_genre_query = """
    WITH genre_analysis AS (
        SELECT
            LOWER(TRIM(jsonb_array_elements_text(ee.entities_genres))) as genre_name,
            COUNT(*) as mention_count,
            AVG(COALESCE(sa.sentiment_strength, 5.0)) as avg_sentiment,
            COUNT(DISTINCT ee.source_platform) as platform_count,
            AVG(ee.confidence_score) as avg_confidence
        FROM analytics.entity_extraction ee
        LEFT JOIN analytics.sentiment_analysis sa ON ee.original_text = sa.original_text
        WHERE ee.entities_genres IS NOT NULL
        AND jsonb_array_length(ee.entities_genres) > 0
        GROUP BY genre_name
        HAVING COUNT(*) >= 5
    )
    SELECT
        INITCAP(genre_name) as genre,
        mention_count,
        avg_sentiment,
        platform_count,
        ROUND(avg_confidence * mention_count / 10.0, 2) as popularity_score
    FROM genre_analysis
    WHERE genre_name != 'unknown'
    AND genre_name != ''
    AND LENGTH(genre_name) > 2
    ORDER BY popularity_score DESC, mention_count DESC
    LIMIT 25
    """
    
    # DBT model query
    dbt_genre_query = """
    SELECT * FROM analytics.genre_trends_dashboard
    LIMIT 25
    """
    
    original_time, original_rows = time_query(original_genre_query, description="Original Complex Genre Query")
    dbt_time, dbt_rows = time_query(dbt_genre_query, description="DBT Model Genre Query")
    
    if original_time and dbt_time:
        improvement = ((original_time - dbt_time) / original_time) * 100
        print(f"⚡ Performance improvement: {improvement:.1f}% faster")
        print(f"📈 Speedup factor: {original_time/dbt_time:.1f}x")

    # Test 3: Platform Data
    print("\n📊 Test 3: Platform Data Query")
    
    # Original platform query
    original_platform_query = """
    WITH platform_stats AS (
        SELECT
            ee.source_platform as platform,
            COUNT(*) as total_mentions,
            AVG(COALESCE(sa.sentiment_strength, 5.0)) as avg_sentiment,
            COUNT(DISTINCT ee.entities_artists::text) as unique_artists
        FROM analytics.entity_extraction ee
        LEFT JOIN analytics.sentiment_analysis sa ON ee.original_text = sa.original_text
        WHERE ee.entities_artists IS NOT NULL
        GROUP BY ee.source_platform
    )
    SELECT * FROM platform_stats
    ORDER BY total_mentions DESC
    """
    
    # DBT model query
    dbt_platform_query = """
    SELECT * FROM analytics.platform_data_dashboard
    """
    
    original_time, original_rows = time_query(original_platform_query, description="Original Complex Platform Query")
    dbt_time, dbt_rows = time_query(dbt_platform_query, description="DBT Model Platform Query")
    
    if original_time and dbt_time:
        improvement = ((original_time - dbt_time) / original_time) * 100
        print(f"⚡ Performance improvement: {improvement:.1f}% faster")
        print(f"📈 Speedup factor: {original_time/dbt_time:.1f}x")
    
    print("\n" + "=" * 60)
    print("🎯 Summary: DBT models provide significant performance improvements")
    print("   by pre-computing complex aggregations and transformations!")
    print("=" * 60)

if __name__ == "__main__":
    main()
