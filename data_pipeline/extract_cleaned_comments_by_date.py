import os
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from datetime import datetime
import argparse
import sys

"""
Extract cleaned comments from Reddit and YouTube with date filtering support.
All text fields in CSV output are properly quoted with double quotes to handle
special characters, commas, and newlines in comment text.
"""

# Load environment variables from .env file for local development
load_dotenv()

PG_USER = os.getenv("WAREHOUSE_USER")
PG_PW = os.getenv("WAREHOUSE_PASSWORD")
PG_HOST = 'localhost'   # for local test only
PG_PORT = "5434"         # for local test only
# PG_HOST = os.getenv("WAREHOUSE_HOST")
# PG_PORT = os.getenv("WAREHOUSE_PORT", "5432")
PG_DB = os.getenv("WAREHOUSE_DB")

DATABASE_URL = f"postgresql+psycopg2://{PG_USER}:{PG_PW}@{PG_HOST}:{PG_PORT}/{PG_DB}"

# Debug: Print environment variables (without password)
print(f"DEBUG: WAREHOUSE_USER = {PG_USER}")
print(f"DEBUG: WAREHOUSE_DB = {PG_DB}")
print(f"DEBUG: PG_HOST = {PG_HOST}")
print(f"DEBUG: PG_PORT = {PG_PORT}")

if not PG_USER or not PG_PW or not PG_DB:
    print("❌ Error: Missing required environment variables!")
    print("Required variables: WAREHOUSE_USER, WAREHOUSE_PASSWORD, WAREHOUSE_DB")
    sys.exit(1)

engine = create_engine(DATABASE_URL)

def extract_to_csv(sql, outfile, filter_date=None):
    extraction_date = datetime.now().strftime("%Y%m%d")
    output_dir = "data/intermediate/Cleaned_data"
    os.makedirs(output_dir, exist_ok=True)

    # Include filter date in filename if provided
    if filter_date:
        filename = f"{extraction_date}_{filter_date}_{outfile}"
    else:
        filename = f"{extraction_date}_{outfile}"

    output_path = os.path.join(output_dir, filename)
    print(f"Database URL: {DATABASE_URL}")

    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print(f"Connection test: {result.fetchone()}")
        df = pd.read_sql(sql, conn)

    df.to_csv(output_path, index=False, quoting=1, quotechar='"')  # quoting=1 means QUOTE_ALL
    print(f"Wrote {len(df)} rows to {output_path}")
    return output_path

def extract_reddit_comments(filter_date=None):
    """Extract cleaned Reddit comments, optionally filtered by date"""
    if filter_date:
        reddit_sql = """
        SELECT
            comment_id, post_id, author_clean, body_clean, created_utc_fmt, fetch_date_fmt
        FROM intermediate.cleaned_reddit_comments
        WHERE fetch_date_fmt >= %s
        ORDER BY fetch_date_fmt DESC
        """
        print(f"Extracting Reddit comments with fetch_date_fmt >= {filter_date}")

        with engine.connect() as conn:
            df = pd.read_sql(reddit_sql, conn, params=[filter_date])
    else:
        reddit_sql = """
        SELECT
            comment_id, post_id, author_clean, body_clean, created_utc_fmt, fetch_date_fmt
        FROM intermediate.cleaned_reddit_comments
        ORDER BY fetch_date_fmt DESC
        """
        print("Extracting all Reddit comments")

        with engine.connect() as conn:
            df = pd.read_sql(reddit_sql, conn)

    # Save to CSV
    extraction_date = datetime.now().strftime("%Y%m%d")
    output_dir = "data/intermediate/Cleaned_data"
    os.makedirs(output_dir, exist_ok=True)

    if filter_date:
        filename = f"{extraction_date}_{filter_date}_reddit_comments_cleaned.csv"
    else:
        filename = f"{extraction_date}_reddit_comments_cleaned.csv"

    output_path = os.path.join(output_dir, filename)
    df.to_csv(output_path, index=False, quoting=1, quotechar='"')  # quoting=1 means QUOTE_ALL
    print(f"Wrote {len(df)} Reddit comments to {output_path}")
    return output_path

def extract_youtube_comments(filter_date=None):
    """Extract cleaned YouTube comments, optionally filtered by date"""
    if filter_date:
        youtube_sql = """
        SELECT
            comment_pk, video_id, comment_id, text_clean, author_clean, published_at, keyword_clean, fetch_date
        FROM intermediate.cleaned_youtube_comments
        WHERE fetch_date >= %s
        ORDER BY fetch_date DESC
        """
        print(f"Extracting YouTube comments with fetch_date >= {filter_date}")

        with engine.connect() as conn:
            df = pd.read_sql(youtube_sql, conn, params=[filter_date])
    else:
        youtube_sql = """
        SELECT
            comment_pk, video_id, comment_id, text_clean, author_clean, published_at, keyword_clean, fetch_date
        FROM intermediate.cleaned_youtube_comments
        ORDER BY fetch_date DESC
        """
        print("Extracting all YouTube comments")

        with engine.connect() as conn:
            df = pd.read_sql(youtube_sql, conn)

    # Save to CSV
    extraction_date = datetime.now().strftime("%Y%m%d")
    output_dir = "data/intermediate/Cleaned_data"
    os.makedirs(output_dir, exist_ok=True)

    if filter_date:
        filename = f"{extraction_date}_{filter_date}_youtube_comments_cleaned.csv"
    else:
        filename = f"{extraction_date}_youtube_comments_cleaned.csv"

    output_path = os.path.join(output_dir, filename)
    df.to_csv(output_path, index=False, quoting=1, quotechar='"')  # quoting=1 means QUOTE_ALL
    print(f"Wrote {len(df)} YouTube comments to {output_path}")
    return output_path

def validate_date_format(date_string):
    """Validate that the date string is in YYYY-MM-DD format"""
    try:
        datetime.strptime(date_string, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def main():
    parser = argparse.ArgumentParser(
        description='Extract cleaned comments from Reddit and YouTube, optionally filtered by date'
    )
    parser.add_argument(
        '--date',
        type=str,
        help='Filter date in YYYY-MM-DD format. Extract comments with fetch date >= this date',
        required=False
    )
    parser.add_argument(
        '--source',
        type=str,
        choices=['reddit', 'youtube', 'both'],
        default='both',
        help='Source to extract from: reddit, youtube, or both (default: both)'
    )

    args = parser.parse_args()

    # Validate date format if provided
    if args.date and not validate_date_format(args.date):
        print(f"Error: Date must be in YYYY-MM-DD format. Got: {args.date}")
        sys.exit(1)

    filter_date = args.date

    try:
        if args.source in ['reddit', 'both']:
            reddit_output = extract_reddit_comments(filter_date)
            print(f"✅ Reddit extraction completed: {reddit_output}")

        if args.source in ['youtube', 'both']:
            youtube_output = extract_youtube_comments(filter_date)
            print(f"✅ YouTube extraction completed: {youtube_output}")

        print("🎉 All extractions completed successfully!")

    except Exception as e:
        print(f"❌ Error during extraction: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
