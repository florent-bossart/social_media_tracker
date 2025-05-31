#!/usr/bin/env python3
"""
Minimal database import test - one table at a time
"""

import os
import sys
import pandas as pd
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

print("🔧 Testing minimal database import...")

try:
    # Create engine
    engine = create_engine(DATABASE_URL, echo=False)

    # Test 1: Import entity extraction
    print("\n📊 Test 1: Entity extraction import")
    csv_file = 'data/intermediate/entity_extraction/quick_test_entities.csv'

    if os.path.exists(csv_file):
        df = pd.read_csv(csv_file)
        print(f"   Loaded CSV: {len(df)} records")
        print(f"   Columns: {list(df.columns)}")

        # Import directly to database
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
