from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from data_pipeline.load_json_to_postgres import metadata, load_all_files, get_engine

def run_init_db():
    engine = get_engine()
    metadata.create_all(engine)
    print("All tables created (if not already present).")

def run_load_all_files():
    engine = get_engine()
    with engine.begin() as conn:
        load_all_files(conn)

with DAG(
    "load_all_social_media_raw",
    start_date=datetime(2024, 5, 1),
    schedule_interval=None,
    catchup=False,
    description="Loads all Reddit and YouTube data"
) as dag:
    init_db_task = PythonOperator(
        task_id="init_db",
        python_callable=run_init_db,
    )
    load_task = PythonOperator(
        task_id="load_all",
        python_callable=run_load_all_files,
    )
    init_db_task >> load_task
