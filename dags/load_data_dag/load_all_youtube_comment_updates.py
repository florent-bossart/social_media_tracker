from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys
import os

# Add your project root/data_pipeline module to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../data_pipeline")))

from data_pipeline.load_json_to_postgres import engine, load_all_youtube_comment_update_files

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email_on_failure": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=10),
}

def load_all_updates():
    with engine.begin() as conn:
        load_all_youtube_comment_update_files(conn)

with DAG(
    dag_id="load_all_youtube_comment_updates",
    default_args=default_args,
    description="Load all YouTube comment update files into warehouse",
    schedule_interval=None,  # Set to desired schedule
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["youtube", "comment_updates", "warehouse"]
) as dag:
    run_loader = PythonOperator(
        task_id="load_all_comment_updates",
        python_callable=load_all_updates
    )
