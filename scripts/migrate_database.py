#!/usr/bin/env python3
"""
Direct Database Migration Script
Copy data directly from local PostgreSQL to Supabase using Python.

This script connects to both databases and copies data table by table,
handling data types and formatting automatically.
"""

import os
import sys
import pandas as pd
import psycopg2
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.dialects import postgresql
import streamlit as st
from tqdm import tqdm
import time

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

def get_local_engine():
    """Create connection to local PostgreSQL database."""
    
    # Local database configuration (from docker-compose)
    local_config = {
        'host': 'localhost',
        'port': 5432,
        'database': 'social_db',
        'username': 'dbt', 
        'password': os.getenv('DBT_DB_PASSWORD', 'bossart')
    }
    
    connection_string = f"postgresql://{local_config['username']}:{local_config['password']}@{local_config['host']}:{local_config['port']}/{local_config['database']}"
    return create_engine(connection_string)

def get_supabase_engine():
    """Create connection to Supabase PostgreSQL database."""
    
    # Supabase configuration (from environment)
    supabase_config = {
        'host': os.getenv('ONLINE_DB_HOST'),
        'port': int(os.getenv('ONLINE_DB_PORT', 5432)),
        'database': os.getenv('ONLINE_DB_NAME', 'postgres'),
        'username': os.getenv('ONLINE_DB_USER', 'postgres'),
        'password': os.getenv('ONLINE_DB_PASSWORD')
    }
    
    if not all([supabase_config['host'], supabase_config['password']]):
        raise ValueError("Supabase configuration not found. Please set ONLINE_DB_* environment variables.")
    
    connection_string = f"postgresql://{supabase_config['username']}:{supabase_config['password']}@{supabase_config['host']}:{supabase_config['port']}/{supabase_config['database']}"
    return create_engine(connection_string)

def create_schemas_on_supabase(supabase_engine):
    """Create necessary schemas on Supabase."""
    
    schemas_to_create = ['raw', 'intermediate', 'analytics']
    
    with supabase_engine.connect() as conn:
        for schema in schemas_to_create:
            try:
                conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema}"))
                conn.commit()
                print(f"✓ Schema '{schema}' created/verified")
            except Exception as e:
                print(f"⚠ Warning creating schema '{schema}': {e}")

def get_table_list(engine, exclude_dbt_tables=True):
    """Get list of all tables from the database."""
    
    inspector = inspect(engine)
    tables = []
    
    # Get tables from all schemas
    for schema in inspector.get_schema_names():
        if schema in ['information_schema', 'pg_catalog', 'pg_toast']:
            continue
            
        for table in inspector.get_table_names(schema=schema):
            # Skip DBT utility tables
            if exclude_dbt_tables and ('dbt_' in table or table.startswith('my_first_')):
                continue
                
            tables.append(f"{schema}.{table}")
    
    return sorted(tables)

