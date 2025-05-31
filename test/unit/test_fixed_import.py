#!/usr/bin/env python3
"""
Fixed database import by excluding conflicting ID columns
"""

import os
import sys
import pandas as pd
import json
from sqlalchemy import create_engine, text

# Set environment
os.environ.update({
    'WAREHOUSE_HOST': 'localhost',
    'WAREHOUSE_PORT': '5434',
    'WAREHOUSE_DB': 'social_db',
    'WAREHOUSE_USER': 'dbt',
    'WAREHOUSE_PASSWORD': 'bossart'
})

DATABASE_URL = f"postgresql+psycopg2://dbt:bossart@localhost:5434/social_db"

def safe_json_parse(x):
    """Safely parse JSON strings"""
    if pd.notna(x) and x != '' and x != '[]':
        try:
            return json.dumps(json.loads(x))
        except:
            return json.dumps([])
    return json.dumps([])

print("🔧 Testing fixed database import (excluding ID columns)...")

try:
    # Create engine
    engine = create_engine(DATABASE_URL, echo=False)

    # Test 1: Import entity extraction (exclude id column)
    print("\n📊 Test 1: Entity extraction import")
    csv_file = 'data/intermediate/entity_extraction/quick_test_entities.csv'

    if os.path.exists(csv_file):
        df = pd.read_csv(csv_file)
        print(f"   Original data: {len(df)} records, {len(df.columns)} columns")

        # Drop the 'id' column if it exists to avoid conflicts with auto-increment
        if 'id' in df.columns:
            df = df.drop('id', axis=1)
            print(f"   Dropped 'id' column, now {len(df.columns)} columns")

        # Process JSON columns
        json_columns = [
            'entities_artists', 'entities_songs', 'entities_genres',
            'entities_song_indicators', 'entities_sentiment_indicators',
            'entities_music_events', 'entities_temporal_references',
            'entities_other_entities'
        ]

        for col in json_columns:
            if col in df.columns:
                df[col] = df[col].apply(safe_json_parse)

        # Convert date columns
        if 'extraction_date' in df.columns:
            df['extraction_date'] = pd.to_datetime(df['extraction_date']).dt.date

        print(f"   Final columns: {list(df.columns)}")

        # Import to database
        with engine.begin() as conn:
            df.to_sql('entity_extraction', conn, schema='analytics',
                     if_exists='append', index=False, method='multi')

        print("   ✅ Import successful")

        # Verify data
        with engine.connect() as conn:
            result = conn.execute(text('SELECT COUNT(*) FROM analytics.entity_extraction;'))
            count = result.fetchone()[0]
            print(f"   ✅ Verified: {count} records in database")
    else:
        print(f"   ❌ File not found: {csv_file}")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n✅ Test completed")
