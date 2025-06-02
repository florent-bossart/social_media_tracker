#!/usr/bin/env python3
"""
Debug Data Issues - Comprehensive analysis of the entity extraction data
"""

import pandas as pd
import psycopg2
from pathlib import Path
import json
from collections import Counter
import sys

# Database connection
def get_db_connection():
    return psycopg2.connect(
        host="localhost",
        database="social_db",
        user="dbt",
        password="bossart",
        port="5434"
    )

def analyze_csv_data():
    """Analyze the CSV file directly to understand the data issues"""
    csv_path = Path("/home/florent.bossart/code/florent-bossart/social_media_tracker/data/intermediate/entity_extraction/20250529_reddit_entities.csv")

    print("=== CSV FILE ANALYSIS ===")

    if not csv_path.exists():
        print(f"CSV file not found at {csv_path}")
        return

    df = pd.read_csv(csv_path)
    print(f"Total rows in CSV: {len(df)}")

    # Check for duplicates
    print(f"Unique original_text entries: {df['original_text'].nunique()}")
    print(f"Duplicate rate: {((len(df) - df['original_text'].nunique()) / len(df)) * 100:.2f}%")

    # Look for "hall of" entries
    hall_of_artists = []
    for idx, row in df.iterrows():
        if pd.notna(row['entities_artists']):
            try:
                artists = json.loads(row['entities_artists'])
                for artist in artists:
                    if 'hall of' in artist.lower():
                        hall_of_artists.append(artist)
            except:
                continue

    print(f"\n'Hall of...' artists found: {len(hall_of_artists)}")
    hall_counter = Counter(hall_of_artists)
    for artist, count in hall_counter.most_common(10):
        print(f"  {artist}: {count} times")

    # Check Babymetal specifically
    babymetal_rows = []
    for idx, row in df.iterrows():
        if pd.notna(row['entities_artists']):
            try:
                artists = json.loads(row['entities_artists'])
                for artist in artists:
                    if 'babymetal' in artist.lower():
                        babymetal_rows.append({
                            'id': row['id'],
                            'original_text': row['original_text'][:100] + "...",
                            'artist': artist,
                            'source_date': row['source_date']
                        })
            except:
                continue

    print(f"\nBabymetal mentions in CSV: {len(babymetal_rows)}")

    # Check for exact duplicates
    duplicate_mask = df.duplicated(subset=['original_text', 'source_platform'], keep=False)
    duplicates = df[duplicate_mask]
    print(f"\nExact duplicates (same text + platform): {len(duplicates)} rows")

def analyze_database_data():
    """Analyze the database data to see what's actually in there"""
    print("\n=== DATABASE ANALYSIS ===")

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Total rows
        cursor.execute("SELECT COUNT(*) FROM analytics.entity_extraction")
        total_rows = cursor.fetchone()[0]
        print(f"Total rows in database: {total_rows}")

        # Unique texts
        cursor.execute("SELECT COUNT(DISTINCT original_text) FROM analytics.entity_extraction")
        unique_texts = cursor.fetchone()[0]
        print(f"Unique texts in database: {unique_texts}")
        print(f"Database duplicate rate: {((total_rows - unique_texts) / total_rows) * 100:.2f}%")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"Database analysis failed: {e}")

def test_current_dashboard_query():
    """Test the current dashboard query to see what it returns"""
    print("\n=== DASHBOARD QUERY TEST ===")

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Test simple query first
        query = """
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

        cursor.execute(query)
        results = cursor.fetchall()

        print("Top 10 artists (raw count):")
        for artist, mentions in results:
            print(f"  {artist}: {mentions} mentions")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"Dashboard query test failed: {e}")

def main():
    print("Starting comprehensive data analysis...")
    analyze_csv_data()
    analyze_database_data()
    test_current_dashboard_query()
    print("\nAnalysis complete!")

if __name__ == "__main__":
    main()
