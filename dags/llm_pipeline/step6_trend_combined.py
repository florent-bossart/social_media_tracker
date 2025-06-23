#!/usr/bin/env python3
"""
Step 6: Combined Tr    cmd = [
        "poetry", "run", "python",
        "/app/llm_enrichment/trend/trend_detection_combined_standalone.py",
        "--input_file_youtube", youtube_file,
        "--input_file_reddit", reddit_file,
        "--output_dir", output_dir,
        "--log_level", "INFO"
    ]ction DAG
Runs trend detection using both YouTube and Reddit sentiment analysis files.
"""

import os
from datetime import datetime, timedelta
from pathlib import Path

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago

# Define the base path for the project
PROJECT_BASE_PATH = "/app"

def detect_trends_combined(**context):
    """Run combined trend detection on the latest sentiment analysis files."""
    import sys
    import subprocess

    # Add project root to Python path
    sys.path.append(PROJECT_BASE_PATH)

    # Import standalone file detection utilities from data_pipeline
    sys.path.append(os.path.join(PROJECT_BASE_PATH, 'data_pipeline'))
    from file_detection_utils import find_latest_sentiment_file

    # Find the latest sentiment files for both platforms
    youtube_sentiment = find_latest_sentiment_file("youtube", f"{PROJECT_BASE_PATH}/airflow/data/intermediate")
    reddit_sentiment = find_latest_sentiment_file("reddit", f"{PROJECT_BASE_PATH}/airflow/data/intermediate")

    if not youtube_sentiment:
        raise FileNotFoundError("No YouTube sentiment file found for trend detection")
    if not reddit_sentiment:
        raise FileNotFoundError("No Reddit sentiment file found for trend detection")

    print(f"Found latest YouTube sentiment file: {youtube_sentiment}")
    print(f"Found latest Reddit sentiment file: {reddit_sentiment}")

    # Set up output directory
    output_dir = f"{PROJECT_BASE_PATH}/airflow/data/intermediate/trend_analysis"
    os.makedirs(output_dir, exist_ok=True)

    # Run the combined trend detection script
    cmd = [
        "poetry", "run", "python",
        f"{PROJECT_BASE_PATH}/llm_enrichment/trend/trend_detection_combined_standalone.py",
        "--input_file_youtube", youtube_sentiment,
        "--input_file_reddit", reddit_sentiment,
        "--output_dir", output_dir,
        "--log_level", "INFO"
    ]

    print(f"Running trend detection command: {' '.join(cmd)}")

    # Change to project directory to ensure .env file is found
    result = subprocess.run(cmd, cwd="/app/airflow", capture_output=True, text=True)

    if result.returncode != 0:
        print(f"Trend detection failed with return code {result.returncode}")
        print(f"STDOUT: {result.stdout}")
        print(f"STDERR: {result.stderr}")
        raise RuntimeError(f"Trend detection failed: {result.stderr}")

    print(f"Trend detection completed successfully")
    print(f"Output: {result.stdout}")

    # Find the generated output files
    from file_detection_utils import find_latest_trend_files
    artist_file, genre_file, temporal_file, summary_file = find_latest_trend_files(f"{PROJECT_BASE_PATH}/airflow/data/intermediate")

    return {
        "input_youtube": youtube_sentiment,
        "input_reddit": reddit_sentiment,
        "output_artist": artist_file,
        "output_genre": genre_file,
        "output_temporal": temporal_file,
        "output_summary": summary_file,
        "status": "success"
    }

# Default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 0,  # No retries as requested
}

# Create the DAG
with DAG(
    dag_id='llm_step6_trend_combined',
    default_args=default_args,
    description='Step 6: Combined trend detection using YouTube and Reddit sentiment files',
    schedule_interval=None,  # Manual execution only
    start_date=days_ago(1),
    catchup=False,
    tags=['llm', 'trend', 'combined', 'step6'],
) as dag:

    trend_task = PythonOperator(
        task_id='detect_trends_combined',
        python_callable=detect_trends_combined,
        execution_timeout=None,  # No timeout as requested
    )
