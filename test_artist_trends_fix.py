#!/usr/bin/env python3
"""
Test script to verify the artist trends fix is working correctly
"""
import psycopg2

def test_artist_trends_fix():
    """Test the fixed artist trends query to ensure realistic mention counts"""
    try:
        conn = psycopg2.connect(
            host='localhost',
            port=5434,
            database='social_db',
            user='dbt',
            password='bossart'
        )
        cursor = conn.cursor()

        print("Testing the fixed artist trends query...")
        print("=" * 50)

        # Test the new simplified query
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

        print("Top 10 artists with fixed query:")
        print("-" * 80)
        print(f"{'Artist':<25} {'Mentions':<10} {'Sentiment':<10} {'Trend':<10} {'Engagement':<12}")
        print("-" * 80)

        for row in results:
            artist_name, mention_count, sentiment_score, trend_strength, trend_direction, engagement_level, platform_count = row
            print(f"{artist_name[:24]:<25} {mention_count:<10} {sentiment_score:<10.1f} {trend_direction:<10} {engagement_level:<12}")

        print("-" * 80)

        # Also check total database scale for context
        cursor.execute("SELECT COUNT(*) FROM analytics.entity_extraction WHERE entities_artists IS NOT NULL")
        total_entity_rows = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM analytics.sentiment_analysis")
        total_sentiment_rows = cursor.fetchone()[0]

        print(f"\nDatabase context:")
        print(f"Total entity extraction rows with artists: {total_entity_rows}")
        print(f"Total sentiment analysis rows: {total_sentiment_rows}")

        # Verify the highest mention count is reasonable
        if results:
            max_mentions = results[0][1]  # mention_count of first (highest) result
            print(f"Highest mention count: {max_mentions}")

            if max_mentions > total_entity_rows * 2:  # Should not be more than 2x the total rows
                print("⚠️  WARNING: Mention counts still seem inflated!")
                return False
            else:
                print("✅ Mention counts look realistic!")
                return True

        conn.close()

    except Exception as e:
        print(f"Error testing artist trends: {e}")
        return False

if __name__ == "__main__":
    test_artist_trends_fix()
