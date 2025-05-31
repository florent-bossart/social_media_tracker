\
import argparse
import json
import os
import logging
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text, inspect
from sqlalchemy import Table, Column, Integer, String, Float, Date, JSON, MetaData
from sqlalchemy.dialects.postgresql import JSONB
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables from .env file
load_dotenv()

DB_USER = os.getenv("POSTGRES_USER", "dbt")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "dbt")
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "social_db")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

metadata = MetaData()
ANALYTICS_SCHEMA = "analytics"

# Define tables
entity_extraction_table = Table(
    "entity_extraction",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("source_platform", String),
    Column("original_text", String),
    Column("extraction_date", Date),
    Column("confidence_score", Float),
    Column("entities_artists", JSONB),
    Column("entities_artists_count", Integer),
    Column("entities_songs", JSONB),
    Column("entities_songs_count", Integer),
    Column("entities_genres", JSONB),
    Column("entities_genres_count", Integer),
    Column("entities_song_indicators", JSONB),
    Column("entities_song_indicators_count", Integer),
    Column("entities_sentiment_indicators", JSONB),
    Column("entities_sentiment_indicators_count", Integer),
    Column("entities_music_events", JSONB),
    Column("entities_music_events_count", Integer),
    Column("entities_temporal_references", JSONB),
    Column("entities_temporal_references_count", Integer),
    Column("entities_other_entities", JSONB),
    Column("entities_other_entities_count", Integer),
    schema=ANALYTICS_SCHEMA,
)

sentiment_analysis_table = Table(
    "sentiment_analysis",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("source_platform", String),
    Column("original_text", String), # Assuming this might be useful for joining or context
    Column("sentiment_score", Float),
    Column("sentiment_label", String),
    Column("sentiment_reasoning", String),
    Column("artist_sentiment", JSONB),
    Column("genre_sentiment", JSONB),
    Column("overall_sentiment", String), # As per shell script, though might be redundant if score is present
    Column("confidence_score", Float), # Model confidence for the sentiment
    Column("analysis_date", Date),
    schema=ANALYTICS_SCHEMA,
)

# Renamed from 'trend_analysis' in shell script for clarity
artist_trends_table = Table(
    "artist_trends",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("artist_name", String),
    Column("trend_score", Float),
    Column("mention_count", Integer),
    Column("sentiment_trend", Float),
    Column("platforms", JSONB), # Storing as JSONB if it's a list/dict of platforms
    Column("analysis_date", Date),
    schema=ANALYTICS_SCHEMA,
)

# Assuming similar structure for genre_trends, can be adjusted
genre_trends_table = Table(
    "genre_trends",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("genre_name", String),
    Column("trend_score", Float),
    Column("mention_count", Integer),
    Column("sentiment_trend", Float),
    Column("platforms", JSONB),
    Column("analysis_date", Date),
    schema=ANALYTICS_SCHEMA,
)

# Assuming similar structure for temporal_trends, can be adjusted
temporal_trends_table = Table(
    "temporal_trends",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("trend_period", String), # e.g., "2024-W23", "2024-06"
    Column("trend_score", Float),
    Column("mention_count", Integer),
    Column("sentiment_trend", Float),
    Column("topic", String), # e.g. "overall", "specific artist/genre"
    Column("analysis_date", Date),
    schema=ANALYTICS_SCHEMA,
)

# For loading trend_summary.json
trend_summaries_table = Table(
    "trend_summaries",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("summary_content", JSONB),
    Column("analysis_date", Date), # Or a more specific run_id/timestamp
    Column("source_file", String), # To track which file this came from
    schema=ANALYTICS_SCHEMA,
)

summarization_metrics_table = Table(
    "summarization_metrics",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("total_artists", Integer),
    Column("total_mentions", Integer),
    Column("avg_sentiment", Float),
    Column("top_platforms", JSONB),
    Column("analysis_confidence", Float),
    Column("analysis_date", Date),
    schema=ANALYTICS_SCHEMA,
)

# For loading trend_insights_summary.json (or similar name)
insights_summaries_table = Table(
    "insights_summaries",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("summary_title", String), # Optional: if the JSON has a title
    Column("summary_content", JSONB),
    Column("analysis_date", Date),
    Column("source_file", String),
    schema=ANALYTICS_SCHEMA,
)


