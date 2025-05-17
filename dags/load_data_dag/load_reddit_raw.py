from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from data_pipeline.init_db import main as init_db_main
from data_pipeline.load_json_to_postgres import load_reddit_files
from sqlalchemy import create_engine
import os

def get_engine():
    return create_engine(os.environ["AIRFLOW__DATABASE__SQL_ALCHEMY_CONN"])

def run_init_db():
    init_db_main()

def run_load_reddit_files():
    engine = get_engine()
    with engine.begin() as conn:
        load_reddit_files("data/reddit", conn)

with DAG(
    "load_reddit_raw",
    start_date=datetime(2024, 5, 1),
    schedule_interval=None,
    catchup=False,
    description="Loads only Reddit data"
) as dag:
    init_db_task = PythonOperator(
        task_id="init_db",
        python_callable=run_init_db,
    )
    load_task = PythonOperator(
        task_id="load_reddit",
        python_callable=run_load_reddit_files,
    )
    init_db_task >> load_task
