from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from data_pipeline.load_json_to_postgres import metadata, load_youtube_files, get_engine

def run_init_db():
    engine = get_engine()
    metadata.create_all(engine)
    print("All tables created (if not already present).")

def run_load_youtube_files():
    engine = get_engine()
    with engine.begin() as conn:
        load_youtube_files("data/youtube", conn)

with DAG(
    "load_youtube_raw",
    start_date=datetime(2024, 5, 1),
    schedule_interval=None,
    catchup=False,
    description="Loads only YouTube data"
) as dag:
    init_db_task = PythonOperator(
        task_id="init_db",
        python_callable=run_init_db,
    )
    load_task = PythonOperator(
        task_id="load_youtube",
        python_callable=run_load_youtube_files,
    )
    init_db_task >> load_task
