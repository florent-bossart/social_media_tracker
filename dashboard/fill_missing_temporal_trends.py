#!/usr/bin/env python3
"""
Fill Missing Temporal Trends Data

This script checks the temporal_trends table in the database, identifies missing days in June 2025,
and generates realistic data based on existing patterns to fill the gaps.
"""

import os
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import json
import random
from datetime import datetime, timedelta
import numpy as np

# Load environment variables
load_dotenv()

# Database connection
PG_USER = os.getenv('WAREHOUSE_USER')
PG_PW = os.getenv('WAREHOUSE_PASSWORD')
PG_HOST = os.getenv('WAREHOUSE_HOST', 'localhost')
PG_PORT = os.getenv('WAREHOUSE_PORT', '5432')
PG_DB = os.getenv('WAREHOUSE_DB')

DATABASE_URL = f'postgresql+psycopg2://{PG_USER}:{PG_PW}@{PG_HOST}:{PG_PORT}/{PG_DB}'

def analyze_existing_data():
    """Analyze existing temporal trends data to understand patterns."""
    
    engine = create_engine(DATABASE_URL)
    
    # Get existing temporal trends data
    query = """
    SELECT 
        time_period,
        dominant_artists,
        dominant_genres,
        sentiment_shift,
        engagement_pattern,
        notable_events
    FROM analytics.temporal_trends
    WHERE time_period >= '2025-06-01' AND time_period <= '2025-06-30'
    ORDER BY time_period
    """
    
    df = pd.read_sql(query, engine)
    
    print("Existing temporal trends data for June 2025:")
    print(df)
    print(f"\nTotal records: {len(df)}")
    
    if len(df) > 0:
        print(f"Date range: {df['time_period'].min()} to {df['time_period'].max()}")
        
        # Analyze patterns
        all_artists = []
        all_genres = []
        sentiment_values = []
        engagement_patterns = []
        
        for _, row in df.iterrows():
            try:
                # Handle None values
                artists_str = row['dominant_artists']
                genres_str = row['dominant_genres']
                
                if artists_str and artists_str != 'None':
                    artists = json.loads(artists_str.replace("'", '"'))
                    all_artists.extend([a for a in artists if a != 'nan' and a is not None])
                
                if genres_str and genres_str != 'None':
                    genres = json.loads(genres_str.replace("'", '"'))
                    all_genres.extend([g for g in genres if g != 'nan' and g is not None])
                
                sentiment_values.append(row['sentiment_shift'])
                engagement_patterns.append(row['engagement_pattern'])
                
            except Exception as e:
                print(f"Error parsing row: {e}")
                # Still collect basic values even if JSON parsing fails
                sentiment_values.append(row['sentiment_shift'])
                engagement_patterns.append(row['engagement_pattern'])
                continue
        
        # Get unique values for pattern generation
        unique_artists = list(set(all_artists))
        unique_genres = list(set(all_genres))
        unique_engagement = list(set(engagement_patterns))
        
        print(f"\nPattern Analysis:")
        print(f"Unique artists: {unique_artists}")
        print(f"Unique genres: {unique_genres}")
        if sentiment_values:
            print(f"Sentiment range: {min(sentiment_values)} to {max(sentiment_values)}")
        else:
            print(f"Sentiment range: No data")
        print(f"Engagement patterns: {unique_engagement}")
        
        return df, unique_artists, unique_genres, sentiment_values, unique_engagement
    
    return df, [], [], [], []

def update_existing_null_data(existing_df, artists_pool, genres_pool, sentiment_values, engagement_patterns):
    """Update existing records that have null/None data."""
    
    # Default values if no existing data
    if not artists_pool:
        artists_pool = ['Babymetal', 'Perfume', 'ONE OK ROCK', 'Kyary Pamyu Pamyu', 'AKB48', 'Arashi']
    if not genres_pool:
        genres_pool = ['J-pop', 'rock', 'metal', 'electronic', 'pop']
    if not sentiment_values:
        sentiment_values = [0.0, 0.1, -0.1, 0.2, -0.2]
    if not engagement_patterns:
        engagement_patterns = ['high', 'medium', 'low']
    
    update_data = []
    
    for _, row in existing_df.iterrows():
        if row['dominant_artists'] is None or row['dominant_genres'] is None:
            # Generate new data for this existing record
            selected_artists = random.sample(artists_pool, min(3, len(artists_pool)))
            selected_genres = random.sample(genres_pool, min(3, len(genres_pool)))
            
            # Keep existing sentiment if it exists and is reasonable, otherwise generate new
            sentiment = row['sentiment_shift']
            if sentiment is None or pd.isna(sentiment):
                sentiment = round(random.choice(sentiment_values) + random.uniform(-0.1, 0.1), 2)
            
            # Keep existing engagement if it exists, otherwise use most common
            engagement = row['engagement_pattern']
            if engagement is None or pd.isna(engagement):
                engagement = random.choice(engagement_patterns)
            
            update_data.append({
                'time_period': row['time_period'],
                'dominant_artists': json.dumps(selected_artists),
                'dominant_genres': json.dumps(selected_genres),
                'sentiment_shift': sentiment,
                'engagement_pattern': engagement,
                'notable_events': '[]'
            })
    
    return update_data

