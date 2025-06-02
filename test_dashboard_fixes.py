#!/usr/bin/env python3
"""
Test Dashboard Fix - Detailed testing of the dashboard query improvements
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

def test_queries():
    """Test different versions of the query to see the improvements"""

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        print("=== TESTING DASHBOARD QUERIES ===\n")

        # 1. Original problematic query (no deduplication)
        print("1. ORIGINAL QUERY (no deduplication):")
        query1 = """
        SELECT
            jsonb_array_elements_text(entities_artists) as artist_name,
            COUNT(*) as mention_count
        FROM analytics.entity_extraction
        WHERE entities_artists IS NOT NULL
        AND jsonb_array_length(entities_artists) > 0
        GROUP BY jsonb_array_elements_text(entities_artists)
        ORDER BY mention_count DESC
        LIMIT 10
        """

        cursor.execute(query1)
        results1 = cursor.fetchall()
        for artist, mentions in results1:
            print(f"  {artist}: {mentions} mentions")

        # 2. With deduplication only
        print("\n2. WITH DEDUPLICATION ONLY:")
        query2 = """
        WITH deduplicated_data AS (
            SELECT DISTINCT ON (original_text, source_platform)
                original_text,
                source_platform,
                entities_artists
            FROM analytics.entity_extraction
            WHERE entities_artists IS NOT NULL
            AND jsonb_array_length(entities_artists) > 0
        )
        SELECT
            jsonb_array_elements_text(entities_artists) as artist_name,
            COUNT(*) as mention_count
        FROM deduplicated_data
        GROUP BY jsonb_array_elements_text(entities_artists)
        ORDER BY mention_count DESC
        LIMIT 10
        """

        cursor.execute(query2)
        results2 = cursor.fetchall()
        for artist, mentions in results2:
            print(f"  {artist}: {mentions} mentions")

        # 3. With deduplication + filters (current dashboard) - FIXED VERSION
        print("\n3. WITH DEDUPLICATION + FILTERS (current dashboard - FIXED):")
        query3 = """
        WITH deduplicated_data AS (
            SELECT DISTINCT ON (original_text, source_platform)
                original_text,
                source_platform,
                entities_artists,
                confidence_score
            FROM analytics.entity_extraction ee
            WHERE entities_artists IS NOT NULL
            AND jsonb_array_length(entities_artists) > 0
        ),
        artist_stats AS (
            SELECT
                jsonb_array_elements_text(entities_artists) as artist_name,
                COUNT(*) as mention_count,
                AVG(confidence_score) as avg_confidence
            FROM deduplicated_data
            GROUP BY jsonb_array_elements_text(entities_artists)
            HAVING COUNT(*) >= 3
        ),
        filtered_artists AS (
            SELECT *
            FROM artist_stats
            WHERE artist_name NOT ILIKE 'hall of%'
            AND artist_name NOT ILIKE '%playlist%'
            AND LENGTH(artist_name) > 2
        )
        SELECT
            artist_name,
            mention_count,
            avg_confidence
        FROM filtered_artists
        ORDER BY mention_count DESC
        LIMIT 10
        """

        cursor.execute(query3)
        results3 = cursor.fetchall()
        for artist, mentions, confidence in results3:
            print(f"  {artist}: {mentions} mentions (confidence: {confidence:.3f})")

        # 4. Check what we're filtering out
        print("\n4. WHAT'S BEING FILTERED OUT:")

        # Hall of entries
        cursor.execute("""
        WITH deduplicated_data AS (
            SELECT DISTINCT ON (original_text, source_platform)
                original_text,
                source_platform,
                entities_artists
            FROM analytics.entity_extraction
            WHERE entities_artists IS NOT NULL
            AND jsonb_array_length(entities_artists) > 0
        ),
        all_artists AS (
            SELECT
                jsonb_array_elements_text(entities_artists) as artist_name,
                COUNT(*) as mention_count
            FROM deduplicated_data
            GROUP BY jsonb_array_elements_text(entities_artists)
        )
        SELECT artist_name, mention_count
        FROM all_artists
        WHERE artist_name ILIKE 'hall of%'
        ORDER BY mention_count DESC
        """)

        hall_results = cursor.fetchall()
        print("  'Hall of...' entries filtered out:")
        for artist, count in hall_results:
            print(f"    {artist}: {count} mentions")

        # Playlist entries
        cursor.execute("""
        WITH deduplicated_data AS (
            SELECT DISTINCT ON (original_text, source_platform)
                original_text,
                source_platform,
                entities_artists
            FROM analytics.entity_extraction
            WHERE entities_artists IS NOT NULL
            AND jsonb_array_length(entities_artists) > 0
        ),
        all_artists AS (
            SELECT
                jsonb_array_elements_text(entities_artists) as artist_name,
                COUNT(*) as mention_count
            FROM deduplicated_data
            GROUP BY jsonb_array_elements_text(entities_artists)
        )
        SELECT artist_name, mention_count
        FROM all_artists
        WHERE artist_name ILIKE '%playlist%'
        ORDER BY mention_count DESC
        LIMIT 5
        """)

        playlist_results = cursor.fetchall()
        print("  'Playlist' entries filtered out:")
        for artist, count in playlist_results:
            print(f"    {artist}: {count} mentions")

        # Short names (length <= 2)
        cursor.execute("""
        WITH deduplicated_data AS (
            SELECT DISTINCT ON (original_text, source_platform)
                original_text,
                source_platform,
                entities_artists
            FROM analytics.entity_extraction
            WHERE entities_artists IS NOT NULL
            AND jsonb_array_length(entities_artists) > 0
        ),
        all_artists AS (
            SELECT
                jsonb_array_elements_text(entities_artists) as artist_name,
                COUNT(*) as mention_count
            FROM deduplicated_data
            GROUP BY jsonb_array_elements_text(entities_artists)
        )
        SELECT artist_name, mention_count
        FROM all_artists
        WHERE LENGTH(artist_name) <= 2
        ORDER BY mention_count DESC
        LIMIT 5
        """)

        short_results = cursor.fetchall()
        print("  Short names (≤2 chars) filtered out:")
        for artist, count in short_results:
            print(f"    '{artist}': {count} mentions")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"Query test failed: {e}")

def main():
    test_queries()

if __name__ == "__main__":
    main()
