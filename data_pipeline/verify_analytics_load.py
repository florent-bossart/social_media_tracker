#!/usr/bin/env python3
"""
Verify analytics data load.
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

def main():
    # Load environment variables
    load_dotenv()

    # Connect to database
    PG_USER = os.getenv('WAREHOUSE_USER')
    PG_PW = os.getenv('WAREHOUSE_PASSWORD') 
    PG_HOST = os.getenv('WAREHOUSE_HOST', 'localhost')
    PG_PORT = os.getenv('WAREHOUSE_PORT', '5432')
    PG_DB = os.getenv('WAREHOUSE_DB')

    DATABASE_URL = f'postgresql+psycopg2://{PG_USER}:{PG_PW}@{PG_HOST}:{PG_PORT}/{PG_DB}'

    try:
        engine = create_engine(DATABASE_URL)
        
        # Check row counts in analytics tables
        tables = [
            'entity_extraction', 
            'sentiment_analysis', 
            'artist_trends', 
            'genre_trends', 
            'temporal_trends',
            'trend_summary_overview',
            'trend_summary_top_artists',
            'insights_summary_overview',
            'summarization_metrics',
            'wordcloud_data'
        ]
        
        with engine.connect() as conn:
            print('Analytics Data Load Verification:')
            print('=' * 50)
            
            for table in tables:
                try:
                    result = conn.execute(text(f'SELECT COUNT(*) FROM analytics.{table}'))
                    count = result.scalar() 
                    print(f'{table:25s}: {count:>8,} rows')
                except Exception as e:
                    print(f'{table:25s}: ERROR - {str(e)[:50]}')
            
            print('=' * 50)
            print('Verification complete')
            
    except Exception as e:
        print(f'Database connection error: {e}')
        exit(1)

if __name__ == '__main__':
    main()
