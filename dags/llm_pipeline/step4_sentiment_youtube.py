#!/usr/bin/env python3
"""
Step 4: YouTube Sentiment Analysis DAG
Runs sentiment analysis on the latest YouTube entity file.
"""

import os
from datetime import datetime, timedelta
from pathlib import Path

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago

# Define the base path for the project
PROJECT_BASE_PATH = "/app"

def analyze_sentiment_youtube(**context):
    """Run sentiment analysis on the latest YouTube entity file."""
    import sys
    import subprocess

    # Add project root to Python path
    sys.path.append(PROJECT_BASE_PATH)

    # Import standalone file detection utilities
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from file_detection_utils import find_latest_entity_file

    # Find the latest YouTube entity file (use /app/airflow/data for container)
    latest_file = find_latest_entity_file("youtube", "/app/airflow/data/intermediate")

    if not latest_file:
        raise FileNotFoundError("No YouTube entity file found for sentiment analysis")

    print(f"Found latest YouTube entity file: {latest_file}")

    # Set up output directory (use /app/airflow/data for container)
    output_dir = "/app/airflow/data/intermediate/sentiment_analysis"
    os.makedirs(output_dir, exist_ok=True)

    # Get LLM host from environment
    llm_host = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
    print(f"Using LLM host: {llm_host}")

    # Run the sentiment analysis script
    cmd = [
        "poetry", "run", "python",
        "/app/data_pipeline/run_sentiment_pipeline.py",
        "youtube",
        "--input_file", latest_file,
        "--output_dir", output_dir
    ]

    # Add LLM host if available
    if llm_host:
        cmd.extend(["--ollama-host", llm_host])

    print(f"Running sentiment analysis command: {' '.join(cmd)}")

    # Change to project directory to ensure .env file is found
    result = subprocess.run(cmd, cwd="/app/airflow", capture_output=True, text=True)

    if result.returncode != 0:
        print(f"Sentiment analysis failed with return code {result.returncode}")
        print(f"STDOUT: {result.stdout}")
        print(f"STDERR: {result.stderr}")
        raise RuntimeError(f"Sentiment analysis failed: {result.stderr}")

    print(f"Sentiment analysis completed successfully")
    print(f"Output: {result.stdout}")

    # Find the generated output file (prefer combined) (use /app/airflow/data for container)
    from file_detection_utils import find_latest_sentiment_file
    output_file = find_latest_sentiment_file("youtube", "/app/airflow/data/intermediate")

    return {
        "input_file": latest_file,
        "output_file": output_file,
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
    dag_id='llm_step4_sentiment_youtube',
    default_args=default_args,
    description='Step 4: Sentiment analysis on latest YouTube entity file',
    schedule_interval=None,  # Manual execution only
    start_date=days_ago(1),
    catchup=False,
    tags=['llm', 'sentiment', 'youtube', 'step4'],
) as dag:

    sentiment_task = PythonOperator(
        task_id='analyze_youtube_sentiment',
        python_callable=analyze_sentiment_youtube,
        execution_timeout=None,  # No timeout as requested
    )