def generate_missing_days(existing_df, artists_pool, genres_pool, sentiment_values, engagement_patterns):
    """Generate data for missing days in June 2025."""
    
    # Create full range of June 2025 dates
    start_date = datetime(2025, 6, 1)
    end_date = datetime(2025, 6, 22)  # Up to current date
    
    all_dates = []
    current_date = start_date
    while current_date <= end_date:
        all_dates.append(current_date.strftime('%Y-%m-%d'))
        current_date += timedelta(days=1)
    
    # Find missing dates
    existing_dates = existing_df['time_period'].astype(str).tolist()
    missing_dates = [date for date in all_dates if date not in existing_dates]
    
    print(f"\nMissing dates: {missing_dates}")
    
    if not missing_dates:
        print("No missing dates found!")
        return []
    
    # Default values if no existing data
    if not artists_pool:
        artists_pool = ['Babymetal', 'Perfume', 'ONE OK ROCK', 'Kyary Pamyu Pamyu', 'AKB48', 'Arashi']
    if not genres_pool:
        genres_pool = ['J-pop', 'rock', 'metal', 'electronic', 'pop']
    if not sentiment_values:
        sentiment_values = [0.0, 0.1, -0.1, 0.2, -0.2]
    if not engagement_patterns:
        engagement_patterns = ['high', 'medium', 'low']
    
    # Generate data for missing dates
    missing_data = []
    
    for date in missing_dates:
        # Randomly select 2-3 artists and genres
        selected_artists = random.sample(artists_pool, min(3, len(artists_pool)))
        selected_genres = random.sample(genres_pool, min(3, len(genres_pool)))
        
        # Random sentiment shift (based on existing pattern)
        sentiment = round(random.choice(sentiment_values) + random.uniform(-0.1, 0.1), 2)
        
        # Random engagement pattern
        engagement = random.choice(engagement_patterns)
        
        missing_data.append({
            'time_period': date,
            'dominant_artists': json.dumps(selected_artists),
            'dominant_genres': json.dumps(selected_genres),
            'sentiment_shift': sentiment,
            'engagement_pattern': engagement,
            'notable_events': '[]'
        })
    
    return missing_data

def update_existing_records(update_data):
    """Update existing records with null data."""
    
    if not update_data:
        print("No existing records to update.")
        return
    
    engine = create_engine(DATABASE_URL)
    
    with engine.begin() as conn:
        for data in update_data:
            update_query = text("""
            UPDATE analytics.temporal_trends 
            SET dominant_artists = :dominant_artists,
                dominant_genres = :dominant_genres,
                sentiment_shift = :sentiment_shift,
                engagement_pattern = :engagement_pattern,
                notable_events = :notable_events
            WHERE time_period = :time_period
            """)
            
            conn.execute(update_query, data)
            print(f"Updated data for {data['time_period']}")
        
        print(f"\nSuccessfully updated {len(update_data)} existing records!")

def insert_missing_data(missing_data):
    """Insert missing data into the database."""
    
    if not missing_data:
        print("No missing data to insert.")
        return
    
    engine = create_engine(DATABASE_URL)
    
    with engine.begin() as conn:
        for data in missing_data:
            insert_query = text("""
            INSERT INTO analytics.temporal_trends 
            (time_period, dominant_artists, dominant_genres, sentiment_shift, engagement_pattern, notable_events)
            VALUES (:time_period, :dominant_artists, :dominant_genres, :sentiment_shift, :engagement_pattern, :notable_events)
            """)
            
            conn.execute(insert_query, data)
            print(f"Inserted data for {data['time_period']}")
        
        print(f"\nSuccessfully inserted {len(missing_data)} missing records!")

def main():
    """Main function to fill missing temporal trends data."""
    
    print("Analyzing existing temporal trends data...")
    
    try:
        # Analyze existing data
        existing_df, artists_pool, genres_pool, sentiment_values, engagement_patterns = analyze_existing_data()
        
        # Check for records with null data that need updating
        update_data = update_existing_null_data(existing_df, artists_pool, genres_pool, sentiment_values, engagement_patterns)
        
        # Generate missing data
        missing_data = generate_missing_days(existing_df, artists_pool, genres_pool, sentiment_values, engagement_patterns)
        
        total_changes = len(update_data) + len(missing_data)
        
        if total_changes > 0:
            print(f"\nFound {len(update_data)} records to update and {len(missing_data)} missing records to insert...")
            
            # Show preview
            if update_data:
                print("\nPreview of records to update:")
                for i, data in enumerate(update_data[:3]):
                    print(f"Update {i+1}. {data['time_period']}: {data['dominant_artists'][:50]}...")
                    
            if missing_data:
                print("\nPreview of records to insert:")
                for i, data in enumerate(missing_data[:3]):
                    print(f"Insert {i+1}. {data['time_period']}: {data['dominant_artists'][:50]}...")
            
            # Ask for confirmation
            response = input(f"\nProcess {total_changes} changes? (y/n): ")
            if response.lower() == 'y':
                if update_data:
                    update_existing_records(update_data)
                if missing_data:
                    insert_missing_data(missing_data)
            else:
                print("Operation cancelled.")
        else:
            print("No changes needed - all dates present with valid data!")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
