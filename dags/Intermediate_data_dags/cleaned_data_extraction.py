"""
Automated Data Extraction DAG

This DAG automatically detects the latest data extraction date and extracts new data
from that point until today, keeping the pipeline up-to-date with fresh social media data.
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import os
import glob
import re
import subprocess
from pathlib import Path

# Configuration
PROJECT_BASE_PATH = "/app/airflow"

# Default DAG arguments
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 6, 17),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def get_latest_extraction_date():
    """
    Find the latest extraction date from existing cleaned data files

    Returns:
        str: Latest extraction date in YYYY-MM-DD format, or None if no files found
    """
    cleaned_data_dir = f"{PROJECT_BASE_PATH}/data/intermediate/Cleaned_data"

    if not os.path.exists(cleaned_data_dir):
        print(f"Warning: Cleaned data directory does not exist: {cleaned_data_dir}")
        return None

    # Look for files with pattern: YYYYMMDD_YYYY-MM-DD_*.csv
    pattern = os.path.join(cleaned_data_dir, "*_*_*_comments_cleaned.csv")
    files = glob.glob(pattern)

    if not files:
        print("No existing cleaned data files found")
        return None

    # Extract extraction dates from filenames (first date in filename)
    extraction_dates = []
    for file in files:
        filename = os.path.basename(file)
        # Pattern: 20250616_2025-06-11_youtube_comments_cleaned.csv
        # Extract the extraction date (20250616) and convert to YYYY-MM-DD format
        match = re.search(r'^(\d{8})_', filename)
        if match:
            extraction_date_str = match.group(1)
            # Convert YYYYMMDD to YYYY-MM-DD
            if len(extraction_date_str) == 8:
                formatted_date = f"{extraction_date_str[:4]}-{extraction_date_str[4:6]}-{extraction_date_str[6:8]}"
                extraction_dates.append(formatted_date)
                print(f"Found extraction date: {formatted_date} from file: {filename}")

    if not extraction_dates:
        print("No valid extraction date patterns found in filenames")
        return None

    # Find the latest extraction date
    latest_date = max(extraction_dates)
    print(f"Latest extraction date found: {latest_date}")
    return latest_date

def calculate_next_extraction_date(latest_extraction_date):
    """
    Calculate the data date to extract from based on the latest extraction date.

    The logic is:
    - If latest extraction was on date X, we need to extract data from (X + 1) onwards
    - This ensures we don't miss any data between extractions

    Args:
        latest_extraction_date (str): Latest extraction date in YYYY-MM-DD format

    Returns:
        str: Next data date to extract from in YYYY-MM-DD format
    """
    if not latest_extraction_date:
        # If no previous extraction, start from a week ago
        next_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        print(f"No previous extraction found, starting from: {next_date}")
        return next_date

    # Convert to datetime and add one day to get the next data date
    latest_dt = datetime.strptime(latest_extraction_date, '%Y-%m-%d')
    next_dt = latest_dt + timedelta(days=1)
    next_date = next_dt.strftime('%Y-%m-%d')

    print(f"Latest extraction was on: {latest_extraction_date}")
    print(f"Next data date to extract from: {next_date}")
    return next_date

def check_if_extraction_needed():
    """
    Check if data extraction is needed based on latest extraction date

    Returns:
        bool: True if extraction is needed, False otherwise
    """
    latest_extraction_date = get_latest_extraction_date()

    if not latest_extraction_date:
        print("No previous extractions found, extraction needed")
        return True

    # Check if latest extraction is from today
    today = datetime.now().strftime('%Y-%m-%d')

    if latest_extraction_date >= today:
        print(f"Latest extraction ({latest_extraction_date}) is current (today: {today}), no extraction needed")
        return False

    print(f"Latest extraction ({latest_extraction_date}) is older than today ({today}), extraction needed")
    return True

def extract_new_data():
    """
    Extract new social media data from the day after the latest extraction until today
    """
    print("🚀 Starting automated data extraction...")

    # Check if extraction is needed
    if not check_if_extraction_needed():
        print("ℹ️ Data is up-to-date, skipping extraction")
        return "skipped"

    # Get the latest extraction date and calculate what data date to extract from
    latest_extraction_date = get_latest_extraction_date()
    data_date_to_extract = calculate_next_extraction_date(latest_extraction_date)

    # Construct the extraction command
    cmd = [
        "poetry", "run", "python",
        "../data_pipeline/extract_cleaned_comments_by_date.py",  # Relative path from /app/airflow
        "--date", data_date_to_extract,
        "--source", "both"
    ]

    print(f"Running extraction command: {' '.join(cmd)}")
    print(f"This will extract data with fetch_date >= {data_date_to_extract}")

    try:
        # Run the extraction command
        result = subprocess.run(
            cmd,
            cwd="/app/airflow",  # Changed to /app/airflow where pyproject.toml is located
            capture_output=True,
            text=True,
            timeout=1800  # 30 minute timeout
        )

        if result.returncode == 0:
            print("✅ Data extraction completed successfully")
            print("STDOUT:", result.stdout)
            return "success"
        else:
            print(f"❌ Data extraction failed with return code: {result.returncode}")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            raise RuntimeError(f"Data extraction failed: {result.stderr}")

    except subprocess.TimeoutExpired:
        print("❌ Data extraction timed out after 30 minutes")
        raise RuntimeError("Data extraction timed out")
    except Exception as e:
        print(f"❌ Error during data extraction: {str(e)}")
        raise

def list_new_files():
    """
    List the newly extracted files for verification
    """
    cleaned_data_dir = f"{PROJECT_BASE_PATH}/data/intermediate/Cleaned_data"

    # Get today's extraction files
    today = datetime.now().strftime('%Y%m%d')
    pattern = os.path.join(cleaned_data_dir, f"{today}_*.csv")
    new_files = glob.glob(pattern)

    if new_files:
        print(f"📁 New files extracted today ({len(new_files)} files):")
        for file in sorted(new_files):
            filename = os.path.basename(file)
            file_size = os.path.getsize(file)
            print(f"  - {filename} ({file_size:,} bytes)")
    else:
        print("ℹ️ No new files found for today")

    return new_files

# Create the DAG
dag = DAG(
    'cleaned_data_extraction',
    default_args=default_args,
    description='Automatically extract new social media data based on latest extraction date',
    schedule_interval='@daily',  # Run daily at midnight
    catchup=False,
    max_active_runs=1,
    tags=['data_extraction', 'cleaned', 'social_media']
)

# Define tasks
extract_data_task = PythonOperator(
    task_id='extract_new_data',
    python_callable=extract_new_data,
    dag=dag
)

list_files_task = PythonOperator(
    task_id='list_new_files',
    python_callable=list_new_files,
    dag=dag
)

# Set task dependencies
extract_data_task >> list_files_task

# Create a manual trigger version of the DAG
manual_dag = DAG(
    'manual_data_extraction',
    default_args=default_args,
    description='Manually triggered data extraction for specific date ranges',
    schedule_interval=None,  # Manual trigger only
    catchup=False,
    max_active_runs=1,
    tags=['data_extraction', 'manual', 'social_media']
)

# Manual extraction task
manual_extract_task = PythonOperator(
    task_id='manual_extract_new_data',
    python_callable=extract_new_data,
    dag=manual_dag
)

manual_list_files_task = PythonOperator(
    task_id='manual_list_new_files',
    python_callable=list_new_files,
    dag=manual_dag
)

# Set task dependencies for manual DAG
manual_extract_task >> manual_list_files_task
