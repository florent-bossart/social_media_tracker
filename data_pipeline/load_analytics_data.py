import argparse
import json
import os
import logging
from pathlib import Path
from datetime import date

import pandas as pd
from sqlalchemy import create_engine, text, inspect, Table, Column, Integer, String, Float, Date, JSON, MetaData, DateTime, Text, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from dotenv import load_dotenv

# Configure logging with file output
log_file = f"/home/florent.bossart/code/florent-bossart/social_media_tracker/logs/load_analytics_{date.today().strftime('%Y%m%d')}.log"
os.makedirs(os.path.dirname(log_file), exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

# Load environment variables from .env file
load_dotenv()

# Updated environment variables to match your setup
PG_USER = os.getenv("WAREHOUSE_USER")
PG_PW = os.getenv("WAREHOUSE_PASSWORD")
PG_HOST = "localhost"
PG_PORT = "5434"
PG_DB = os.getenv("WAREHOUSE_DB")

DATABASE_URL = f"postgresql+psycopg2://{PG_USER}:{PG_PW}@{PG_HOST}:{PG_PORT}/{PG_DB}"

metadata = MetaData()
ANALYTICS_SCHEMA = "analytics"

# Define tables to match actual CSV structures
entity_extraction_table = Table(
    "entity_extraction",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("source_platform", String),
    Column("original_text", Text),
    Column("extraction_date", Date),
    Column("source_date", DateTime),
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
    Column("original_text", Text),
    Column("analysis_date", Date),
    Column("overall_sentiment", String),
    Column("sentiment_strength", Float),
    Column("confidence_score", Float),
    Column("sentiment_reasoning", Text),
    Column("artist_sentiment", JSONB),
    Column("music_quality_sentiment", String),
    Column("performance_sentiment", String),
    Column("personal_experience_sentiment", String),
    Column("emotional_indicators", JSONB),
    Column("emotional_indicators_count", Integer),
    Column("has_comparison", Boolean),
    Column("comparison_type", String),
    Column("favorable_entities", JSONB),
    Column("unfavorable_entities", JSONB),
    Column("comparison_sentiment", String),
    schema=ANALYTICS_SCHEMA,
)

artist_trends_table = Table(
    "artist_trends",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("entity_type", String),
    Column("entity_name", String),
    Column("mention_count", Integer),
    Column("sentiment_score", Float),
    Column("sentiment_consistency", Float),
    Column("growth_rate", Float),
    Column("engagement_level", String),
    Column("trend_strength", Float),
    Column("trend_direction", String),
    Column("first_seen", Date),
    Column("last_seen", Date),
    Column("platforms", JSONB),
    Column("peak_sentiment", Float),
    Column("sentiment_volatility", Float),
    schema=ANALYTICS_SCHEMA,
)

genre_trends_table = Table(
    "genre_trends",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("genre", String),
    Column("popularity_score", Float),
    Column("sentiment_trend", String),
    Column("artist_diversity", Integer),
    Column("cross_platform_presence", Integer),
    Column("emotional_associations", JSONB),
    Column("trend_momentum", Float),
    schema=ANALYTICS_SCHEMA,
)

temporal_trends_table = Table(
    "temporal_trends",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("time_period", String),
    Column("dominant_artists", JSONB),
    Column("dominant_genres", JSONB),
    Column("sentiment_shift", Float),
    Column("engagement_pattern", String),
    Column("notable_events", JSONB),
    schema=ANALYTICS_SCHEMA,
)

# Flattened trend summary tables
trend_summary_overview_table = Table(
    "trend_summary_overview",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("analysis_timestamp", DateTime),
    Column("total_artists_analyzed", Integer),
    Column("total_genres_analyzed", Integer),
    Column("time_periods_analyzed", Integer),
    Column("min_mentions_for_trend", Integer),
    Column("positive_sentiment_threshold", Float),
    Column("source_file", String),
    schema=ANALYTICS_SCHEMA,
)

trend_summary_top_artists_table = Table(
    "trend_summary_top_artists",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("analysis_timestamp", DateTime),
    Column("artist_name", String),
    Column("trend_strength", Float),
    Column("mentions", Integer),
    Column("sentiment_score", Float),
    Column("sentiment_direction", String),
    Column("platforms", JSONB),
    Column("source_file", String),
    schema=ANALYTICS_SCHEMA,
)

trend_summary_top_genres_table = Table(
    "trend_summary_top_genres",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("analysis_timestamp", DateTime),
    Column("genre_name", String),
    Column("popularity_score", Float),
    Column("sentiment_trend", String),
    Column("artist_diversity", Integer),
    Column("platforms_count", Integer),
    Column("source_file", String),
    schema=ANALYTICS_SCHEMA,
)

trend_summary_sentiment_patterns_table = Table(
    "trend_summary_sentiment_patterns",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("analysis_timestamp", DateTime),
    Column("positive_trends", Integer),
    Column("negative_trends", Integer),
    Column("neutral_trends", Integer),
    Column("source_file", String),
    schema=ANALYTICS_SCHEMA,
)

trend_summary_engagement_levels_table = Table(
    "trend_summary_engagement_levels",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("analysis_timestamp", DateTime),
    Column("high_engagement", Integer),
    Column("medium_engagement", Integer),
    Column("low_engagement", Integer),
    Column("source_file", String),
    schema=ANALYTICS_SCHEMA,
)

# Flattened insights summary tables
insights_summary_overview_table = Table(
    "insights_summary_overview",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("analysis_timestamp", DateTime),
    Column("data_period", DateTime),
    Column("confidence_score", Float),
    Column("executive_summary", Text),
    Column("source_file", String),
    schema=ANALYTICS_SCHEMA,
)

insights_summary_key_findings_table = Table(
    "insights_summary_key_findings",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("analysis_timestamp", DateTime),
    Column("finding_text", Text),
    Column("finding_order", Integer),
    Column("source_file", String),
    schema=ANALYTICS_SCHEMA,
)

insights_summary_artist_insights_table = Table(
    "insights_summary_artist_insights",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("analysis_timestamp", DateTime),
    Column("artist_name", String),
    Column("insight_text", Text),
    Column("source_file", String),
    schema=ANALYTICS_SCHEMA,
)

summarization_metrics_table = Table(
    "summarization_metrics",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("metric", String),
    Column("value", String),
    Column("analysis_date", Date),
    Column("source_file", String),
    schema=ANALYTICS_SCHEMA,
)

wordcloud_data_table = Table(
    "wordcloud_data",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("word", String, nullable=False),
    Column("frequency", Integer, default=1),
    Column("source_platform", String),
    Column("generation_date", Date),
    Column("source_file", String),
    schema=ANALYTICS_SCHEMA,
)


def get_engine():
    """Creates and returns a SQLAlchemy engine."""
    return create_engine(DATABASE_URL)

def ensure_schema_and_tables(engine):
    """Ensures the analytics schema and all defined tables exist."""
    # Check if schema exists using inspector
    inspector = inspect(engine)
    if ANALYTICS_SCHEMA not in inspector.get_schema_names():
        logging.info(f"Schema '{ANALYTICS_SCHEMA}' not found, creating...")
        # Use begin() to create a transaction context for schema creation
        with engine.begin() as connection:
            connection.execute(text(f"CREATE SCHEMA {ANALYTICS_SCHEMA}"))
        logging.info(f"Schema '{ANALYTICS_SCHEMA}' created.")
    else:
        logging.info(f"Schema '{ANALYTICS_SCHEMA}' already exists.")

    logging.info("Creating tables if they don't exist...")
    metadata.create_all(engine, checkfirst=True)
    logging.info("Table check/creation complete.")

def truncate_table(engine, table_name_with_schema):
    """Truncates the specified table."""
    try:
        with engine.begin() as connection:
            connection.execute(text(f"TRUNCATE TABLE {table_name_with_schema} RESTART IDENTITY CASCADE"))
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

    logging.info(f"Loaded DataFrame with {len(df)} rows and columns: {df.columns.tolist()}")

    # Clean up NaN values and empty strings that cause JSON parsing issues
    # Replace NaN values with None for proper null handling
    df = df.where(pd.notnull(df), None)

    # Convert empty strings in JSON columns to None to avoid JSON parsing errors
    json_like_columns = [col for col in df.columns if any(keyword in col.lower() for keyword in ['entities', 'platforms', 'emotional_indicators', 'artist_sentiment', 'favorable_entities', 'unfavorable_entities'])]
    for col in json_like_columns:
        if col in df.columns:
            df[col] = df[col].apply(lambda x: None if (x == '' or x == 'NaN' or pd.isna(x)) else x)

    # Convert known date columns or columns with 'date' in their name
    known_date_columns = ['extraction_date', 'source_date', 'analysis_date', 'first_seen', 'last_seen', 'trend_start_date', 'trend_end_date']

    for col_name in df.columns:
        if col_name in known_date_columns or 'date' in col_name.lower():
            try:
                df[col_name] = pd.to_datetime(df[col_name], errors='coerce').dt.date
            except Exception as e:
                logging.warning(f"Could not convert column {col_name} to date in {file_path}: {e}. Column data type: {df[col_name].dtype}")

    # Add source_file column for tracking if it doesn't exist
    if 'source_file' not in df.columns:
        df['source_file'] = Path(file_path).name

    # For summarization metrics, add analysis_date if not present
    if table_name == "summarization_metrics" and "analysis_date" not in df.columns:
        df["analysis_date"] = date.today()

    table_name_with_schema = f"{target_schema}.{table_name}"
    if truncate_before_load:
        # Check if table exists before truncating
        inspector = inspect(engine)
        if inspector.has_table(table_name, schema=target_schema):
            truncate_table(engine, table_name_with_schema)
        else:
            logging.info(f"Table {table_name_with_schema} does not exist, skipping truncation.")

    try:
        # Get table metadata
        tbl_meta = metadata.tables.get(f"{target_schema}.{table_name}")
        if tbl_meta is not None:
            # Handle JSONB columns - convert to proper JSON strings or None
            for col in tbl_meta.columns:
                if isinstance(col.type, JSONB) and col.name in df.columns:
                    def clean_json_value(x):
                        if x is None or pd.isna(x) or x == '' or x == 'NaN':
                            return None
                        if isinstance(x, str):
                            # If it's already a JSON string, validate it
                            try:
                                json.loads(x)
                                return x
                            except (json.JSONDecodeError, ValueError):
                                # If it's not valid JSON, treat as null
                                return None
                        else:
                            # If it's an object, convert to JSON
                            try:
                                return json.dumps(x)
                            except (TypeError, ValueError):
                                return None

                    df[col.name] = df[col.name].apply(clean_json_value)

            # Filter DataFrame to only include columns that exist in the target table
            expected_columns = [col.name for col in tbl_meta.columns if col.name != 'id']  # Exclude auto-increment id
            available_columns = [col for col in expected_columns if col in df.columns]
            df_filtered = df[available_columns].copy()

            logging.info(f"Filtered to {len(available_columns)} columns: {available_columns}")
        else:
            # If no table metadata found, use all columns except 'id'
            df_filtered = df.drop(columns=['id'], errors='ignore').copy()
            logging.warning(f"No table metadata found for {target_schema}.{table_name}, using all available columns")

        df_filtered.to_sql(table_name, engine, schema=target_schema, if_exists="append", index=False, method='multi')
        logging.info(f"Successfully loaded {len(df_filtered)} rows from {file_path} into {target_schema}.{table_name}")
    except Exception as e:
        logging.error(f"Error loading data from {file_path} to {target_schema}.{table_name}: {e}")
        logging.error("DataFrame columns: %s", df.columns.tolist())
        logging.error("Expected table columns: %s", [col.name for col in tbl_meta.columns] if tbl_meta else "Table not found")
        logging.error("DataFrame head:\n%s", df.head().to_string())


def load_trend_summary_json_to_tables(engine, file_path, target_schema, truncate_before_load=False):
    """Loads flattened trend summary data from a JSON file into multiple tables."""
    if not Path(file_path).exists():
        logging.warning(f"JSON file not found: {file_path}. Skipping load for trend summary tables.")
        return

    logging.info(f"Loading trend summary JSON data from {file_path} into flattened tables...")

    with open(file_path, 'r') as f:
        try:
            json_data = json.load(f)
        except json.JSONDecodeError as e:
            logging.error(f"Invalid JSON in file {file_path}: {e}")
            return

    source_file = str(Path(file_path).name)
    analysis_timestamp = pd.to_datetime(json_data.get("analysis_timestamp", pd.Timestamp.now())).to_pydatetime()

    # Truncate tables if requested
    if truncate_before_load:
        tables_to_truncate = [
            "trend_summary_overview", "trend_summary_top_artists", "trend_summary_top_genres",
            "trend_summary_sentiment_patterns", "trend_summary_engagement_levels"
        ]
        for table_name in tables_to_truncate:
            table_name_with_schema = f"{target_schema}.{table_name}"
            inspector = inspect(engine)
            if inspector.has_table(table_name, schema=target_schema):
                truncate_table(engine, table_name_with_schema)

    try:
        # Load overview data
        overview_data = json_data.get("overview", {})
        config_data = json_data.get("config_summary", {})
        overview_df = pd.DataFrame([{
            "analysis_timestamp": analysis_timestamp,
            "total_artists_analyzed": overview_data.get("total_artists_analyzed"),
            "total_genres_analyzed": overview_data.get("total_genres_analyzed"),
            "time_periods_analyzed": overview_data.get("time_periods_analyzed"),
            "min_mentions_for_trend": config_data.get("min_mentions_for_trend"),
            "positive_sentiment_threshold": config_data.get("positive_sentiment_threshold"),
            "source_file": source_file
        }])
        overview_df.to_sql("trend_summary_overview", engine, schema=target_schema, if_exists="append", index=False)
        logging.info(f"Loaded overview data into {target_schema}.trend_summary_overview")

        # Load top artists data
        top_artists = json_data.get("top_artists", [])
        if top_artists:
            artists_data = []
            for artist in top_artists:
                artists_data.append({
                    "analysis_timestamp": analysis_timestamp,
                    "artist_name": artist.get("name"),
                    "trend_strength": artist.get("trend_strength"),
                    "mentions": artist.get("mentions"),
                    "sentiment_score": artist.get("sentiment_score"),
                    "sentiment_direction": artist.get("sentiment_direction"),
                    "platforms": json.dumps(artist.get("platforms", [])),
                    "source_file": source_file
                })
            artists_df = pd.DataFrame(artists_data)
            artists_df.to_sql("trend_summary_top_artists", engine, schema=target_schema, if_exists="append", index=False)
            logging.info(f"Loaded {len(artists_data)} top artists into {target_schema}.trend_summary_top_artists")

        # Load top genres data
        top_genres = json_data.get("top_genres", [])
        if top_genres:
            genres_data = []
            # Dictionary to aggregate duplicate genres
            genre_aggregation = {}
            
            for genre in top_genres:
                original_name = genre.get("name")
                normalized_name = normalize_genre_name(original_name)
                
                # If we've seen this normalized genre before, aggregate the data
                if normalized_name in genre_aggregation:
                    existing = genre_aggregation[normalized_name]
                    # Sum popularity scores and artist diversity, average sentiment
                    existing["popularity_score"] += genre.get("popularity_score", 0)
                    existing["artist_diversity"] += genre.get("artist_diversity", 0)
                    existing["platforms_count"] = max(existing["platforms_count"], genre.get("platforms_count", 0))
                    # Keep sentiment trend from the genre with higher popularity
                    if genre.get("popularity_score", 0) > existing.get("max_popularity", 0):
                        existing["sentiment_trend"] = genre.get("sentiment_trend")
                        existing["max_popularity"] = genre.get("popularity_score", 0)
                else:
                    # First time seeing this normalized genre
                    genre_aggregation[normalized_name] = {
                        "analysis_timestamp": analysis_timestamp,
                        "genre_name": normalized_name,
                        "popularity_score": genre.get("popularity_score", 0),
                        "sentiment_trend": genre.get("sentiment_trend"),
                        "artist_diversity": genre.get("artist_diversity", 0),
                        "platforms_count": genre.get("platforms_count", 0),
                        "max_popularity": genre.get("popularity_score", 0),
                        "source_file": source_file
                    }
            
            # Convert aggregated data to list, removing helper fields
            for genre_name, genre_data in genre_aggregation.items():
                genre_data.pop("max_popularity", None)  # Remove helper field
                genres_data.append(genre_data)
            
            genres_df = pd.DataFrame(genres_data)
            genres_df.to_sql("trend_summary_top_genres", engine, schema=target_schema, if_exists="append", index=False)
            logging.info(f"Loaded {len(genres_data)} normalized top genres into {target_schema}.trend_summary_top_genres")

        # Load sentiment patterns data
        sentiment_patterns = json_data.get("sentiment_patterns_artists", {})
        if sentiment_patterns:
            sentiment_df = pd.DataFrame([{
                "analysis_timestamp": analysis_timestamp,
                "positive_trends": sentiment_patterns.get("positive_trends"),
                "negative_trends": sentiment_patterns.get("negative_trends"),
                "neutral_trends": sentiment_patterns.get("neutral_trends"),
                "source_file": source_file
            }])
            sentiment_df.to_sql("trend_summary_sentiment_patterns", engine, schema=target_schema, if_exists="append", index=False)
            logging.info(f"Loaded sentiment patterns into {target_schema}.trend_summary_sentiment_patterns")

        # Load engagement levels data
        engagement_levels = json_data.get("engagement_levels_artists", {})
        if engagement_levels:
            engagement_df = pd.DataFrame([{
                "analysis_timestamp": analysis_timestamp,
                "high_engagement": engagement_levels.get("high"),
                "medium_engagement": engagement_levels.get("medium"),
                "low_engagement": engagement_levels.get("low"),
                "source_file": source_file
            }])
            engagement_df.to_sql("trend_summary_engagement_levels", engine, schema=target_schema, if_exists="append", index=False)
            logging.info(f"Loaded engagement levels into {target_schema}.trend_summary_engagement_levels")

    except Exception as e:
        logging.error(f"Error loading trend summary data from {file_path}: {e}")


def load_insights_summary_json_to_tables(engine, file_path, target_schema, truncate_before_load=False):
    """Loads flattened insights summary data from a JSON file into multiple tables."""
    if not Path(file_path).exists():
        logging.warning(f"JSON file not found: {file_path}. Skipping load for insights summary tables.")
        return

    logging.info(f"Loading insights summary JSON data from {file_path} into flattened tables...")

    with open(file_path, 'r') as f:
        try:
            json_data = json.load(f)
        except json.JSONDecodeError as e:
            logging.error(f"Invalid JSON in file {file_path}: {e}")
            return

    source_file = str(Path(file_path).name)
    analysis_timestamp = pd.to_datetime(json_data.get("timestamp", pd.Timestamp.now())).to_pydatetime()

    # Truncate tables if requested
    if truncate_before_load:
        tables_to_truncate = [
            "insights_summary_overview", "insights_summary_key_findings", "insights_summary_artist_insights"
        ]
        for table_name in tables_to_truncate:
            table_name_with_schema = f"{target_schema}.{table_name}"
            inspector = inspect(engine)
            if inspector.has_table(table_name, schema=target_schema):
                truncate_table(engine, table_name_with_schema)

    try:
        # Load overview data
        overview_df = pd.DataFrame([{
            "analysis_timestamp": analysis_timestamp,
            "data_period": pd.to_datetime(json_data.get("data_period", pd.Timestamp.now())).to_pydatetime(),
            "confidence_score": json_data.get("confidence_score"),
            "executive_summary": json_data.get("executive_summary"),
            "source_file": source_file
        }])
        overview_df.to_sql("insights_summary_overview", engine, schema=target_schema, if_exists="append", index=False)
        logging.info(f"Loaded insights overview data into {target_schema}.insights_summary_overview")

        # Load key findings data
        key_findings = json_data.get("key_findings", [])
        if key_findings:
            findings_data = []
            for i, finding in enumerate(key_findings):
                findings_data.append({
                    "analysis_timestamp": analysis_timestamp,
                    "finding_text": finding,
                    "finding_order": i + 1,
                    "source_file": source_file
                })
            findings_df = pd.DataFrame(findings_data)
            findings_df.to_sql("insights_summary_key_findings", engine, schema=target_schema, if_exists="append", index=False)
            logging.info(f"Loaded {len(findings_data)} key findings into {target_schema}.insights_summary_key_findings")

        # Load artist insights data
        artist_insights = json_data.get("artist_insights", [])
        if artist_insights:
            insights_data = []
            for insight in artist_insights:
                # Extract artist name from the insight text (first bold text)
                artist_name = insight.split("**")[1] if "**" in insight else "Unknown"
                insights_data.append({
                    "analysis_timestamp": analysis_timestamp,
                    "artist_name": artist_name,
                    "insight_text": insight,
                    "source_file": source_file
                })
            insights_df = pd.DataFrame(insights_data)
            insights_df.to_sql("insights_summary_artist_insights", engine, schema=target_schema, if_exists="append", index=False)
            logging.info(f"Loaded {len(insights_data)} artist insights into {target_schema}.insights_summary_artist_insights")

    except Exception as e:
        logging.error(f"Error loading insights summary data from {file_path}: {e}")


def load_json_to_table(engine, file_path, table_name, target_schema, content_column_name, truncate_before_load=False):
    """Legacy function - kept for backward compatibility but not recommended for use."""
    logging.warning(f"load_json_to_table is deprecated. Please use specific flattened loaders for {table_name}")

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


def load_wordcloud_text_to_table(engine, file_path, target_schema, truncate_before_load=False):
    """Loads wordcloud text data from a text file into the wordcloud_data table."""
    if not Path(file_path).exists():
        logging.warning(f"Wordcloud text file not found: {file_path}. Skipping load for table {target_schema}.wordcloud_data.")
        return

    logging.info(f"Loading wordcloud text data from {file_path} into {target_schema}.wordcloud_data...")

    # Read the text file and count word frequencies
    word_counts = {}
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            word = line.strip()
            if word:  # Skip empty lines
                word_counts[word] = word_counts.get(word, 0) + 1

    # Convert to DataFrame
    df_data = []
    for word, frequency in word_counts.items():
        df_data.append({
            'word': word,
            'frequency': frequency,
            'source_platform': 'combined',  # Since it combines YouTube and Reddit
            'generation_date': date.today(),
            'source_file': Path(file_path).name
        })

    df = pd.DataFrame(df_data)
    logging.info(f"Processed {len(df)} unique words from {sum(word_counts.values())} total words")

    table_name = "wordcloud_data"
    table_name_with_schema = f"{target_schema}.{table_name}"

    if truncate_before_load:
        inspector = inspect(engine)
        if inspector.has_table(table_name, schema=target_schema):
            truncate_table(engine, table_name_with_schema)
        else:
            logging.info(f"Table {table_name_with_schema} does not exist, skipping truncation.")

    try:
        df.to_sql(table_name, engine, schema=target_schema, if_exists="append", index=False, method='multi')
        logging.info(f"Successfully loaded {len(df)} unique words into {target_schema}.{table_name}")
    except Exception as e:
        logging.error(f"Error loading wordcloud data from {file_path} to {target_schema}.{table_name}: {e}")
        logging.error("DataFrame columns: %s", df.columns.tolist())
        logging.error("DataFrame head:\n%s", df.head().to_string())


def normalize_genre_name(genre_name):
    """
    Normalize genre names to eliminate duplicates due to case differences.
    Follows the same logic as the DBT models for consistency.
    """
    if not genre_name or not isinstance(genre_name, str):
        return genre_name
    
    genre_lower = genre_name.lower().strip()
    
    # Apply normalization mapping
    genre_mappings = {
        # Pop variations
        'pop': 'J-Pop', 'j-pop': 'J-Pop', 'jpop': 'J-Pop', 'j pop': 'J-Pop',
        # Rock variations  
        'rock': 'J-Rock', 'j-rock': 'J-Rock', 'jrock': 'J-Rock', 'j rock': 'J-Rock',
        # Metal variations
        'metal': 'Metal', 'j-metal': 'Metal', 'jmetal': 'Metal',
        # Hip Hop variations
        'hip hop': 'Hip-Hop', 'hip-hop': 'Hip-Hop', 'hiphop': 'Hip-Hop', 'rap': 'Hip-Hop',
        # Electronic variations
        'electronic': 'Electronic', 'electro': 'Electronic', 'edm': 'Electronic',
        # Indie variations
        'indie': 'Indie', 'independent': 'Indie',
        # Alternative variations
        'alternative': 'Alternative', 'alt': 'Alternative',
        # Punk variations
        'punk': 'Punk', 'j-punk': 'Punk', 'jpunk': 'Punk',
        # Folk variations
        'folk': 'Folk', 'j-folk': 'Folk', 'jfolk': 'Folk',
        # Jazz variations
        'jazz': 'Jazz', 'j-jazz': 'Jazz', 'jjazz': 'Jazz',
        # Classical variations
        'classical': 'Classical', 'classic': 'Classical',
        # Blues variations
        'blues': 'Blues', 'j-blues': 'Blues', 'jblues': 'Blues',
        # R&B variations
        'r&b': 'R&B', 'rnb': 'R&B', 'r and b': 'R&B', 'rhythm and blues': 'R&B',
        # Vocal variations
        'vocal': 'Vocal', 'vocals': 'Vocal',
        # Common metal sub-genres
        'black metal': 'Black Metal', 'blackmetal': 'Black Metal',
        'death metal': 'Death Metal', 'deathmetal': 'Death Metal',
        'power metal': 'Power Metal', 'powermetal': 'Power Metal',
        'heavy metal': 'Heavy Metal', 'heavymetal': 'Heavy Metal',
        'thrash metal': 'Thrash Metal', 'thrashmetal': 'Thrash Metal', 'thrash': 'Thrash Metal',
        'nu metal': 'Nu Metal', 'numetal': 'Nu Metal', 'nu-metal': 'Nu Metal',
        # Post genres
        'post rock': 'Post-Rock', 'post-rock': 'Post-Rock', 'postrock': 'Post-Rock',
        'post punk': 'Post-Punk', 'post-punk': 'Post-Punk', 'postpunk': 'Post-Punk',
        # Electronic sub-genres
        'drum and bass': 'Drum & Bass', 'dnb': 'Drum & Bass', 'd&b': 'Drum & Bass', 'drum&bass': 'Drum & Bass',
        'dubstep': 'Dubstep', 'dub step': 'Dubstep',
        'house': 'House', 'tech house': 'House',
        'techno': 'Techno', 'tech': 'Techno',
        'trance': 'Trance', 'psytrance': 'Trance',
        # Other common variations
        'acoustic': 'Acoustic', 'unplugged': 'Acoustic',
        'experimental': 'Experimental', 'avant-garde': 'Experimental',
        'progressive': 'Progressive', 'prog': 'Progressive',
        'ambient': 'Ambient', 'chillout': 'Ambient', 'chill': 'Ambient',
        'new wave': 'New Wave', 'newwave': 'New Wave',
        'shoegaze': 'Shoegaze', 'shoe gaze': 'Shoegaze',
    }
    
    # Check if we have a specific mapping
    if genre_lower in genre_mappings:
        return genre_mappings[genre_lower]
    
    # Default: Use proper title case
    return genre_name.title()

# ...existing code...
def main():
    parser = argparse.ArgumentParser(description="Load LLM pipeline outputs into PostgreSQL analytics schema.")
    parser.add_argument("--entities-file-reddit", type=str, help="Path to the Reddit entity extraction CSV file.")
    parser.add_argument("--entities-file-youtube", type=str, help="Path to the YouTube entity extraction CSV file.")
    parser.add_argument("--sentiment-file-reddit", type=str, help="Path to the Reddit sentiment analysis CSV file.")
    parser.add_argument("--sentiment-file-youtube", type=str, help="Path to the YouTube sentiment analysis CSV file.")
    parser.add_argument("--artist-trends-file", type=str, help="Path to the artist trends CSV file.")
    parser.add_argument("--genre-trends-file", type=str, help="Path to the genre trends CSV file.")
    parser.add_argument("--temporal-trends-file", type=str, help="Path to the temporal trends CSV file.")
    parser.add_argument("--trend-summary-json", type=str, help="Path to the trend summary JSON file.")
    parser.add_argument("--summarization-metrics-file", type=str, help="Path to the summarization metrics CSV file.")
    parser.add_argument("--insights-summary-json", type=str, help="Path to the insights summary JSON file.")
    parser.add_argument("--wordcloud-text-file", type=str, help="Path to the wordcloud text file.")
    parser.add_argument("--truncate", action="store_true", help="Truncate tables before loading data.")

    args = parser.parse_args()

    engine = get_engine()
    ensure_schema_and_tables(engine)

    # Load entity extraction files (combining Reddit and YouTube)
    if args.entities_file_reddit:
        load_csv_to_table(engine, args.entities_file_reddit, "entity_extraction", ANALYTICS_SCHEMA, args.truncate)
    if args.entities_file_youtube:
        load_csv_to_table(engine, args.entities_file_youtube, "entity_extraction", ANALYTICS_SCHEMA, False)  # Don't truncate on second file

    # Load sentiment analysis files (combining Reddit and YouTube)
    if args.sentiment_file_reddit:
        load_csv_to_table(engine, args.sentiment_file_reddit, "sentiment_analysis", ANALYTICS_SCHEMA, args.truncate)
    if args.sentiment_file_youtube:
        load_csv_to_table(engine, args.sentiment_file_youtube, "sentiment_analysis", ANALYTICS_SCHEMA, False)  # Don't truncate on second file

    # Load trend analysis files
    if args.artist_trends_file:
        load_csv_to_table(engine, args.artist_trends_file, "artist_trends", ANALYTICS_SCHEMA, args.truncate)
    if args.genre_trends_file:
        load_csv_to_table(engine, args.genre_trends_file, "genre_trends", ANALYTICS_SCHEMA, args.truncate)
    if args.temporal_trends_file:
        load_csv_to_table(engine, args.temporal_trends_file, "temporal_trends", ANALYTICS_SCHEMA, args.truncate)

    # Load flattened JSON files
    if args.trend_summary_json:
        load_trend_summary_json_to_tables(engine, args.trend_summary_json, ANALYTICS_SCHEMA, args.truncate)
    if args.insights_summary_json:
        load_insights_summary_json_to_tables(engine, args.insights_summary_json, ANALYTICS_SCHEMA, args.truncate)

    # Load summarization metrics CSV
    if args.summarization_metrics_file:
        load_csv_to_table(engine, args.summarization_metrics_file, "summarization_metrics", ANALYTICS_SCHEMA, args.truncate)

    # Load wordcloud text file
    if args.wordcloud_text_file:
        load_wordcloud_text_to_table(engine, args.wordcloud_text_file, ANALYTICS_SCHEMA, args.truncate)

    logging.info("Data loading process finished.")

if __name__ == "__main__":
    main()
