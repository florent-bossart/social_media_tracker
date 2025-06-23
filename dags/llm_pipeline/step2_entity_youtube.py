#!/usr/bin/env python3
"""
Step 2: YouTube Entity Extraction DAG
Runs entity extraction on the latest translated YouTube file.
"""

import os
from datetime import datetime, timedelta
from pathlib import Path

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago

# Define the base path for the project
PROJECT_BASE_PATH = "/app"

def extract_entities_youtube(**context):
    """Run entity extraction on the latest translated YouTube file."""
    import sys
    import subprocess

    # Add project root to Python path
    sys.path.append(PROJECT_BASE_PATH)

    # Import standalone file detection utilities from data_pipeline
    sys.path.append(os.path.join(PROJECT_BASE_PATH, 'data_pipeline'))
    from file_detection_utils import find_latest_translated_file

    # Find the latest YouTube translated file (use /app/airflow/data for container)
    latest_file = find_latest_translated_file("youtube", "/app/airflow/data/intermediate")

    if not latest_file:
        raise FileNotFoundError("No YouTube translated file found for entity extraction")

    print(f"Found latest YouTube translated file: {latest_file}")

    # Set up output directory (use /app/airflow/data for container)
    output_dir = "/app/airflow/data/intermediate/entity_extraction"
    os.makedirs(output_dir, exist_ok=True)

    # Get LLM host from environment
    llm_host = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
    print(f"Using LLM host: {llm_host}")

    # Run the entity extraction script
    cmd = [
        "poetry", "run", "python",
        "/app/data_pipeline/run_specific_entity_extraction.py",
        "--input_file", latest_file,
        "--platform", "youtube",
        "--output_dir", output_dir
    ]

    # Add LLM host if available
    if llm_host:
        cmd.extend(["--ollama-host", llm_host])

    print(f"Running entity extraction command: {' '.join(cmd)}")

    # Change to project directory to ensure .env file is found
    result = subprocess.run(cmd, cwd="/app/airflow", capture_output=True, text=True)

    if result.returncode != 0:
        print(f"Entity extraction failed with return code {result.returncode}")
        print(f"STDOUT: {result.stdout}")
        print(f"STDERR: {result.stderr}")
        raise RuntimeError(f"Entity extraction failed: {result.stderr}")

    print(f"Entity extraction completed successfully")
    print(f"Output: {result.stdout}")

    # Find the generated output file
    from file_detection_utils import find_latest_entity_file
    output_file = find_latest_entity_file("youtube", f"{PROJECT_BASE_PATH}/data/intermediate")

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
    dag_id='llm_step2_entity_youtube',
    default_args=default_args,
    description='Step 2: Entity extraction on latest translated YouTube file',
    schedule_interval=None,  # Manual execution only
    start_date=days_ago(1),
    catchup=False,
    tags=['llm', 'entity', 'youtube', 'step2'],
) as dag:

    entity_task = PythonOperator(
        task_id='extract_youtube_entities',
        python_callable=extract_entities_youtube,
        execution_timeout=None,  # No timeout as requested
    )