def get_engine():
    """Creates and returns a SQLAlchemy engine."""
    return create_engine(DATABASE_URL)

def ensure_schema_and_tables(engine):
    """Ensures the analytics schema and all defined tables exist."""
    with engine.connect() as connection:
        # The inspect module is preferred for checking schema existence
        inspector = inspect(engine)
        if ANALYTICS_SCHEMA not in inspector.get_schema_names():
            logging.info(f"Schema '{ANALYTICS_SCHEMA}' not found, creating...")
            # Use text() for executing raw SQL is good practice
            connection.execute(text(f"CREATE SCHEMA {ANALYTICS_SCHEMA}"))
            logging.info(f"Schema '{ANALYTICS_SCHEMA}' created.")
        else:
            logging.info(f"Schema '{ANALYTICS_SCHEMA}' already exists.")
        connection.commit() # Commit schema creation before creating tables

    logging.info("Creating tables if they don't exist...")
    metadata.create_all(engine, checkfirst=True)
    logging.info("Table check/creation complete.")

def truncate_table(engine, table_name_with_schema):
    """Truncates the specified table."""
    try:
        with engine.connect() as connection:
            connection.execute(text(f"TRUNCATE TABLE {table_name_with_schema} RESTART IDENTITY CASCADE"))
            connection.commit()
        logging.info(f"Successfully truncated table {table_name_with_schema}")
    except Exception as e:
        logging.error(f"Error truncating table {table_name_with_schema}: {e}")


def load_csv_to_table(engine, file_path, table_name, target_schema, truncate_before_load=False):
    """Loads data from a CSV file into the specified table."""
    if not Path(file_path).exists():
        logging.warning(f"CSV file not found: {file_path}. Skipping load for table {target_schema}.{table_name}.")
        return

    logging.info(f"Loading CSV data from {file_path} into {target_schema}.{table_name}...")
    df = pd.read_csv(file_path)

    for col in df.columns:
        if 'date' in col.lower():
            try:
                df[col] = pd.to_datetime(df[col], errors='coerce').dt.date
            except Exception as e:
                logging.warning(f"Could not convert column {col} to date in {file_path}: {e}")

    table_name_with_schema = f"{target_schema}.{table_name}"
    if truncate_before_load:
        # Check if table exists before truncating
        inspector = inspect(engine)
        if inspector.has_table(table_name, schema=target_schema):
            truncate_table(engine, table_name_with_schema)
        else:
            logging.info(f"Table {table_name_with_schema} does not exist, skipping truncation.")


    try:
        # Ensure all JSONB columns are correctly formatted as JSON strings before loading
        # This is a common point of failure if pandas infers them as objects/dicts
        # and to_sql tries to pass them in a way the DB driver doesn't like for JSONB.
        tbl_meta = metadata.tables.get(f"{target_schema}.{table_name}")
        if tbl_meta is not None:
            for col in tbl_meta.columns:
                if isinstance(col.type, JSONB) and col.name in df.columns:
                    # Convert non-string, non-null values in JSONB columns to JSON strings
                    df[col.name] = df[col.name].apply(
                        lambda x: json.dumps(x) if x is not None and not isinstance(x, str) else x
                    )

        df.to_sql(table_name, engine, schema=target_schema, if_exists="append", index=False, method='multi')
        logging.info(f"Successfully loaded {len(df)} rows from {file_path} into {target_schema}.{table_name}")
    except Exception as e:
        logging.error(f"Error loading data from {file_path} to {target_schema}.{table_name}: {e}")
        logging.error("DataFrame columns: %s", df.columns.tolist())
        logging.error("DataFrame head:\n%s", df.head().to_string())


