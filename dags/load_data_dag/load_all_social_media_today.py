from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from data_pipeline.load_json_to_postgres import metadata, load_all_files_for_date, get_engine

def run_init_db():
    engine = get_engine()
    metadata.create_all(engine)
    print("All tables created (if not already present).")

def run_load_all_files_today(**context):
    engine = get_engine()
    date_str = context["logical_date"].strftime("%Y-%m-%d")
    with engine.begin() as conn:
        load_all_files_for_date(date_str, conn)

with DAG(
    "load_all_social_media_raw_today",
    start_date=datetime(2024, 5, 1),
    schedule_interval="20 1 * * *",
    catchup=False,
    description="Loads both Reddit and YouTube data for current execution date",
    tags=["social_media", "raw", "warehouse", "Daily"]
) as dag:
    init_db_task = PythonOperator(
        task_id="init_db",
        python_callable=run_init_db,
    )
    load_task = PythonOperator(
        task_id="load_all_today",
        python_callable=run_load_all_files_today,
        provide_context=True,
    )
    init_db_task >> load_task
