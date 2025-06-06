import os
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago

# Define the base path for the project to correctly locate scripts and data
PROJECT_BASE_PATH = "/home/florent.bossart/code/florent-bossart/social_media_tracker"
PIPELINE_SCRIPT_PATH = os.path.join(PROJECT_BASE_PATH, "run_complete_pipeline.py")
DATA_DIR = os.path.join(PROJECT_BASE_PATH, "data/intermediate/translated")
OUTPUT_DIR_BASE = os.path.join(PROJECT_BASE_PATH, "data/intermediate/youtube_pipeline_output") # Specific output for this DAG

# Default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='llm_youtube_processing_dag',
    default_args=default_args,
    description='Runs the LLM processing pipeline for YouTube comments using the file for the DAG execution date.',
    schedule_interval='@daily',  # Or your desired schedule
    start_date=days_ago(1),
    catchup=False,  # Set to True if you want to backfill
    tags=['llm', 'youtube'],
) as dag:

    # Dynamically determine the input filename based on the DAG's execution date
    # The filename format is YYYYMMDD_full_youtube_comments_cleaned_nllb_translated.csv
    # ds is the execution date as YYYY-MM-DD
    # ds_nodash is YYYYMMDD
    input_file_name_template = "{{ ds_nodash }}_full_youtube_comments_cleaned_nllb_translated.csv"
    input_file_path = os.path.join(DATA_DIR, input_file_name_template)

    # Create a specific output directory for this DAG run to avoid conflicts
    # This uses the DAG run's execution date to version the output
    output_dir_templated = os.path.join(OUTPUT_DIR_BASE, "{{ ds_nodash }}")

    run_youtube_pipeline = BashOperator(
        task_id='run_youtube_llm_pipeline',
        bash_command=f"""
            mkdir -p "{output_dir_templated}" && \\
            export PYTHONPATH="{PROJECT_BASE_PATH}:$PYTHONPATH" && \\
            python "{PIPELINE_SCRIPT_PATH}" \\
                --input "{input_file_path}" \\
                --output "{output_dir_templated}"
        """,
        cwd=PROJECT_BASE_PATH, # Ensure .env file is found
    )
