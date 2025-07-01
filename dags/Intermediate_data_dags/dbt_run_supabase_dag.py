from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator
from airflow.operators.bash import BashOperator
from docker.types import Mount
from datetime import datetime
import os

with DAG(
    "dbt_run_supabase",
    start_date=datetime(2024, 5, 1),
    schedule_interval=None,
    catchup=False,
    description="Runs dbt models against Supabase database"
) as dag:
    
    # Option 1: Using Docker (similar to current setup)
    dbt_run_supabase_docker = DockerOperator(
        task_id="dbt_run_supabase_docker",
        image="ghcr.io/dbt-labs/dbt-postgres:latest",
        api_version="auto",
        auto_remove='success',
        command="run --target supabase",
        docker_url="unix://var/run/docker.sock",
        # No network_mode needed for external Supabase connection
        working_dir="/app/dbt_social_media_tracker",
        environment={
            "ONLINE_DB_HOST": os.environ.get("ONLINE_DB_HOST"),
            "ONLINE_DB_PASSWORD": os.environ.get("ONLINE_DB_PASSWORD"),
            "ONLINE_DB_USER": os.environ.get("ONLINE_DB_USER"), 
            "ONLINE_DB_NAME": os.environ.get("ONLINE_DB_NAME"),
            "ONLINE_DB_PORT": os.environ.get("ONLINE_DB_PORT"),
            "DBT_PROFILES_DIR": "/app/dbt_social_media_tracker",
        },
        mounts=[
            Mount(
                source="/home/florent.bossart/code/florent-bossart/social_media_tracker/dbt_social_media_tracker",  # host path
                target="/app/dbt_social_media_tracker",  # container path
                type="bind"
            )
        ],
        mount_tmp_dir=False,
    )

    # Option 2: Using local Bash (if dbt is installed locally)
    dbt_run_supabase_local = BashOperator(
        task_id="dbt_run_supabase_local",
        bash_command="""
        cd /home/florent.bossart/code/florent-bossart/social_media_tracker && 
        ./run_dbt_supabase_docker.sh run
        """,
        env={
            "ONLINE_DB_HOST": os.environ.get("ONLINE_DB_HOST"),
            "ONLINE_DB_PASSWORD": os.environ.get("ONLINE_DB_PASSWORD"),
        }
    )

    # Specific task to run dashboard views
    dbt_run_dashboard_views_supabase = DockerOperator(
        task_id="dbt_run_dashboard_views_supabase",
        image="ghcr.io/dbt-labs/dbt-postgres:latest",
        api_version="auto",
        auto_remove='success',
        command="run --select artist_trends_enriched_dashboard author_influence_dashboard url_analysis_dashboard --target supabase",
        docker_url="unix://var/run/docker.sock",
        working_dir="/app/dbt_social_media_tracker",
        environment={
            "ONLINE_DB_HOST": os.environ.get("ONLINE_DB_HOST"),
            "ONLINE_DB_PASSWORD": os.environ.get("ONLINE_DB_PASSWORD"),
            "ONLINE_DB_USER": os.environ.get("ONLINE_DB_USER"), 
            "ONLINE_DB_NAME": os.environ.get("ONLINE_DB_NAME"),
            "ONLINE_DB_PORT": os.environ.get("ONLINE_DB_PORT"),
            "DBT_PROFILES_DIR": "/app/dbt_social_media_tracker",
        },
        mounts=[
            Mount(
                source="/home/florent.bossart/code/florent-bossart/social_media_tracker/dbt_social_media_tracker",
                target="/app/dbt_social_media_tracker",
                type="bind"
            )
        ],
        mount_tmp_dir=False,
    )

    # Set task dependencies - you can choose which approach to use
    # Uncomment the one you prefer:
    
    # For Docker approach:
    dbt_run_supabase_docker >> dbt_run_dashboard_views_supabase
    
    # For local approach (comment out the above and uncomment below):
    # dbt_run_supabase_local
