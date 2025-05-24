from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator
from docker.types import Mount
from datetime import datetime
import os

with DAG(
    "dbt_run",
    start_date=datetime(2024, 5, 1),
    schedule_interval=None,
    catchup=False,
    description="Runs dbt models in the dbt container"
) as dag:
    dbt_run = DockerOperator(
        task_id="dbt_run",
        image="ghcr.io/dbt-labs/dbt-postgres:latest",
        api_version="auto",
        auto_remove='success',
        command="run",
        docker_url="unix://var/run/docker.sock",
        network_mode="social_media_tracker_default",
        working_dir="/app/airflow/dbt_social_media_tracker",  # <-- match the mount target
        environment={
            "DBT_DB_PASSWORD": os.environ.get("DBT_DB_PASSWORD"),
            "DBT_PROFILES_DIR": "/app/airflow/dbt_social_media_tracker",  # <-- match the mount target!
        },
        mounts=[
            Mount(
                source="/home/florent.bossart/code/florent-bossart/social_media_tracker/dbt_social_media_tracker",  # host path
                target="/app/airflow/dbt_social_media_tracker",  # container path (must match above)
                type="bind"
            )
        ],
        mount_tmp_dir=False,
    )
