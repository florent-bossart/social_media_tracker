#!/usr/bin/env python3
"""
Simple database test to debug connection issues
"""

import os
import sys
import psycopg2
from sqlalchemy import create_engine, text

# Set environment explicitly
os.environ.update({
    'WAREHOUSE_HOST': 'localhost',
    'WAREHOUSE_PORT': '5434',
    'WAREHOUSE_DB': 'social_db',
    'WAREHOUSE_USER': 'dbt',
    'WAREHOUSE_PASSWORD': 'bossart'
})

print("🔧 Testing database connection...")

# Test 1: Direct psycopg2 connection
try:
    print("Test 1: Direct psycopg2 connection")
    conn = psycopg2.connect(
        host='localhost',
        port=5434,
        database='social_db',
        user='dbt',
        password='bossart',
        connect_timeout=5
    )
    cur = conn.cursor()
    cur.execute('SELECT version();')
    version = cur.fetchone()[0]
    print(f"✅ psycopg2 connection successful: {version[:50]}...")
    conn.close()
except Exception as e:
    print(f"❌ psycopg2 connection failed: {e}")

# Test 2: SQLAlchemy connection
try:
    print("\nTest 2: SQLAlchemy connection")
    DATABASE_URL = f"postgresql+psycopg2://dbt:bossart@localhost:5434/social_db"
    engine = create_engine(DATABASE_URL, echo=False)

    with engine.connect() as conn:
        result = conn.execute(text('SELECT 1 as test;'))
        test_val = result.fetchone()[0]
        print(f"✅ SQLAlchemy connection successful: test={test_val}")

except Exception as e:
    print(f"❌ SQLAlchemy connection failed: {e}")

# Test 3: Check analytics schema
try:
    print("\nTest 3: Analytics schema check")
    with engine.connect() as conn:
        result = conn.execute(text("SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'analytics';"))
        schema = result.fetchone()
        if schema:
            print(f"✅ Analytics schema exists: {schema[0]}")

            # List tables
            result = conn.execute(text("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'analytics'
                ORDER BY table_name;
            """))
            tables = [row[0] for row in result.fetchall()]
            print(f"✅ Analytics tables: {tables}")

            # Count records in each table
            for table in tables:
                try:
                    result = conn.execute(text(f'SELECT COUNT(*) FROM analytics.{table};'))
                    count = result.fetchone()[0]
                    print(f"   {table}: {count} records")
                except Exception as e:
                    print(f"   {table}: Error - {e}")
        else:
            print("❌ Analytics schema does not exist")

except Exception as e:
    print(f"❌ Schema check failed: {e}")

print("\n✅ Database test completed")
