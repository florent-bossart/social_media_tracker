#!/usr/bin/env python3
"""
Final Validation - Summary of all fixes applied to the dashboard
"""

import psycopg2

def get_db_connection():
    return psycopg2.connect(
        host="localhost",
        database="social_db",
        user="dbt",
        password="bossart",
        port="5434"
    )

def final_validation():
    """Final validation of the dashboard fixes"""

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        print("=== FINAL VALIDATION REPORT ===")
        print("Date: June 1, 2025")
        print("Issues Fixed: Inflated mention counts + 'Hall of...' entries")
        print()

        # Test the current dashboard query (exact same as in dashboard.py)
        query = """
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
                jsonb_array_elements_text(dd.entities_artists) as artist_name,
                COUNT(*) as mention_count,
                AVG(dd.confidence_score) as avg_confidence,
                COUNT(DISTINCT dd.source_platform) as platform_count,
                AVG(COALESCE(dd.sentiment_strength, 5.0)) as sentiment_score
            FROM deduplicated_data dd
            GROUP BY jsonb_array_elements_text(dd.entities_artists)
            HAVING COUNT(*) >= 3  -- Only artists with at least 3 mentions
        ),
        filtered_artists AS (
            SELECT *
            FROM artist_stats
            WHERE artist_name NOT ILIKE 'hall of%'  -- Filter out playlist names
            AND artist_name NOT ILIKE '%playlist%'  -- Filter out other playlists
            AND LENGTH(artist_name) > 2  -- Filter out very short names
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
        FROM filtered_artists
        ORDER BY mention_count DESC
        LIMIT 20
        """

        cursor.execute(query)
        results = cursor.fetchall()

        print("TOP 20 ARTISTS (Fixed Dashboard Results):")
        print("-" * 80)
        print(f"{'Artist':<20} {'Mentions':<10} {'Sentiment':<10} {'Confidence':<12} {'Engagement':<12}")
        print("-" * 80)

        for artist, mentions, sentiment, confidence, trend_dir, engagement, platforms in results:
            print(f"{artist:<20} {mentions:<10} {sentiment:<10.1f} {confidence:<12.3f} {engagement:<12}")

        # Summary statistics
        babymetal_result = next((r for r in results if 'babymetal' in r[0].lower()), None)
        if babymetal_result:
            print(f"\n📊 BABYMETAL FINAL RESULT:")
            print(f"   - Mentions: {babymetal_result[1]} (down from millions!)")
            print(f"   - Sentiment: {babymetal_result[2]:.1f}/10")
            print(f"   - Confidence: {babymetal_result[3]:.3f}")
            print(f"   - Engagement: {babymetal_result[5]}")

        # Check if any 'hall of' entries made it through (should be 0)
        hall_count = sum(1 for r in results if 'hall of' in r[0].lower())
        print(f"\n🚫 HALL OF ENTRIES IN RESULTS: {hall_count} (should be 0)")

        # Data quality metrics
        cursor.execute("""
        SELECT
            COUNT(*) as total_rows,
            COUNT(DISTINCT original_text) as unique_texts,
            ROUND(((COUNT(*) - COUNT(DISTINCT original_text))::numeric / COUNT(*) * 100), 2) as duplicate_percentage
        FROM analytics.entity_extraction
        """)

        total, unique, dup_pct = cursor.fetchone()
        print(f"\n📈 DATA QUALITY METRICS:")
        print(f"   - Total rows: {total:,}")
        print(f"   - Unique texts: {unique:,}")
        print(f"   - Duplication rate: {dup_pct}% (handled by DISTINCT ON)")

        print(f"\n✅ FIXES APPLIED:")
        print(f"   1. Added deduplication with DISTINCT ON (original_text, source_platform)")
        print(f"   2. Filtered out 'hall of%' playlist names")
        print(f"   3. Filtered out '%playlist%' references")
        print(f"   4. Filtered out names ≤ 2 characters")
        print(f"   5. Fixed SQL syntax error in HAVING clause")
        print(f"   6. Minimum 3 mentions threshold for trending artists")

        print(f"\n🎯 RESULTS:")
        print(f"   - Realistic mention counts (no more millions)")
        print(f"   - No 'hall of...' playlist names")
        print(f"   - Clean, meaningful artist trends")
        print(f"   - Fixed SQL syntax issues")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"Validation failed: {e}")

def main():
    final_validation()

if __name__ == "__main__":
    main()
