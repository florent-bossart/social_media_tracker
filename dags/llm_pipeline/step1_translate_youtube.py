#!/usr/bin/env python3
"""
Step 1: YouTube Tra    # Run the translation script
    cmd = [
        "poetry", "run", "python",
        "/app/data_pipeline/translate_youtube_comments.py",
        "--input-file", latest_file,
        "--output-dir", output_dir,
        "--column", "comment_text",
        "--output-column", "text_clean_en_nllb"
    ]n DAG
Translates the latest YouTube cleaned file from Japanese to English.
"""

import os
from datetime import datetime, timedelta
from pathlib import Path

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago

# Define the base path for the project (not used for data paths anymore)
PROJECT_BASE_PATH = "/app"

def translate_latest_youtube_file(**context):
    """Translate the latest YouTube cleaned file."""
    import sys
    import subprocess
    import glob
    from pathlib import Path

    # Add project root to Python path
    sys.path.append(PROJECT_BASE_PATH)

    # Import standalone file detection utilities
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from file_detection_utils import find_latest_cleaned_file

    # Find the latest YouTube cleaned file (data is in /app/airflow/data)
    latest_file = find_latest_cleaned_file("youtube", "/app/airflow/data/intermediate")

    if not latest_file:
        raise FileNotFoundError("No YouTube cleaned file found for translation")

    print(f"Found latest YouTube cleaned file: {latest_file}")

    # Extract just the filename for the output
    input_filename = Path(latest_file).name

    # Set up output directory (also in /app/airflow/data)
    output_dir = "/app/airflow/data/intermediate/translated"
    os.makedirs(output_dir, exist_ok=True)

    # Run the translation script (script is at /app/data_pipeline, run from /app/airflow)
    cmd = [
        "poetry", "run", "python",
        "../data_pipeline/translate_youtube_comments.py",  # Relative path from /app/airflow
        "--input-file", latest_file,
        "--output-dir", output_dir,
        "--column", "comment_text"
    ]

    print(f"Running translation command: {' '.join(cmd)}")

    # Change to project directory to ensure .env file is found
    result = subprocess.run(cmd, cwd="/app/airflow", capture_output=True, text=True)

    if result.returncode != 0:
        print(f"Translation failed with return code {result.returncode}")
        print(f"STDOUT: {result.stdout}")
        print(f"STDERR: {result.stderr}")
        raise RuntimeError(f"Translation failed: {result.stderr}")

    print(f"Translation completed successfully")
    print(f"Output: {result.stdout}")

    # Return the output file path for downstream tasks
    output_filename = input_filename.replace('_cleaned.csv', '_cleaned_nllb_translated.csv')
    output_path = f"{output_dir}/{output_filename}"

    return {
        "input_file": latest_file,
        "output_file": output_path,
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
    dag_id='llm_step1_translate_youtube',
    default_args=default_args,
    description='Step 1: Translate latest YouTube cleaned file from Japanese to English',
    schedule_interval=None,  # Manual execution only
    start_date=days_ago(1),
    catchup=False,
    tags=['llm', 'translation', 'youtube', 'step1'],
) as dag:

    translate_task = PythonOperator(
        task_id='translate_youtube_comments',
        python_callable=translate_latest_youtube_file,
        execution_timeout=None,  # No timeout as requested
    )
