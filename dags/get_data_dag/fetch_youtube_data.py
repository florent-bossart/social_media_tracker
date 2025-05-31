from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import requests

API_URL = "http://smt_api:8000/youtube"  # Use the Docker service name as host inside Docker Compose

def trigger_youtube_api():
    resp = requests.get(API_URL, timeout=600)
    resp.raise_for_status()  # will fail task if not 2XX

with DAG(
    "fetch_youtube_data",
    start_date=datetime(2024, 5, 1),
    schedule_interval=None,
    catchup=False,
    description="Triggers the YouTube data fetch API",
    tags=["youtube", "fetch", "api"]
) as dag:
    PythonOperator(
        task_id="trigger_youtube_api",
        python_callable=trigger_youtube_api,
    )
