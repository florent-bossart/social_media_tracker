#!/usr/bin/env python3
"""
Essential Database Migration Script
Copy only the essential tables needed for the dashboard to work.

This is a lighter version that focuses on the key analytics tables
required for the Streamlit dashboard functionality.
"""

import os
import sys
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_local_connection_string():
    """Get local database connection string."""
    password = os.getenv('DBT_DB_PASSWORD', 'bossart')
    return f"postgresql://dbt:{password}@localhost:5432/social_db"

def get_supabase_connection_string():
    """Get Supabase database connection string."""
    host = os.getenv('ONLINE_DB_HOST')
    password = os.getenv('ONLINE_DB_PASSWORD')
    
    if not host or not password:
        raise ValueError("Missing Supabase credentials. Check ONLINE_DB_HOST and ONLINE_DB_PASSWORD")
    
    return f"postgresql://postgres:{password}@{host}:5432/postgres"

def migrate_essential_tables():
    """Migrate only the essential analytics tables needed for the dashboard."""
    
    # Essential tables for dashboard functionality
    essential_tables = [
        'analytics.trend_summary_overview',
        'analytics.trend_summary_top_artists', 
        'analytics.trend_summary_top_genres',
        'analytics.trend_summary_engagement_levels',
        'analytics.trend_summary_sentiment_patterns',
        'analytics.temporal_trends',
        'analytics.genre_trends',
        'analytics.artist_trends'
    ]
    
    print("🚀 Starting essential database migration...")
    print(f"📋 Will migrate {len(essential_tables)} essential tables")
    
    try:
        # Connect to databases
        local_engine = create_engine(get_local_connection_string())
        supabase_engine = create_engine(get_supabase_connection_string())
        
        # Test connections
        with local_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✓ Connected to local database")
        
        with supabase_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✓ Connected to Supabase")
        
        # Create analytics schema
        with supabase_engine.connect() as conn:
            conn.execute(text("CREATE SCHEMA IF NOT EXISTS analytics"))
            conn.commit()
        print("✓ Analytics schema created")
        
        # Migrate each table
        for table_name in essential_tables:
            print(f"\n📦 Migrating {table_name}...")
            
            # Read data from local database
            with local_engine.connect() as conn:
                try:
                    df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
                    row_count = len(df)
                    
                    if row_count == 0:
                        print(f"⚠ Table {table_name} is empty, skipping...")
                        continue
                        
                    print(f"📊 Found {row_count:,} rows")
                    
                except Exception as e:
                    print(f"✗ Error reading {table_name}: {e}")
                    continue
            
            # Write to Supabase
            try:
                schema, table = table_name.split('.')
                df.to_sql(
                    table,
                    supabase_engine,
                    schema=schema,
                    if_exists='replace',  # Replace existing table
                    index=False,
                    method='multi'
                )
                print(f"✓ Successfully migrated {row_count:,} rows")
                
            except Exception as e:
                print(f"✗ Error writing to Supabase: {e}")
                continue
        
        print(f"\n🎉 Essential migration completed!")
        print(f"🚀 Your dashboard should now work with Supabase!")
        
        return True
        
    except Exception as e:
        print(f"💥 Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = migrate_essential_tables()
    
    if success:
        print("\n✅ Next steps:")
        print("1. Deploy your updated streamlit_app.py to Streamlit Cloud")
        print("2. Update your Streamlit Cloud secrets with Supabase credentials")
        print("3. Test the dashboard!")
    else:
        print("\n❌ Migration failed. Please check the errors above.")
    
    sys.exit(0 if success else 1)
