#!/usr/bin/env python3
"""
Airflow DAG Step 8: Load Analytics Data

This DAG loads all analytics data (entities, sentiment, trends, summarization) into the database.
It auto-detects the latest files from all pipeline steps and loads them into the analytics schema.
"""



from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
import logging
import os
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Default arguments for the DAG
default_args = {
    'owner': 'data-pipeline',
    'depends_on_past': False,
    'start_date': datetime(2025, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Create DAG
dag = DAG(
    'step8_load_analytics_data',
    default_args=default_args,
    description='Load all analytics data into database',
    schedule_interval=None,  # Manual trigger
    catchup=False,
    max_active_runs=1,
    tags=['llm-pipeline', 'analytics', 'loading']
)

def detect_latest_files(**context):
    """Detect all latest analytics files and prepare load commands."""

    # Import file detection utilities from data_pipeline
    import sys
    sys.path.append("/app/data_pipeline")
    from file_detection_utils import (
        find_latest_entity_file,
        find_latest_sentiment_file,
        find_latest_trend_files,
        find_latest_summarization_files,
        find_latest_wordcloud_file
    )

    # Base directory for intermediate data (use /app/airflow/data for container)
    base_dir = "/app/airflow/data/intermediate"

    logger.info("Detecting latest analytics files...")

    # Find entity files
    entity_reddit = find_latest_entity_file("reddit", base_dir)
    entity_youtube = find_latest_entity_file("youtube", base_dir)

    # Find sentiment files
    sentiment_reddit = find_latest_sentiment_file("reddit", base_dir)
    sentiment_youtube = find_latest_sentiment_file("youtube", base_dir)

    # Find trend files
    artist_trends, genre_trends, temporal_trends, trend_summary = find_latest_trend_files(base_dir)

    # Find summarization files
    insights_summary, metrics_csv = find_latest_summarization_files(base_dir)

    # Find wordcloud file
    wordcloud_file = find_latest_wordcloud_file(base_dir)

    # Log findings
    logger.info(f"Entity files - Reddit: {entity_reddit}, YouTube: {entity_youtube}")
    logger.info(f"Sentiment files - Reddit: {sentiment_reddit}, YouTube: {sentiment_youtube}")
    logger.info(f"Trend files - Artists: {artist_trends}, Genres: {genre_trends}, Temporal: {temporal_trends}")
    logger.info(f"Trend summary: {trend_summary}")
    logger.info(f"Summarization - Insights: {insights_summary}, Metrics: {metrics_csv}")
    logger.info(f"Wordcloud file: {wordcloud_file}")

    # Store file paths in XCom for use by loading task
    files_info = {
        'entity_reddit': entity_reddit,
        'entity_youtube': entity_youtube,
        'sentiment_reddit': sentiment_reddit,
        'sentiment_youtube': sentiment_youtube,
        'artist_trends': artist_trends,
        'genre_trends': genre_trends,
        'temporal_trends': temporal_trends,
        'trend_summary': trend_summary,
        'insights_summary': insights_summary,
        'metrics_csv': metrics_csv,
        'wordcloud_file': wordcloud_file
    }

    return files_info

def build_load_command(**context):
    """Build the load command with all detected files."""

    # Retrieve file paths from XCom
    files_info = context['task_instance'].xcom_pull(task_ids='detect_files')

    if not files_info:
        raise ValueError("No file information received from detect_files task")

    # Base command
    load_script = "/app/data_pipeline/load_analytics_data.py"
    cmd = [f"cd /app && python {load_script}"]

    # Add file arguments
    if files_info.get('entity_reddit'):
        cmd.append(f"--entities-file-reddit '{files_info['entity_reddit']}'")

    if files_info.get('entity_youtube'):
        cmd.append(f"--entities-file-youtube '{files_info['entity_youtube']}'")

    if files_info.get('sentiment_reddit'):
        cmd.append(f"--sentiment-file-reddit '{files_info['sentiment_reddit']}'")

    if files_info.get('sentiment_youtube'):
        cmd.append(f"--sentiment-file-youtube '{files_info['sentiment_youtube']}'")

    if files_info.get('artist_trends'):
        cmd.append(f"--artist-trends-file '{files_info['artist_trends']}'")

    if files_info.get('genre_trends'):
        cmd.append(f"--genre-trends-file '{files_info['genre_trends']}'")

    if files_info.get('temporal_trends'):
        cmd.append(f"--temporal-trends-file '{files_info['temporal_trends']}'")

    if files_info.get('trend_summary'):
        cmd.append(f"--trend-summary-json '{files_info['trend_summary']}'")

    if files_info.get('insights_summary'):
        cmd.append(f"--insights-summary-json '{files_info['insights_summary']}'")

    if files_info.get('metrics_csv'):
        cmd.append(f"--summarization-metrics-file '{files_info['metrics_csv']}'")

    if files_info.get('wordcloud_file'):
        cmd.append(f"--wordcloud-text-file '{files_info['wordcloud_file']}'")

    # Add truncate flag to refresh all data
    cmd.append("--truncate")

    # Join command parts
    full_command = " ".join(cmd)

    logger.info(f"Generated load command: {full_command}")

    return full_command

# Task 1: Detect latest files
detect_files_task = PythonOperator(
    task_id='detect_files',
    python_callable=detect_latest_files,
    dag=dag,
)

# Task 2: Build load command
build_command_task = PythonOperator(
    task_id='build_load_command',
    python_callable=build_load_command,
    dag=dag,
)

# Task 3: Execute load command
load_analytics_task = BashOperator(
    task_id='load_analytics_data',
    bash_command="{{ task_instance.xcom_pull(task_ids='build_load_command') }}",
    dag=dag,
)

# Task 4: Verify loaded data
verify_load_task = BashOperator(
    task_id='verify_load',
    bash_command="""
    cd /app && python -c "
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

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
"
    """,
    dag=dag,
)

# Define task dependencies
detect_files_task >> build_command_task >> load_analytics_task >> verify_load_task
