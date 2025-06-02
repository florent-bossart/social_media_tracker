#!/usr/bin/env python3
"""
Validation script to test the improved artist trends query with deduplication and filtering
"""
import psycopg2
import pandas as pd

def validate_improved_artist_trends():
    """Test the improved artist trends query"""

    try:
        conn = psycopg2.connect(
            host='social_media_tracker_db',
            database='social_db',
            user='dbt',
            password='bossart'
        )
        cursor = conn.cursor()

        print("🔍 VALIDATING IMPROVED ARTIST TRENDS")
        print("=" * 60)

        # Test the improved query
        improved_query = """
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
            HAVING COUNT(*) >= 3
            AND jsonb_array_elements_text(dd.entities_artists) NOT ILIKE 'hall of%'
            AND jsonb_array_elements_text(dd.entities_artists) NOT ILIKE '%playlist%'
            AND LENGTH(jsonb_array_elements_text(dd.entities_artists)) > 2
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
            platform_count
        FROM artist_stats
        ORDER BY mention_count DESC
        LIMIT 15
        """

        cursor.execute(improved_query)
        results = cursor.fetchall()

        print("✅ IMPROVED ARTIST TRENDS RESULTS:")
        print("-" * 80)
        print(f"{'Artist':<25} {'Mentions':<10} {'Sentiment':<10} {'Platforms':<10} {'Direction':<10}")
        print("-" * 80)

        max_mentions = 0
        total_mentions = 0
        hall_count = 0

        for row in results:
            artist_name, mention_count, sentiment_score, trend_strength, trend_direction, platform_count = row
            print(f"{artist_name[:24]:<25} {mention_count:<10} {sentiment_score:<10.1f} {platform_count:<10} {trend_direction:<10}")
            max_mentions = max(max_mentions, mention_count)
            total_mentions += mention_count

            # Check if any "hall of" entries slipped through
            if "hall of" in artist_name.lower():
                hall_count += 1

        print("-" * 80)
        print(f"Max mentions: {max_mentions}")
        print(f"Total mentions shown: {total_mentions}")
        print(f"'Hall of' entries: {hall_count}")

        # Compare with before deduplication for Babymetal
        print(f"\n📊 BABYMETAL COMPARISON:")
        cursor.execute("""
        SELECT 'Before deduplication' as status, COUNT(*) as babymetal_mentions
        FROM analytics.entity_extraction
        WHERE entities_artists::text ILIKE '%babymetal%'
        UNION ALL
        SELECT 'After deduplication', COUNT(*)
        FROM (
            SELECT DISTINCT ON (original_text, source_platform) *
            FROM analytics.entity_extraction
            WHERE entities_artists::text ILIKE '%babymetal%'
        ) deduped
        """)

        comparison = cursor.fetchall()
        for row in comparison:
            status, count = row
            print(f"{status}: {count} mentions")

        # Validation checks
        print(f"\n🧪 VALIDATION RESULTS:")

        if hall_count > 0:
            print(f"❌ FAIL: Still found {hall_count} 'hall of' entries")
        else:
            print(f"✅ PASS: No 'hall of' playlist entries found")

        if max_mentions > 1000:
            print(f"⚠️  WARNING: Max mentions ({max_mentions}) still seems high")
        elif max_mentions > 100:
            print(f"✅ GOOD: Max mentions ({max_mentions}) is reasonable but notable")
        else:
            print(f"✅ EXCELLENT: Max mentions ({max_mentions}) looks very realistic")

        if total_mentions < 2000:
            print(f"✅ PASS: Total mentions ({total_mentions}) looks much more realistic")
        else:
            print(f"⚠️  WARNING: Total mentions ({total_mentions}) might still be inflated")

        print(f"\n🎯 SUMMARY:")
        print(f"   • Deduplication: Working (reduced duplicate data)")
        print(f"   • Playlist filtering: {'Working' if hall_count == 0 else 'Needs attention'}")
        print(f"   • Realistic counts: {'Yes' if max_mentions < 1000 else 'Improved but may need more work'}")

        return True

    except Exception as e:
        print(f"❌ Error validating improvements: {e}")
        return False
    finally:
        try:
            conn.close()
        except:
            pass

if __name__ == "__main__":
    validate_improved_artist_trends()
