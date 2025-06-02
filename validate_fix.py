#!/usr/bin/env python3
"""
Quick validation script to test the fixed artist trends query
Run this inside the dashboard container to verify mention counts are realistic
"""
import psycopg2
import pandas as pd
from datetime import datetime

def validate_artist_trends_fix():
    """Validate that the artist trends fix is working correctly"""

    try:
        # Connect to database
        conn = psycopg2.connect(
            host='social_media_tracker_db',
            database='social_db',
            user='dbt',
            password='bossart'
        )
        cursor = conn.cursor()

        print("🔍 Validating Artist Trends Fix")
        print("=" * 50)

        # Get some baseline numbers first
        cursor.execute("SELECT COUNT(*) FROM analytics.entity_extraction WHERE entities_artists IS NOT NULL")
        total_entity_rows = cursor.fetchone()[0]
        print(f"📊 Total entity extraction rows with artists: {total_entity_rows}")

        cursor.execute("SELECT COUNT(*) FROM analytics.sentiment_analysis")
        total_sentiment_rows = cursor.fetchone()[0]
        print(f"📊 Total sentiment analysis rows: {total_sentiment_rows}")

        # Test the fixed query
        fixed_query = """
        WITH artist_stats AS (
            SELECT
                jsonb_array_elements_text(ee.entities_artists) as artist_name,
                COUNT(*) as mention_count,
                AVG(ee.confidence_score) as avg_confidence,
                COUNT(DISTINCT ee.source_platform) as platform_count,
                AVG(COALESCE(sa.sentiment_strength, 5.0)) as sentiment_score
            FROM analytics.entity_extraction ee
            LEFT JOIN analytics.sentiment_analysis sa ON ee.original_text = sa.original_text
            WHERE ee.entities_artists IS NOT NULL
            AND jsonb_array_length(ee.entities_artists) > 0
            GROUP BY jsonb_array_elements_text(ee.entities_artists)
            HAVING COUNT(*) >= 3  -- Only artists with at least 3 mentions
        )
        SELECT
            artist_name,
            mention_count,
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
        FROM artist_stats
        ORDER BY mention_count DESC
        LIMIT 10
        """

        cursor.execute(fixed_query)
        results = cursor.fetchall()

        print(f"\n✅ Fixed Query Results:")
        print("-" * 80)
        print(f"{'Artist':<25} {'Mentions':<10} {'Sentiment':<10} {'Platforms':<10} {'Trend':<10}")
        print("-" * 80)

        max_mentions = 0
        total_mentions = 0

        for row in results:
            artist_name, mention_count, sentiment_score, trend_strength, trend_direction, engagement_level, platform_count = row
            print(f"{artist_name[:24]:<25} {mention_count:<10} {sentiment_score:<10.1f} {platform_count:<10} {trend_direction:<10}")
            max_mentions = max(max_mentions, mention_count)
            total_mentions += mention_count

        print("-" * 80)
        print(f"Max mentions: {max_mentions}")
        print(f"Total mentions shown: {total_mentions}")

        # Validation checks
        print(f"\n🧪 Validation Results:")

        if max_mentions > total_entity_rows * 5:  # Should not be more than 5x the total rows (generous threshold)
            print(f"❌ FAIL: Max mentions ({max_mentions}) still seem inflated compared to total entity rows ({total_entity_rows})")
            return False
        elif max_mentions > 1000:
            print(f"⚠️  WARNING: Max mentions ({max_mentions}) seems high but might be realistic")
        else:
            print(f"✅ PASS: Mention counts look realistic (max: {max_mentions})")

        if total_mentions > total_entity_rows * 10:  # Total should not be more than 10x entity rows
            print(f"❌ FAIL: Total mentions ({total_mentions}) seems inflated")
            return False
        else:
            print(f"✅ PASS: Total mention distribution looks reasonable")

        print(f"\n🎯 Summary: Artist trends fix appears to be working correctly!")
        return True

    except Exception as e:
        print(f"❌ Error validating fix: {e}")
        return False
    finally:
        try:
            conn.close()
        except:
            pass

if __name__ == "__main__":
    validate_artist_trends_fix()
