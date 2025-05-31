# filepath: /home/florent.bossart/code/florent-bossart/social_media_tracker/dags/llm_reddit_processing_dag.py
import os
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago

# Define the base path for the project to correctly locate scripts and data
PROJECT_BASE_PATH = "/home/florent.bossart/code/florent-bossart/social_media_tracker"
PIPELINE_SCRIPT_PATH = os.path.join(PROJECT_BASE_PATH, "data_pipeline/run_complete_pipeline.py")
DATA_DIR = os.path.join(PROJECT_BASE_PATH, "data/intermediate/translated") # Assuming reddit files are also here after translation
OUTPUT_DIR_BASE = os.path.join(PROJECT_BASE_PATH, "data/intermediate/reddit_pipeline_output") # Specific output for this DAG

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
    dag_id='llm_reddit_processing_dag',
    default_args=default_args,
    description='Runs the LLM processing pipeline for Reddit comments using the file for the DAG execution date.',
    schedule_interval='@daily',  # Or your desired schedule
    start_date=days_ago(1),
    catchup=False,  # Set to True if you want to backfill
    tags=['llm', 'reddit'],
) as dag:

    # Dynamically determine the input filename based on the DAG's execution date
    # The filename format is YYYYMMDD_full_reddit_comments_cleaned.csv
    # ds is the execution date as YYYY-MM-DD
    # ds_nodash is YYYYMMDD
    input_file_name_template = "{{ ds_nodash }}_full_reddit_comments_cleaned.csv"
    input_file_path = os.path.join(DATA_DIR, input_file_name_template)

    # Create a specific output directory for this DAG run to avoid conflicts
    # This uses the DAG run's execution date to version the output
    output_dir_templated = os.path.join(OUTPUT_DIR_BASE, "{{ ds_nodash }}")

    run_reddit_pipeline = BashOperator(
        task_id='run_reddit_llm_pipeline',
        bash_command=f"""
            set -e;
            cd /opt/airflow/projects/social_media_tracker && \\
            poetry run python data_pipeline/run_complete_pipeline.py \\
                --input {{{{ dag_run.conf.get(\'input_file\', \'/opt/airflow/projects/social_media_tracker/data/intermediate/20250530_full_reddit_comments_cleaned.csv\') }}}} \\
                --output {{{{ dag_run.conf.get(\'output_dir\', \'/opt/airflow/projects/social_media_tracker/data/intermediate\') }}}} \\
                --llm-host {{{{ dag_run.conf.get(\'llm_host\', \'http://host.docker.internal:11434\') }}}}
        """,
        cwd=PROJECT_BASE_PATH, # Ensure .env file is found
    )
