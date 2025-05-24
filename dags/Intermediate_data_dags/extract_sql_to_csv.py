from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

default_args = {
    "owner": "airflow",
    "retries": 1,
}

with DAG(
    dag_id="extract_to_csv",
    default_args=default_args,
    description="Extracts cleaned Reddit and YouTube comments to intermediate CSV files",
    schedule_interval=None,  # Set your desired schedule, e.g. '@daily'
    start_date=datetime(2024, 5, 1),
    catchup=False,
) as dag:

    run_extraction = BashOperator(
        task_id="run_extract_to_csv",
        bash_command="poetry run python /app/data_pipeline/extract_cleaned_comments.py",
        cwd="/app/airflow",
    )
