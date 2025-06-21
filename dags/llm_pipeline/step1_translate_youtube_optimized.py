#!/usr/bin/env python3
"""
Step 1 Optimized: YouTube Translation DAG (Memory Optimized)
Translates the latest YouTube cleaned file from Japanese to English with memory management.
"""

import os
from datetime import datetime, timedelta
from pathlib import Path

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago

# Define the base path for the project
PROJECT_BASE_PATH = "/app"

def translate_latest_youtube_file_optimized(**context):
    """Translate the latest YouTube cleaned file with memory optimization."""
    import sys
    import subprocess
    import glob
    from pathlib import Path

    # Add project root to Python path
    sys.path.append(PROJECT_BASE_PATH)

    # Import standalone file detection utilities
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from file_detection_utils import find_latest_cleaned_file

    # Find the latest YouTube cleaned file
    latest_file = find_latest_cleaned_file("youtube", "/app/airflow/data/intermediate")

    if not latest_file:
        raise FileNotFoundError("No YouTube cleaned file found for translation")

    print(f"Found latest YouTube cleaned file: {latest_file}")

    # Extract just the filename for the output
    input_filename = Path(latest_file).name

    # Set up output directory
    output_dir = "/app/airflow/data/intermediate/translated"
    os.makedirs(output_dir, exist_ok=True)

    # Run the memory-optimized translation script
    cmd = [
        "poetry", "run", "python",
        "../data_pipeline/translate_youtube_comments_optimized.py",  # Use optimized version
        "--input-file", latest_file,
        "--output-dir", output_dir,
        "--column", "comment_text"
    ]

    print(f"Running optimized translation command: {' '.join(cmd)}")

    # Set memory limits using environment variables
    env = os.environ.copy()
    env.update({
        'PYTORCH_CUDA_ALLOC_CONF': 'max_split_size_mb:512',
        'MALLOC_ARENA_MAX': '2',
        'OMP_NUM_THREADS': '1',
        'TOKENIZERS_PARALLELISM': 'false'  # Disable tokenizer parallelism to save memory
    })

    # Change to project directory to ensure .env file is found
    result = subprocess.run(cmd, cwd="/app/airflow", capture_output=True, text=True, env=env)

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

def check_system_resources(**context):
    """Check system resources before starting translation."""
    import logging

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    try:
        import psutil

        # Check available memory
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()

        logger.info(f"System Memory - Total: {memory.total / (1024**3):.1f} GB")
        logger.info(f"System Memory - Available: {memory.available / (1024**3):.1f} GB")
        logger.info(f"System Memory - Used: {memory.percent:.1f}%")
        logger.info(f"Swap Memory - Total: {swap.total / (1024**3):.1f} GB")
        logger.info(f"Swap Memory - Used: {swap.percent:.1f}%")

        # Check if we have enough available memory (at least 2GB recommended)
        min_memory_gb = 2.0
        available_memory_gb = memory.available / (1024**3)

        if available_memory_gb < min_memory_gb:
            logger.warning(f"Low memory warning: Only {available_memory_gb:.1f} GB available, recommend at least {min_memory_gb} GB")

        # Check disk space
        disk = psutil.disk_usage('/')
        logger.info(f"Disk Space - Total: {disk.total / (1024**3):.1f} GB")
        logger.info(f"Disk Space - Free: {disk.free / (1024**3):.1f} GB")
        logger.info(f"Disk Space - Used: {(disk.used / disk.total) * 100:.1f}%")

        return {
            "memory_available_gb": available_memory_gb,
            "memory_percent_used": memory.percent,
            "swap_percent_used": swap.percent,
            "disk_free_gb": disk.free / (1024**3)
        }

    except ImportError:
        logger.warning("psutil not available, skipping detailed resource checks")
        return {
            "memory_available_gb": 0,
            "memory_percent_used": 0,
            "swap_percent_used": 0,
            "disk_free_gb": 0,
            "status": "psutil_not_available"
        }

# Default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 0,  # No retries to avoid repeated memory issues
}

# Create the DAG
with DAG(
    dag_id='llm_step1_translate_youtube_optimized',
    default_args=default_args,
    description='Step 1 (Optimized): Translate latest YouTube cleaned file from Japanese to English',
    schedule_interval=None,  # Manual execution only
    start_date=days_ago(1),
    catchup=False,
    max_active_runs=1,  # Prevent multiple concurrent runs
    tags=['llm', 'translation', 'youtube', 'step1', 'optimized'],
) as dag:

    # Task 1: Check system resources
    check_resources_task = PythonOperator(
        task_id='check_system_resources',
        python_callable=check_system_resources,
        execution_timeout=timedelta(minutes=2),
    )

    # Task 2: Translate with optimization
    translate_task = PythonOperator(
        task_id='translate_youtube_comments_optimized',
        python_callable=translate_latest_youtube_file_optimized,
        execution_timeout=timedelta(hours=4),  # Allow more time but with timeout
        # pool='memory_intensive_pool',  # Commented out until pool is created
    )

    # Set task dependencies
    check_resources_task >> translate_task
