#!/usr/bin/env python3
"""
Airflow DAG Step 8: Load Analytics Data (Simple Version)

This DAG loads all analytics data into the database using the optimized loading script.
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

# Default arguments for the DAG
default_args = {
    'owner': 'data-pipeline',
    'depends_on_past': False,
    'start_date': datetime(2025, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Create DAG
dag = DAG(
    'step8_load_analytics_simple',
    default_args=default_args,
    description='Load all analytics data into database (Simple Version)',
    schedule_interval=None,  # Manual trigger
    catchup=False,
    max_active_runs=1,
    tags=['llm-pipeline', 'analytics', 'loading', 'simple']
)

# Single task that runs the loading script with auto-detection
load_analytics_task = BashOperator(
    task_id='load_analytics_auto_detect',
    bash_command="cd /app && python data_pipeline/load_analytics_auto.py",
    dag=dag,
)

# Optional verification task
verify_load_task = BashOperator(
    task_id='verify_load',
    bash_command="cd /app && python data_pipeline/verify_analytics_load.py",
    dag=dag,
)

# Define task dependencies
load_analytics_task >> verify_load_task
