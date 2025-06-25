from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import requests

API_URL = "http://smt_api:8000/reddit/daily"

def trigger_reddit_daily_api():
    resp = requests.get(API_URL, timeout=1000)  # long timeout as reddit can return a large amount of data
    resp.raise_for_status()

with DAG(
    "fetch_reddit_daily_data",
    start_date=datetime(2024, 5, 1),
    schedule_interval="0 1 * * *",
    catchup=False,
    description="Triggers the Reddit daily fetch API",
    tags=["reddit", "daily", "fetch", "api"]
) as dag:
    PythonOperator(
        task_id="trigger_reddit_daily_api",
        python_callable=trigger_reddit_daily_api,
    )
