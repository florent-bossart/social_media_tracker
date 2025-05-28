from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys
import os

# Add your project root/data_pipeline module to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../data_pipeline")))

from data_pipeline.load_json_to_postgres import engine, load_today_youtube_comment_update_file

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email_on_failure": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=10),
}

def load_today_update():
    with engine.begin() as conn:
        load_today_youtube_comment_update_file(conn)

with DAG(
    dag_id="load_today_youtube_comment_update",
    default_args=default_args,
    description="Load today's YouTube comment update file into warehouse",
    schedule_interval="0 7 * * *",  # Runs every day at 07:00 UTC
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["youtube", "comment_updates", "warehouse"]
) as dag:
    run_loader = PythonOperator(
        task_id="load_today_comment_update",
        python_callable=load_today_update
    )
