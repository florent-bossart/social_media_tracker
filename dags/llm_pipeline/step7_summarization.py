#!/usr/bin/env python3
"""
Step 7: Summarization DAG
Runs summarization on the latest trend detection files.
"""

import os
from datetime import datetime, timedelta
from pathlib import Path

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago

# Define the base path for the project
PROJECT_BASE_PATH = "/app/airflow"

def generate_summary(**context):
    """Run summarization on the latest trend detection files."""
    import sys
    import subprocess

    # Add project root to Python path
    sys.path.append(PROJECT_BASE_PATH)

    # Import standalone file detection utilities
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from file_detection_utils import find_latest_trend_files

    # Helper functions for date and source extraction
    import re
    def extract_date_from_filename(filename: str):
        """Extract YYYYMMDD date from filename."""
        match = re.search(r'(\d{8})', filename)
        return match.group(1) if match else None

    def extract_source_tag_from_filename(filename: str):
        """Extract source tag (combined, youtube, reddit) from filename."""
        if 'combined' in filename.lower():
            return 'combined'
        elif 'youtube' in filename.lower():
            return 'youtube'
        elif 'reddit' in filename.lower():
            return 'reddit'
        else:
            return 'unknown'

    # Find the latest trend files (use /app/airflow/data for container)
    artist_file, genre_file, temporal_file, summary_file = find_latest_trend_files("/app/airflow/data/intermediate")

    if not summary_file:
        raise FileNotFoundError("No trend summary file found for summarization")

    print(f"Found latest trend files:")
    print(f"  Artist: {artist_file}")
    print(f"  Genre: {genre_file}")
    print(f"  Temporal: {temporal_file}")
    print(f"  Summary: {summary_file}")

    # Extract date and source tags from the files
    date_tag = extract_date_from_filename(summary_file)
    source_tag = extract_source_tag_from_filename(summary_file)

    if not date_tag:
        raise ValueError(f"Could not extract date from filename: {summary_file}")

    print(f"Extracted date tag: {date_tag}")
    print(f"Extracted source tag: {source_tag}")

    # Set up input and output directories (use /app/airflow/data for container)
    input_dir = "/app/airflow/data/intermediate/trend_analysis"
    output_dir = "/app/airflow/data/intermediate/summarization"
    os.makedirs(output_dir, exist_ok=True)

    # Get LLM host from environment
    llm_host = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
    print(f"Using LLM host: {llm_host}")

    # Run the summarization script
    cmd = [
        "poetry", "run", "python",
        "/app/llm_enrichment/summarization/summarization_standalone.py",
        "--input-dir", input_dir,
        "--output-dir", output_dir,
        "--date-tag", date_tag,
        "--source-tag", source_tag,
        "--log_level", "INFO"
    ]

    # Add LLM host if available
    if llm_host:
        cmd.extend(["--ollama-host", llm_host])

    print(f"Running summarization command: {' '.join(cmd)}")

    # Change to project directory to ensure .env file is found
    result = subprocess.run(cmd, cwd="/app/airflow", capture_output=True, text=True)

    if result.returncode != 0:
        print(f"Summarization failed with return code {result.returncode}")
        print(f"STDOUT: {result.stdout}")
        print(f"STDERR: {result.stderr}")
        raise RuntimeError(f"Summarization failed: {result.stderr}")

    print(f"Summarization completed successfully")
    print(f"Output: {result.stdout}")

    # Expected output files
    insights_file = f"{output_dir}/trend_insights_{date_tag}_{source_tag}.json"
    metrics_file = f"{output_dir}/trend_insights_{date_tag}_{source_tag}_metrics.csv"

    return {
        "input_summary": summary_file,
        "input_artist": artist_file,
        "input_genre": genre_file,
        "input_temporal": temporal_file,
        "output_insights": insights_file,
        "output_metrics": metrics_file,
        "date_tag": date_tag,
        "source_tag": source_tag,
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
    dag_id='llm_step7_summarization',
    default_args=default_args,
    description='Step 7: Summarization of latest trend detection results',
    schedule_interval=None,  # Manual execution only
    start_date=days_ago(1),
    catchup=False,
    tags=['llm', 'summarization', 'step7'],
) as dag:

    summary_task = PythonOperator(
        task_id='generate_summary',
        python_callable=generate_summary,
        execution_timeout=None,  # No timeout as requested
    )
