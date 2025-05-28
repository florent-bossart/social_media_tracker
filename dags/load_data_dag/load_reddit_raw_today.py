from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from data_pipeline.load_json_to_postgres import metadata, load_reddit_files_for_date, get_engine

def run_init_db():
    engine = get_engine()
    metadata.create_all(engine)
    print("All tables created (if not already present).")

def run_load_reddit_files_today(**context):
    engine = get_engine()
    # Get the Airflow logical/execution date as YYYY-MM-DD
    date_str = context["logical_date"].strftime("%Y-%m-%d")
    with engine.begin() as conn:
        load_reddit_files_for_date(date_str, conn)

with DAG(
    "load_reddit_raw_today",
    start_date=datetime(2024, 5, 1),
    schedule_interval=None,
    catchup=False,
    description="Loads only Reddit data for current execution date",
    tags=["reddit", "raw", "warehouse", "Daily"]
) as dag:
    init_db_task = PythonOperator(
        task_id="init_db",
        python_callable=run_init_db,
    )
    load_task = PythonOperator(
        task_id="load_reddit_today",
        python_callable=run_load_reddit_files_today,
        provide_context=True,
    )
    init_db_task >> load_task
