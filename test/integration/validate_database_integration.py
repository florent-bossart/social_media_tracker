#!/usr/bin/env python3
"""
Complete Database Integration Validation Script
This script comprehensively tests all aspects of the database integration
"""

import psycopg2
import json
from datetime import datetime

def connect_to_database():
    """Connect to PostgreSQL database"""
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5433,
            database="social_db",
            user="dbt",
            password="dbt"
        )
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

def test_table_data(conn):
    """Test data in all pipeline tables"""
    cursor = conn.cursor()

    tables = [
        'analytics.entity_extraction',
        'analytics.sentiment_analysis',
        'analytics.trend_analysis',
        'analytics.summarization_metrics',
        'analytics.summarization_insights'
    ]

    print("=== TABLE DATA VALIDATION ===")
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"{table}: {count} records")

        # Show sample data
        cursor.execute(f"SELECT * FROM {table} LIMIT 1")
        sample = cursor.fetchone()
        if sample:
            print(f"  Sample record: {sample[:3]}...")  # First 3 columns
        print()

def test_analytics_views(conn):
    """Test all analytics views"""
    cursor = conn.cursor()

    print("=== ANALYTICS VIEWS VALIDATION ===")

    # Test pipeline overview
    print("1. Pipeline Overview:")
    cursor.execute("SELECT * FROM analytics.pipeline_overview")
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]} records, confidence: {row[4]:.3f}")
    print()

    # Test artist trends summary
    print("2. Artist Trends Summary:")
    cursor.execute("SELECT * FROM analytics.artist_trends_summary")
    for row in cursor.fetchall():
        print(f"  {row[0]}: strength={row[3]:.2f}, sentiment={row[2]}, direction={row[4]}")
    print()

    # Test platform sentiment comparison
    print("3. Platform Sentiment Comparison:")
    cursor.execute("SELECT * FROM analytics.platform_sentiment_comparison")
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]} comments, avg_sentiment={row[2]:.1f}, {row[6]:.1f}% positive")
    print()

    # Test daily trends
    print("4. Daily Trends:")
    cursor.execute("SELECT * FROM analytics.daily_trends")
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]} entities, avg_sentiment={row[2]:.1f}, {row[6]} neutral trends")
    print()

def test_analytics_functions(conn):
    """Test analytics functions"""
    cursor = conn.cursor()

    print("=== ANALYTICS FUNCTIONS VALIDATION ===")

    # Test get_top_trending_artists
    print("1. Top Trending Artists (2025-05-29):")
    cursor.execute("SELECT * FROM analytics.get_top_trending_artists('2025-05-29'::DATE)")
    for row in cursor.fetchall():
        print(f"  {row[0]}: strength={row[1]:.2f}, mentions={row[3]}")
    print()

    # Test get_artist_sentiment_evolution
    print("2. Wagakki Band Sentiment Evolution:")
    cursor.execute("SELECT * FROM analytics.get_artist_sentiment_evolution('Wagakki Band')")
    for row in cursor.fetchall():
        print(f"  {row[0]}: sentiment={row[1]:.1f} ({row[3]}), confidence={row[2]:.2f}")
    print()

def test_data_quality(conn):
    """Test data quality and consistency"""
    cursor = conn.cursor()

    print("=== DATA QUALITY VALIDATION ===")

    # Check for NULL values in critical fields
    print("1. NULL Value Check:")
    critical_checks = [
        ("entity_extraction", "artists_found"),
        ("sentiment_analysis", "overall_sentiment"),
        ("trend_analysis", "entity_name"),
        ("summarization_metrics", "confidence_score")
    ]

    for table, column in critical_checks:
        cursor.execute(f"SELECT COUNT(*) FROM analytics.{table} WHERE {column} IS NULL")
        null_count = cursor.fetchone()[0]
        print(f"  {table}.{column}: {null_count} NULL values")
    print()

    # Check date ranges
    print("2. Date Range Check:")
    date_checks = [
        ("entity_extraction", "extraction_date"),
        ("sentiment_analysis", "processing_date"),
        ("trend_analysis", "first_seen")
    ]

    for table, column in date_checks:
        cursor.execute(f"SELECT MIN({column}), MAX({column}) FROM analytics.{table}")
        min_date, max_date = cursor.fetchone()
        print(f"  {table}.{column}: {min_date} to {max_date}")
    print()

    # Check confidence score ranges
    print("3. Confidence Score Ranges:")
    confidence_checks = [
        ("entity_extraction", "confidence_score"),
        ("sentiment_analysis", "sentiment_confidence"),
        ("summarization_metrics", "confidence_score")
    ]

    for table, column in confidence_checks:
        cursor.execute(f"SELECT MIN({column}), MAX({column}), AVG({column}) FROM analytics.{table}")
        min_conf, max_conf, avg_conf = cursor.fetchone()
        print(f"  {table}.{column}: min={min_conf:.3f}, max={max_conf:.3f}, avg={avg_conf:.3f}")
    print()

def generate_analytics_report(conn):
    """Generate a comprehensive analytics report"""
    cursor = conn.cursor()

    print("=== COMPREHENSIVE ANALYTICS REPORT ===")
    print(f"Generated at: {datetime.now()}")
    print()

    # Summary statistics
    cursor.execute("""
        SELECT
            COUNT(DISTINCT ee.artists_found) as unique_artists,
            COUNT(DISTINCT sa.source_platform) as unique_platforms,
            SUM(ta.mention_count) as total_mentions,
            AVG(sa.sentiment_strength) as avg_sentiment,
            AVG(sm.confidence_score) as avg_confidence
        FROM analytics.entity_extraction ee
        CROSS JOIN analytics.sentiment_analysis sa
        CROSS JOIN analytics.trend_analysis ta
        CROSS JOIN analytics.summarization_metrics sm
    """)

    stats = cursor.fetchone()
    print("Summary Statistics:")
    print(f"  Unique Artists: {stats[0]}")
    print(f"  Unique Platforms: {stats[1]}")
    print(f"  Total Mentions: {stats[2]}")
    print(f"  Average Sentiment: {stats[3]:.2f}")
    print(f"  Average Confidence: {stats[4]:.2f}")
    print()

    # Top insights
    print("Key Insights:")
    cursor.execute("SELECT insight_type, content FROM analytics.summarization_insights WHERE insight_type = 'executive_summary'")
    summary = cursor.fetchone()
    if summary:
        print(f"  Executive Summary: {summary[1][:100]}...")

    cursor.execute("SELECT insight_type, content FROM analytics.summarization_insights WHERE insight_type = 'key_findings'")
    findings = cursor.fetchone()
    if findings:
        print(f"  Key Findings: {findings[1][:100]}...")
    print()

def main():
    """Main testing function"""
    print("Japanese Music Trends Analysis - Database Integration Test")
    print("=" * 60)

    conn = connect_to_database()
    if not conn:
        print("Failed to connect to database. Exiting.")
        return

    try:
        test_table_data(conn)
        test_analytics_views(conn)
        test_analytics_functions(conn)
        test_data_quality(conn)
        generate_analytics_report(conn)

        print("=== TEST COMPLETED SUCCESSFULLY ===")
        print("All database integration tests passed!")

    except Exception as e:
        print(f"Error during testing: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