def copy_table_structure(source_engine, target_engine, table_name):
    """Copy table structure from source to target database."""
    
    schema, table = table_name.split('.')
    
    # Get CREATE TABLE statement
    with source_engine.connect() as conn:
        result = conn.execute(text(f"""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_schema = '{schema}' AND table_name = '{table}'
            ORDER BY ordinal_position
        """))
        
        columns = result.fetchall()
    
    if not columns:
        print(f"⚠ No columns found for table {table_name}")
        return False
    
    # Build CREATE TABLE statement
    column_definitions = []
    for col in columns:
        col_name, data_type, is_nullable, default = col
        
        # Handle data type mapping
        col_def = f'"{col_name}" {data_type}'
        
        if is_nullable == 'NO':
            col_def += ' NOT NULL'
            
        if default:
            col_def += f' DEFAULT {default}'
            
        column_definitions.append(col_def)
    
    create_statement = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            {', '.join(column_definitions)}
        )
    """
    
    # Execute CREATE TABLE on target
    try:
        with target_engine.connect() as conn:
            conn.execute(text(create_statement))
            conn.commit()
        print(f"✓ Table structure created: {table_name}")
        return True
    except Exception as e:
        print(f"✗ Error creating table {table_name}: {e}")
        return False

def copy_table_data(source_engine, target_engine, table_name, batch_size=1000):
    """Copy data from source table to target table."""
    
    try:
        # Get row count
        with source_engine.connect() as conn:
            count_result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
            total_rows = count_result.scalar()
        
        if total_rows == 0:
            print(f"⚠ Table {table_name} is empty")
            return True
            
        print(f"📊 Copying {total_rows:,} rows from {table_name}")
        
        # Clear target table first
        with target_engine.connect() as conn:
            conn.execute(text(f"TRUNCATE TABLE {table_name} CASCADE"))
            conn.commit()
        
        # Copy data in batches
        for offset in tqdm(range(0, total_rows, batch_size), desc=f"Copying {table_name}"):
            # Read batch from source
            with source_engine.connect() as conn:
                df = pd.read_sql(
                    text(f"SELECT * FROM {table_name} LIMIT {batch_size} OFFSET {offset}"),
                    conn
                )
            
            if df.empty:
                break
                
            # Write batch to target
            schema, table = table_name.split('.')
            df.to_sql(
                table,
                target_engine,
                schema=schema, 
                if_exists='append',
                index=False,
                method='multi'
            )
        
        print(f"✓ Successfully copied {total_rows:,} rows to {table_name}")
        return True
        
    except Exception as e:
        print(f"✗ Error copying data for {table_name}: {e}")
        return False

def main():
    """Main migration function."""
    
    print("🚀 Starting database migration from local PostgreSQL to Supabase...")
    print()
    
    try:
        # Connect to databases
        print("📡 Connecting to databases...")
        local_engine = get_local_engine() 
        supabase_engine = get_supabase_engine()
        
        # Test connections
        with local_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✓ Connected to local PostgreSQL")
        
        with supabase_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✓ Connected to Supabase")
        print()
        
        # Create schemas
        print("🏗️ Creating schemas on Supabase...")
        create_schemas_on_supabase(supabase_engine)
        print()
        
        # Get table list
        print("📋 Getting table list...")
        tables = get_table_list(local_engine)
        print(f"Found {len(tables)} tables to migrate:")
        for table in tables:
            print(f"  - {table}")
        print()
        
        # Priority tables for dashboard functionality
        priority_tables = [
            'analytics.trend_summary_overview',
            'analytics.trend_summary_top_artists', 
            'analytics.trend_summary_top_genres',
            'analytics.trend_summary_engagement_levels',
            'analytics.trend_summary_sentiment_patterns',
            'analytics.temporal_trends',
            'analytics.genre_trends',
            'analytics.artist_trends'
        ]
        
        # Copy priority tables first
        print("🔥 Copying priority tables first...")
        success_count = 0
        failed_tables = []
        
        for table in priority_tables:
            if table in tables:
                print(f"\n📦 Processing priority table: {table}")
                
                # Copy structure
                if copy_table_structure(local_engine, supabase_engine, table):
                    # Copy data
                    if copy_table_data(local_engine, supabase_engine, table):
                        success_count += 1
                    else:
                        failed_tables.append(table)
                else:
                    failed_tables.append(table)
        
        # Copy remaining tables
        remaining_tables = [t for t in tables if t not in priority_tables]
        
        if remaining_tables:
            print(f"\n📚 Copying remaining {len(remaining_tables)} tables...")
            
            for table in remaining_tables:
                print(f"\n📦 Processing table: {table}")
                
                # Copy structure
                if copy_table_structure(local_engine, supabase_engine, table):
                    # Copy data
                    if copy_table_data(local_engine, supabase_engine, table):
                        success_count += 1
                    else:
                        failed_tables.append(table)
                else:
                    failed_tables.append(table)
        
        # Summary
        print(f"\n🎉 Migration completed!")
        print(f"✓ Successfully migrated: {success_count}/{len(tables)} tables")
        
        if failed_tables:
            print(f"⚠ Failed tables ({len(failed_tables)}):")
            for table in failed_tables:
                print(f"  - {table}")
        
        print("\n🚀 Your dashboard should now work with Supabase!")
        
    except Exception as e:
        print(f"💥 Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    # Install required packages if missing
    try:
        import tqdm
    except ImportError:
        print("Installing tqdm...")
        os.system("pip install tqdm")
        import tqdm
    
    success = main()
    sys.exit(0 if success else 1)