def load_json_to_table(engine, file_path, table_name, target_schema, content_column_name, truncate_before_load=False):
    """Loads data from a JSON file into the specified table, placing content in a JSONB column."""
    if not Path(file_path).exists():
        logging.warning(f"JSON file not found: {file_path}. Skipping load for table {target_schema}.{table_name}.")
        return

    logging.info(f"Loading JSON data from {file_path} into {target_schema}.{table_name}...")
    with open(file_path, 'r') as f:
        try:
            json_data = json.load(f)
        except json.JSONDecodeError as e:
            logging.error(f"Invalid JSON in file {file_path}: {e}")
            return

    df_data = {
        content_column_name: [json_data],
        "analysis_date": [pd.Timestamp.now().date()],
        "source_file": [str(Path(file_path).name)]
    }

    df = pd.DataFrame(df_data)

    # Ensure the main content column is treated as a JSON string for to_sql
    if content_column_name in df.columns:
         df[content_column_name] = df[content_column_name].apply(
            lambda x: json.dumps(x) if x is not None and not isinstance(x, str) else x
        )

    if "summary_title" in [c.name for c in metadata.tables[f"{target_schema}.{table_name}"].columns] and isinstance(json_data, dict):
        df["summary_title"] = json_data.get("title", Path(file_path).stem)


    table_name_with_schema = f"{target_schema}.{table_name}"
    if truncate_before_load:
        inspector = inspect(engine)
        if inspector.has_table(table_name, schema=target_schema):
            truncate_table(engine, table_name_with_schema)
        else:
            logging.info(f"Table {table_name_with_schema} does not exist, skipping truncation.")

    try:
        df.to_sql(table_name, engine, schema=target_schema, if_exists="append", index=False, method='multi')
        logging.info(f"Successfully loaded data from {file_path} into {target_schema}.{table_name}")
    except Exception as e:
        logging.error(f"Error loading data from {file_path} to {target_schema}.{table_name}: {e}")
        logging.error("DataFrame columns: %s", df.columns.tolist())
        logging.error("DataFrame head:\n%s", df.head().to_string())


def main():
    parser = argparse.ArgumentParser(description="Load LLM pipeline outputs into PostgreSQL analytics schema.")
    parser.add_argument("--entities-file", type=str, help="Path to the entity extraction CSV file.")
    parser.add_argument("--sentiment-file", type=str, help="Path to the sentiment analysis CSV file.")
    parser.add_argument("--artist-trends-file", type=str, help="Path to the artist trends CSV file.")
    parser.add_argument("--genre-trends-file", type=str, help="Path to the genre trends CSV file.")
    parser.add_argument("--temporal-trends-file", type=str, help="Path to the temporal trends CSV file.")
    parser.add_argument("--trend-summary-json", type=str, help="Path to the trend summary JSON file.")
    parser.add_argument("--summarization-metrics-file", type=str, help="Path to the summarization metrics CSV file.")
    parser.add_argument("--insights-summary-json", type=str, help="Path to the insights summary JSON file.")
    parser.add_argument("--truncate", action="store_true", help="Truncate tables before loading data.")

    args = parser.parse_args()

    engine = get_engine()
    ensure_schema_and_tables(engine)

    if args.entities_file:
        load_csv_to_table(engine, args.entities_file, "entity_extraction", ANALYTICS_SCHEMA, args.truncate)
    if args.sentiment_file:
        load_csv_to_table(engine, args.sentiment_file, "sentiment_analysis", ANALYTICS_SCHEMA, args.truncate)
    if args.artist_trends_file:
        load_csv_to_table(engine, args.artist_trends_file, "artist_trends", ANALYTICS_SCHEMA, args.truncate)
    if args.genre_trends_file:
        load_csv_to_table(engine, args.genre_trends_file, "genre_trends", ANALYTICS_SCHEMA, args.truncate)
    if args.temporal_trends_file:
        load_csv_to_table(engine, args.temporal_trends_file, "temporal_trends", ANALYTICS_SCHEMA, args.truncate)

    if args.trend_summary_json:
        load_json_to_table(engine, args.trend_summary_json, "trend_summaries", ANALYTICS_SCHEMA, "summary_content", args.truncate)
    if args.summarization_metrics_file:
        load_csv_to_table(engine, args.summarization_metrics_file, "summarization_metrics", ANALYTICS_SCHEMA, args.truncate)
    if args.insights_summary_json:
        load_json_to_table(engine, args.insights_summary_json, "insights_summaries", ANALYTICS_SCHEMA, "summary_content", args.truncate)

    logging.info("Data loading process finished.")

if __name__ == "__main__":
    main()
