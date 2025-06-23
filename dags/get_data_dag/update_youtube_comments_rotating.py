from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import requests

API_URL = "http://smt_api:8000/update_youtube_comments_from_fetched_rotating"

def trigger_update_youtube_comments_rotating_api():
    resp = requests.post(API_URL, timeout=300)  # Reduced timeout to 5 minutes (300 seconds)
    resp.raise_for_status()
    return resp.json()

with DAG(
    "update_youtube_comments_rotating",
    start_date=datetime(2024, 5, 1),
    schedule_interval=None,
    catchup=False,
    description="Triggers the YouTube comments update from fetched data with rotation",
    tags=["youtube", "comments", "update", "rotating", "api"]
) as dag:
    PythonOperator(
        task_id="trigger_update_youtube_comments_rotating_api",
        python_callable=trigger_update_youtube_comments_rotating_api,
    )
