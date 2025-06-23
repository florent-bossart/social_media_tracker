from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

# This DAG extracts full cleaned Reddit data and YouTube data to intermediate CSV files.
# It's not part of the main pipeline - that's why it's preceded by zopt (z to appear at the end, opt for optional)


default_args = {
    "owner": "airflow",
    "retries": 1,
}

with DAG(
    dag_id="zopt_extract_full_data_sql_to_csv",
    default_args=default_args,
    description="Extracts cleaned Reddit data and YouTube data to intermediate CSV files",
    schedule_interval=None,
    start_date=datetime(2024, 5, 1),
    catchup=False,
) as dag:

    run_extraction = BashOperator(
        task_id="run_extract_to_csv",
        bash_command="poetry run python /app/data_pipeline/extract_cleaned_data_full.py",
        cwd="/app/airflow",
    )
