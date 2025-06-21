#!/usr/bin/env python3
"""
Complete LLM Pipeline DAG - STRICT SEQUENTIAL EXECUTION
Orchestrates the full pipeline: DBT → Data Extraction → LLM Processing → Data Loading → DBT
All tasks run sequentially to ensure proper dependencies and data consistency.
"""

import os
from datetime import datetime, timedelta
from pathlib import Path

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.providers.docker.operators.docker import DockerOperator
from docker.types import Mount
from airflow.utils.dates import days_ago

# Import the functions from individual step DAGs
import sys
sys.path.append('/opt/airflow/dags/llm_pipeline')

# Define the base path for the project
PROJECT_BASE_PATH = "/app"

# Import functions from step DAGs
def import_step_functions():
    """Import functions from individual step DAGs using a simpler approach."""
    try:
        # Simple approach: define the functions inline to avoid import issues

        def translate_latest_youtube_file(**context):
            """Translate the latest YouTube cleaned file using the exact same approach as the working DAG."""
            import sys
            import subprocess
            import glob
            import os
            from pathlib import Path

            print("Starting YouTube translation task...")

            # Add project root to Python path (same as working DAG)
            sys.path.append("/app")

            # Import file detection utilities (same as working DAG)
            sys.path.append("/app/airflow/dags/llm_pipeline")
            from file_detection_utils import find_latest_cleaned_file

            # Find the latest YouTube cleaned file (same as working DAG)
            latest_file = find_latest_cleaned_file("youtube", "/app/airflow/data/intermediate")

            if not latest_file:
                raise FileNotFoundError("No YouTube cleaned file found for translation")

            print(f"Found latest YouTube cleaned file: {latest_file}")

            # Extract just the filename for the output
            input_filename = Path(latest_file).name

            # Set up output directory (same as working DAG)
            output_dir = "/app/airflow/data/intermediate/translated"
            os.makedirs(output_dir, exist_ok=True)

            # Run the memory-optimized translation script (exact same command as working DAG)
            cmd = [
                "poetry", "run", "python",
                "../data_pipeline/translate_youtube_comments_optimized.py",  # Use optimized version
                "--input-file", latest_file,
                "--output-dir", output_dir,
                "--column", "comment_text"
            ]

            print(f"Running optimized translation command: {' '.join(cmd)}")

            # Set memory limits using environment variables (same as working DAG)
            env = os.environ.copy()
            env.update({
                'PYTORCH_CUDA_ALLOC_CONF': 'max_split_size_mb:512',
                'MALLOC_ARENA_MAX': '2',
                'OMP_NUM_THREADS': '1',
                'TOKENIZERS_PARALLELISM': 'false'  # Disable tokenizer parallelism to save memory
            })

            # Change to project directory to ensure .env file is found (same as working DAG)
            result = subprocess.run(cmd, cwd="/app/airflow", capture_output=True, text=True, env=env)

            if result.returncode != 0:
                print(f"Translation failed with return code {result.returncode}")
                print(f"STDOUT: {result.stdout}")
                print(f"STDERR: {result.stderr}")
                raise RuntimeError(f"Translation failed: {result.stderr}")

            print(f"Translation completed successfully")
            print(f"Output: {result.stdout}")

            # Return the output file path for downstream tasks
            output_filename = input_filename.replace('_cleaned.csv', '_cleaned_nllb_translated.csv')
            output_path = f"{output_dir}/{output_filename}"

            return {
                "input_file": latest_file,
                "output_file": output_path,
                "status": "success"
            }

        def extract_entities_youtube(**context):
            """Run entity extraction on the latest translated YouTube file."""
            import sys
            import subprocess
            import os

            print("Starting YouTube entity extraction...")

            # Add project root to Python path
            sys.path.append("/app")

            # Import file detection utilities
            sys.path.append("/app/airflow/dags/llm_pipeline")
            from file_detection_utils import find_latest_translated_file, find_latest_entity_file

            # Find the latest YouTube translated file
            latest_file = find_latest_translated_file("youtube", "/app/airflow/data/intermediate")

            if not latest_file:
                raise FileNotFoundError("No YouTube translated file found for entity extraction")

            print(f"Found latest YouTube translated file: {latest_file}")

            # Set up output directory
            output_dir = "/app/airflow/data/intermediate/entity_extraction"
            os.makedirs(output_dir, exist_ok=True)

            # Get LLM host from environment
            llm_host = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
            print(f"Using LLM host: {llm_host}")

            # Run the entity extraction script
            cmd = [
                "poetry", "run", "python",
                "/app/data_pipeline/run_specific_entity_extraction.py",
                "--input_file", latest_file,
                "--platform", "youtube",
                "--output_dir", output_dir
            ]

            # Add LLM host if available
            if llm_host:
                cmd.extend(["--ollama-host", llm_host])

            print(f"Running entity extraction command: {' '.join(cmd)}")

            # Change to project directory to ensure .env file is found
            result = subprocess.run(cmd, cwd="/app/airflow", capture_output=True, text=True)

            if result.returncode != 0:
                print(f"Entity extraction failed with return code {result.returncode}")
                print(f"STDOUT: {result.stdout}")
                print(f"STDERR: {result.stderr}")
                raise RuntimeError(f"Entity extraction failed: {result.stderr}")

            print(f"Entity extraction completed successfully")
            print(f"Output: {result.stdout}")

            # Find the generated output file
            output_file = find_latest_entity_file("youtube", "/app/airflow/data/intermediate")

            return {
                "input_file": latest_file,
                "output_file": output_file,
                "status": "success"
            }

        def extract_entities_reddit(**context):
            """Run entity extraction on the latest cleaned Reddit file."""
            import sys
            import subprocess
            import os

            print("Starting Reddit entity extraction...")

            # Add project root to Python path
            sys.path.append("/app")

            # Import file detection utilities
            sys.path.append("/app/airflow/dags/llm_pipeline")
            from file_detection_utils import find_latest_cleaned_file, find_latest_entity_file

            # Find the latest Reddit cleaned file
            latest_file = find_latest_cleaned_file("reddit", "/app/airflow/data/intermediate")

            if not latest_file:
                raise FileNotFoundError("No Reddit cleaned file found for entity extraction")

            print(f"Found latest Reddit cleaned file: {latest_file}")

            # Set up output directory
            output_dir = "/app/airflow/data/intermediate/entity_extraction"
            os.makedirs(output_dir, exist_ok=True)

            # Get LLM host from environment
            llm_host = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
            print(f"Using LLM host: {llm_host}")

            # Run the entity extraction script
            cmd = [
                "poetry", "run", "python",
                "/app/data_pipeline/run_specific_entity_extraction.py",
                "--input_file", latest_file,
                "--platform", "reddit",
                "--output_dir", output_dir
            ]

            # Add LLM host if available
            if llm_host:
                cmd.extend(["--ollama-host", llm_host])

            print(f"Running entity extraction command: {' '.join(cmd)}")

            # Change to project directory to ensure .env file is found
            result = subprocess.run(cmd, cwd="/app/airflow", capture_output=True, text=True)

            if result.returncode != 0:
                print(f"Entity extraction failed with return code {result.returncode}")
                print(f"STDOUT: {result.stdout}")
                print(f"STDERR: {result.stderr}")
                raise RuntimeError(f"Entity extraction failed: {result.stderr}")

            print(f"Entity extraction completed successfully")
            print(f"Output: {result.stdout}")

            # Find the generated output file
            output_file = find_latest_entity_file("reddit", "/app/airflow/data/intermediate")

            return {
                "input_file": latest_file,
                "output_file": output_file,
                "status": "success"
            }

        def analyze_sentiment_youtube(**context):
            """Run sentiment analysis on the latest YouTube entity file."""
            import sys
            import subprocess
            import os

            print("Starting YouTube sentiment analysis...")

            # Add project root to Python path
            sys.path.append("/app")

            # Import file detection utilities
            sys.path.append("/app/airflow/dags/llm_pipeline")
            from file_detection_utils import find_latest_entity_file, find_latest_sentiment_file

            # Find the latest YouTube entity file
            latest_file = find_latest_entity_file("youtube", "/app/airflow/data/intermediate")

            if not latest_file:
                raise FileNotFoundError("No YouTube entity file found for sentiment analysis")

            print(f"Found latest YouTube entity file: {latest_file}")

            # Set up output directory
            output_dir = "/app/airflow/data/intermediate/sentiment_analysis"
            os.makedirs(output_dir, exist_ok=True)

            # Get LLM host from environment
            llm_host = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
            print(f"Using LLM host: {llm_host}")

            # Run the sentiment analysis script
            cmd = [
                "poetry", "run", "python",
                "/app/data_pipeline/run_sentiment_pipeline.py",
                "youtube",
                "--input_file", latest_file,
                "--output_dir", output_dir
            ]

            # Add LLM host if available
            if llm_host:
                cmd.extend(["--ollama-host", llm_host])

            print(f"Running sentiment analysis command: {' '.join(cmd)}")

            # Change to project directory to ensure .env file is found
            result = subprocess.run(cmd, cwd="/app/airflow", capture_output=True, text=True)

            if result.returncode != 0:
                print(f"Sentiment analysis failed with return code {result.returncode}")
                print(f"STDOUT: {result.stdout}")
                print(f"STDERR: {result.stderr}")
                raise RuntimeError(f"Sentiment analysis failed: {result.stderr}")

            print(f"Sentiment analysis completed successfully")
            print(f"Output: {result.stdout}")

            # Find the generated output file
            output_file = find_latest_sentiment_file("youtube", "/app/airflow/data/intermediate")

            return {
                "input_file": latest_file,
                "output_file": output_file,
                "status": "success"
            }

        def analyze_sentiment_reddit(**context):
            """Run sentiment analysis on the latest Reddit entity file."""
            import sys
            import subprocess
            import os

            print("Starting Reddit sentiment analysis...")

            # Add project root to Python path
            sys.path.append("/app")

            # Import file detection utilities
            sys.path.append("/app/airflow/dags/llm_pipeline")
            from file_detection_utils import find_latest_entity_file, find_latest_sentiment_file

            # Find the latest Reddit entity file
            latest_file = find_latest_entity_file("reddit", "/app/airflow/data/intermediate")

            if not latest_file:
                raise FileNotFoundError("No Reddit entity file found for sentiment analysis")

            print(f"Found latest Reddit entity file: {latest_file}")

            # Set up output directory
            output_dir = "/app/airflow/data/intermediate/sentiment_analysis"
            os.makedirs(output_dir, exist_ok=True)

            # Get LLM host from environment
            llm_host = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
            print(f"Using LLM host: {llm_host}")

            # Run the sentiment analysis script
            cmd = [
                "poetry", "run", "python",
                "/app/data_pipeline/run_sentiment_pipeline.py",
                "reddit",
                "--input_file", latest_file,
                "--output_dir", output_dir
            ]

            # Add LLM host if available
            if llm_host:
                cmd.extend(["--ollama-host", llm_host])

            print(f"Running sentiment analysis command: {' '.join(cmd)}")

            # Change to project directory to ensure .env file is found
            result = subprocess.run(cmd, cwd="/app/airflow", capture_output=True, text=True)

            if result.returncode != 0:
                print(f"Sentiment analysis failed with return code {result.returncode}")
                print(f"STDOUT: {result.stdout}")
                print(f"STDERR: {result.stderr}")
                raise RuntimeError(f"Sentiment analysis failed: {result.stderr}")

            print(f"Sentiment analysis completed successfully")
            print(f"Output: {result.stdout}")

            # Find the generated output file
            output_file = find_latest_sentiment_file("reddit", "/app/airflow/data/intermediate")

            return {
                "input_file": latest_file,
                "output_file": output_file,
                "status": "success"
            }

        def detect_trends_combined(**context):
            """Run combined trend detection on the latest sentiment analysis files."""
            import sys
            import subprocess
            import os

            print("Starting combined trend detection...")

            # Add project root to Python path
            sys.path.append("/app")

            # Import file detection utilities
            sys.path.append("/app/airflow/dags/llm_pipeline")
            from file_detection_utils import find_latest_sentiment_file

            # Find the latest sentiment files for both platforms
            youtube_sentiment = find_latest_sentiment_file("youtube", "/app/airflow/data/intermediate")
            reddit_sentiment = find_latest_sentiment_file("reddit", "/app/airflow/data/intermediate")

            if not youtube_sentiment:
                raise FileNotFoundError("No YouTube sentiment file found for trend detection")
            if not reddit_sentiment:
                raise FileNotFoundError("No Reddit sentiment file found for trend detection")

            print(f"Found latest YouTube sentiment file: {youtube_sentiment}")
            print(f"Found latest Reddit sentiment file: {reddit_sentiment}")

            # Set up output directory
            output_dir = "/app/airflow/data/intermediate/trend_analysis"
            os.makedirs(output_dir, exist_ok=True)

            # Run the combined trend detection script
            cmd = [
                "poetry", "run", "python",
                "/app/llm_enrichment/trend/trend_detection_combined_standalone.py",
                "--input_file_youtube", youtube_sentiment,
                "--input_file_reddit", reddit_sentiment,
                "--output_dir", output_dir,
                "--log_level", "INFO"
            ]

            print(f"Running trend detection command: {' '.join(cmd)}")

            # Change to project directory to ensure .env file is found
            result = subprocess.run(cmd, cwd="/app/airflow", capture_output=True, text=True)

            if result.returncode != 0:
                print(f"Trend detection failed with return code {result.returncode}")
                print(f"STDOUT: {result.stdout}")
                print(f"STDERR: {result.stderr}")
                raise RuntimeError(f"Trend detection failed: {result.stderr}")

            print(f"Trend detection completed successfully")
            print(f"Output: {result.stdout}")

            # Find the generated output files
            from file_detection_utils import find_latest_trend_files
            artist_file, genre_file, temporal_file, summary_file = find_latest_trend_files("/app/airflow/data/intermediate")

            return {
                "input_youtube": youtube_sentiment,
                "input_reddit": reddit_sentiment,
                "output_artist": artist_file,
                "output_genre": genre_file,
                "output_temporal": temporal_file,
                "output_summary": summary_file,
                "status": "success"
            }

        def generate_summary(**context):
            """Run summarization on the latest trend detection files."""
            import sys
            import subprocess
            import os
            import re

            print("Starting summary generation...")

            # Add project root to Python path
            sys.path.append("/app")

            # Import file detection utilities
            sys.path.append("/app/airflow/dags/llm_pipeline")
            from file_detection_utils import find_latest_trend_files

            # Helper functions for date and source extraction
            def extract_date_from_filename(filename: str):
                """Extract YYYYMMDD date from filename."""
                match = re.search(r'(\d{8})', filename)
                return match.group(1) if match else None

            def extract_source_tag_from_filename(filename: str):
                """Extract source tag (combined, youtube, reddit) from filename."""
                if 'combined' in filename.lower():
                    return 'combined'
                elif 'youtube' in filename.lower():
                    return 'youtube'
                elif 'reddit' in filename.lower():
                    return 'reddit'
                else:
                    return 'unknown'

            # Find the latest trend files
            artist_file, genre_file, temporal_file, summary_file = find_latest_trend_files("/app/airflow/data/intermediate")

            if not summary_file:
                raise FileNotFoundError("No trend summary file found for summarization")

            print(f"Found latest trend files:")
            print(f"  Artist: {artist_file}")
            print(f"  Genre: {genre_file}")
            print(f"  Temporal: {temporal_file}")
            print(f"  Summary: {summary_file}")

            # Extract date and source tags from the files
            date_tag = extract_date_from_filename(summary_file)
            source_tag = extract_source_tag_from_filename(summary_file)

            if not date_tag:
                raise ValueError(f"Could not extract date from filename: {summary_file}")

            print(f"Extracted date tag: {date_tag}")
            print(f"Extracted source tag: {source_tag}")

            # Set up input and output directories
            input_dir = "/app/airflow/data/intermediate/trend_analysis"
            output_dir = "/app/airflow/data/intermediate/summarization"
            os.makedirs(output_dir, exist_ok=True)

            # Get LLM host from environment
            llm_host = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
            print(f"Using LLM host: {llm_host}")

            # Run the summarization script
            cmd = [
                "poetry", "run", "python",
                "/app/llm_enrichment/summarization/summarization_standalone.py",
                "--input-dir", input_dir,
                "--output-dir", output_dir,
                "--date-tag", date_tag,
                "--source-tag", source_tag,
                "--log_level", "INFO"
            ]

            # Add LLM host if available
            if llm_host:
                cmd.extend(["--ollama-host", llm_host])

            print(f"Running summarization command: {' '.join(cmd)}")

            # Change to project directory to ensure .env file is found
            result = subprocess.run(cmd, cwd="/app/airflow", capture_output=True, text=True)

            if result.returncode != 0:
                print(f"Summarization failed with return code {result.returncode}")
                print(f"STDOUT: {result.stdout}")
                print(f"STDERR: {result.stderr}")
                raise RuntimeError(f"Summarization failed: {result.stderr}")

            print(f"Summarization completed successfully")
            print(f"Output: {result.stdout}")

            # Expected output files
            insights_file = f"{output_dir}/trend_insights_{date_tag}_{source_tag}.json"
            metrics_file = f"{output_dir}/trend_insights_{date_tag}_{source_tag}_metrics.csv"

            return {
                "input_summary": summary_file,
                "input_artist": artist_file,
                "input_genre": genre_file,
                "input_temporal": temporal_file,
                "output_insights": insights_file,
                "output_metrics": metrics_file,
                "date_tag": date_tag,
                "source_tag": source_tag,
                "status": "success"
            }

        return {
            'translate': translate_latest_youtube_file,
            'entity_youtube': extract_entities_youtube,
            'entity_reddit': extract_entities_reddit,
            'sentiment_youtube': analyze_sentiment_youtube,
            'sentiment_reddit': analyze_sentiment_reddit,
            'trend_combined': detect_trends_combined,
            'summarization': generate_summary
        }

    except Exception as e:
        print(f"Warning: Could not create step functions: {e}")
        return None

# Import cleaned data extraction function
def import_cleaned_data_function():
    """Import cleaned data extraction function."""
    try:
        # Use the working function from the existing cleaned_data_extraction DAG
        import sys
        import subprocess
        import os
        import glob
        import re
        from datetime import datetime, timedelta

        def extract_new_data():
            """Extract new social media data from existing working DAG."""
            print("🚀 Starting automated data extraction...")

            # Get latest extraction date
            def get_latest_extraction_date():
                """Find the latest extraction date from existing cleaned data files."""
                pattern = "/app/airflow/data/intermediate/Cleaned_data/*_comments_cleaned.csv"
                files = glob.glob(pattern)

                if not files:
                    print("No existing cleaned data files found")
                    return None

                extraction_dates = []
                for file in files:
                    filename = os.path.basename(file)
                    match = re.search(r'^(\d{8})_', filename)
                    if match:
                        extraction_date_str = match.group(1)
                        if len(extraction_date_str) == 8:
                            formatted_date = f"{extraction_date_str[:4]}-{extraction_date_str[4:6]}-{extraction_date_str[6:8]}"
                            extraction_dates.append(formatted_date)
                            print(f"Found extraction date: {formatted_date} from file: {filename}")

                if not extraction_dates:
                    print("No valid extraction dates found")
                    return None

                latest_date = max(extraction_dates)
                print(f"Latest extraction date found: {latest_date}")
                return latest_date

            def calculate_next_extraction_date(latest_extraction_date):
                """Calculate the data date to extract (day after latest extraction)."""
                if latest_extraction_date is None:
                    # Default to extract from a week ago if no files found
                    return (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')

                latest_dt = datetime.strptime(latest_extraction_date, '%Y-%m-%d')
                next_date = latest_dt + timedelta(days=1)
                return next_date.strftime('%Y-%m-%d')

            # Get the latest extraction date and calculate what data date to extract from
            latest_extraction_date = get_latest_extraction_date()
            data_date_to_extract = calculate_next_extraction_date(latest_extraction_date)

            # Check if extraction is needed (don't extract future dates)
            today = datetime.now().strftime('%Y-%m-%d')
            if data_date_to_extract > today:
                print(f"ℹ️ Data is up-to-date. Next extraction date {data_date_to_extract} is in the future.")
                return {"status": "no_new_data", "latest_date": latest_extraction_date}

            # Construct the extraction command using the correct path
            cmd = [
                "poetry", "run", "python",
                "../data_pipeline/extract_cleaned_comments_by_date.py",  # Relative path from /app/airflow
                "--date", data_date_to_extract,
                "--source", "both"
            ]

            print(f"Running extraction command: {' '.join(cmd)}")
            print(f"This will extract data with fetch_date >= {data_date_to_extract}")

            try:
                # Run the extraction command
                result = subprocess.run(
                    cmd,
                    cwd="/app/airflow",  # Run from /app/airflow where pyproject.toml is located
                    capture_output=True,
                    text=True,
                    timeout=1800  # 30 minute timeout
                )

                print(f"Extraction completed with return code: {result.returncode}")
                print(f"STDOUT: {result.stdout}")

                if result.stderr:
                    print(f"STDERR: {result.stderr}")

                if result.returncode == 0:
                    print("✅ Data extraction completed successfully")
                    return {"status": "success", "date": data_date_to_extract}
                else:
                    print(f"❌ Data extraction failed with return code: {result.returncode}")
                    return {"status": "error", "return_code": result.returncode, "stderr": result.stderr}

            except subprocess.TimeoutExpired:
                print("❌ Data extraction timed out after 30 minutes")
                return {"status": "timeout"}
            except Exception as e:
                print(f"❌ Error during data extraction: {str(e)}")
                return {"status": "error", "error": str(e)}

        return extract_new_data

    except Exception as e:
        print(f"Warning: Could not create cleaned data extraction function: {e}")
        return None

# Default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 0,  # No retries as requested
}

# Create the DAG
with DAG(
    dag_id='llm_complete_pipeline_full',
    default_args=default_args,
    description='Complete Pipeline: DBT → Data Extraction → LLM Processing → Data Loading → DBT (STRICT SEQUENTIAL)',
    schedule_interval=None,  # Manual execution only
    start_date=days_ago(1),
    catchup=False,
    max_active_tasks=1,  # Force sequential execution - only one task at a time
    max_active_runs=1,   # Only one DAG run at a time
    tags=['llm', 'complete', 'pipeline', 'full', 'sequential'],
) as dag:

    # === STEP 0: Clean up existing dashboard views and DBT state ===
    cleanup_dashboard_views = DockerOperator(
        task_id="cleanup_dashboard_views",
        image="ghcr.io/dbt-labs/dbt-postgres:latest",
        api_version="auto",
        auto_remove='success',
        command=["clean"],
        docker_url="unix://var/run/docker.sock",
        network_mode="social_media_tracker_default",
        working_dir="/app/airflow/dbt_social_media_tracker",
        environment={
            "DBT_DB_PASSWORD": os.environ.get("DBT_DB_PASSWORD"),
            "DBT_PROFILES_DIR": "/app/airflow/dbt_social_media_tracker",
        },
        mounts=[
            Mount(
                source="/home/florent.bossart/code/florent-bossart/social_media_tracker/dbt_social_media_tracker",
                target="/app/airflow/dbt_social_media_tracker",
                type="bind"
            )
        ],
        mount_tmp_dir=False,
    )

    # === STEP 1: Initial DBT Run ===
    initial_dbt_run = DockerOperator(
        task_id="initial_dbt_run",
        image="ghcr.io/dbt-labs/dbt-postgres:latest",
        api_version="auto",
        auto_remove='success',
        command=["run"],
        docker_url="unix://var/run/docker.sock",
        network_mode="social_media_tracker_default",
        working_dir="/app/airflow/dbt_social_media_tracker",
        environment={
            "DBT_DB_PASSWORD": os.environ.get("DBT_DB_PASSWORD"),
            "DBT_PROFILES_DIR": "/app/airflow/dbt_social_media_tracker",
        },
        mounts=[
            Mount(
                source="/home/florent.bossart/code/florent-bossart/social_media_tracker/dbt_social_media_tracker",
                target="/app/airflow/dbt_social_media_tracker",
                type="bind"
            )
        ],
        mount_tmp_dir=False,
    )

    initial_dbt_dashboard_views = DockerOperator(
        task_id="initial_dbt_dashboard_views",
        image="ghcr.io/dbt-labs/dbt-postgres:latest",
        api_version="auto",
        auto_remove='success',
        command=["run", "--select", "artist_trends_enriched_dashboard", "author_influence_dashboard", "url_analysis_dashboard"],
        docker_url="unix://var/run/docker.sock",
        network_mode="social_media_tracker_default",
        working_dir="/app/airflow/dbt_social_media_tracker",
        environment={
            "DBT_DB_PASSWORD": os.environ.get("DBT_DB_PASSWORD"),
            "DBT_PROFILES_DIR": "/app/airflow/dbt_social_media_tracker",
        },
        mounts=[
            Mount(
                source="/home/florent.bossart/code/florent-bossart/social_media_tracker/dbt_social_media_tracker",
                target="/app/airflow/dbt_social_media_tracker",
                type="bind"
            )
        ],
        mount_tmp_dir=False,
    )

    # === STEP 2: Cleaned Data Extraction ===
    cleaned_data_extraction_func = import_cleaned_data_function()

    if cleaned_data_extraction_func:
        extract_cleaned_data = PythonOperator(
            task_id='extract_cleaned_data',
            python_callable=cleaned_data_extraction_func,
            execution_timeout=None,
        )
    else:
        # Fallback: create a simple task that logs the issue
        def fallback_data_extraction(**context):
            """Fallback data extraction that explains the issue."""
            print("Data extraction function could not be imported.")
            print("This step would normally extract new social media data.")
            print("Continuing with existing data for LLM processing...")
            return {"status": "skipped", "reason": "import_failed"}

        extract_cleaned_data = PythonOperator(
            task_id='extract_cleaned_data',
            python_callable=fallback_data_extraction,
            execution_timeout=None,
        )

    # === STEPS 3-9: LLM Processing Steps ===
    step_functions = import_step_functions()

    if step_functions:
        # Step 3: Translate YouTube
        step3_translate = PythonOperator(
            task_id='step3_translate_youtube',
            python_callable=step_functions['translate'],
            execution_timeout=None,
        )

        # Step 4: Entity extraction YouTube (depends on step 3)
        step4_entity_youtube = PythonOperator(
            task_id='step4_entity_youtube',
            python_callable=step_functions['entity_youtube'],
            execution_timeout=None,
        )

        # Step 5: Entity extraction Reddit (parallel to step 4)
        step5_entity_reddit = PythonOperator(
            task_id='step5_entity_reddit',
            python_callable=step_functions['entity_reddit'],
            execution_timeout=None,
        )

        # Step 6: Sentiment analysis YouTube (depends on step 4)
        step6_sentiment_youtube = PythonOperator(
            task_id='step6_sentiment_youtube',
            python_callable=step_functions['sentiment_youtube'],
            execution_timeout=None,
        )

        # Step 7: Sentiment analysis Reddit (depends on step 5)
        step7_sentiment_reddit = PythonOperator(
            task_id='step7_sentiment_reddit',
            python_callable=step_functions['sentiment_reddit'],
            execution_timeout=None,
        )

        # Step 8: Combined trend detection (depends on steps 6 and 7)
        step8_trend_combined = PythonOperator(
            task_id='step8_trend_combined',
            python_callable=step_functions['trend_combined'],
            execution_timeout=None,
        )

        # Step 9: Summarization (depends on step 8)
        step9_summarization = PythonOperator(
            task_id='step9_summarization',
            python_callable=step_functions['summarization'],
            execution_timeout=None,
        )

        # === STEP 10: Load Analytics Data (without truncate) ===
        def load_analytics_data_func(**context):
            """Load analytics data without truncating existing data."""
            import subprocess
            import os

            try:
                # Change to the project directory
                os.chdir('/app')

                # Run the analytics data loading script
                result = subprocess.run(
                    ["python", "data_pipeline/load_analytics_auto.py"],
                    capture_output=True,
                    text=True,
                    cwd='/app'
                )

                print(f"Analytics loading completed with return code: {result.returncode}")
                print(f"STDOUT: {result.stdout}")

                if result.stderr:
                    print(f"STDERR: {result.stderr}")

                if result.returncode != 0:
                    raise Exception(f"Analytics loading failed with return code {result.returncode}")

                return {"status": "success"}

            except Exception as e:
                print(f"Error loading analytics data: {e}")
                raise

        load_analytics_data = PythonOperator(
            task_id='load_analytics_data',
            python_callable=load_analytics_data_func,
        )

        # === STEP 11: Final DBT Run ===
        final_dbt_run = DockerOperator(
            task_id="final_dbt_run",
            image="ghcr.io/dbt-labs/dbt-postgres:latest",
            api_version="auto",
            auto_remove='success',
            command=["run"],
            docker_url="unix://var/run/docker.sock",
            network_mode="social_media_tracker_default",
            working_dir="/app/airflow/dbt_social_media_tracker",
            environment={
                "DBT_DB_PASSWORD": os.environ.get("DBT_DB_PASSWORD"),
                "DBT_PROFILES_DIR": "/app/airflow/dbt_social_media_tracker",
            },
            mounts=[
                Mount(
                    source="/home/florent.bossart/code/florent-bossart/social_media_tracker/dbt_social_media_tracker",
                    target="/app/airflow/dbt_social_media_tracker",
                    type="bind"
                )
            ],
            mount_tmp_dir=False,
        )

        final_dbt_dashboard_views = DockerOperator(
            task_id="final_dbt_dashboard_views",
            image="ghcr.io/dbt-labs/dbt-postgres:latest",
            api_version="auto",
            auto_remove='success',
            command=["run", "--select", "artist_trends_enriched_dashboard", "author_influence_dashboard", "url_analysis_dashboard"],
            docker_url="unix://var/run/docker.sock",
            network_mode="social_media_tracker_default",
            working_dir="/app/airflow/dbt_social_media_tracker",
            environment={
                "DBT_DB_PASSWORD": os.environ.get("DBT_DB_PASSWORD"),
                "DBT_PROFILES_DIR": "/app/airflow/dbt_social_media_tracker",
            },
            mounts=[
                Mount(
                    source="/home/florent.bossart/code/florent-bossart/social_media_tracker/dbt_social_media_tracker",
                    target="/app/airflow/dbt_social_media_tracker",
                    type="bind"
                )
            ],
            mount_tmp_dir=False,
        )

        # === DEFINE DEPENDENCIES ===
        # STRICT SEQUENTIAL EXECUTION - No parallel tasks

        # Phase 0: Cleanup
        cleanup_dashboard_views >> initial_dbt_run

        # Phase 1: Initial DBT (must complete before data extraction)
        initial_dbt_run >> initial_dbt_dashboard_views

        # Phase 2: Data Extraction (only after DBT is completely done)
        initial_dbt_dashboard_views >> extract_cleaned_data

        # Phase 3: LLM Processing (Steps 3-9) - ALL SEQUENTIAL
        # First: YouTube translation
        extract_cleaned_data >> step3_translate

        # Second: YouTube entity extraction (depends on translation)
        step3_translate >> step4_entity_youtube

        # Third: Reddit entity extraction (after YouTube entities)
        step4_entity_youtube >> step5_entity_reddit

        # Fourth: YouTube sentiment (after Reddit entities)
        step5_entity_reddit >> step6_sentiment_youtube

        # Fifth: Reddit sentiment (after YouTube sentiment)
        step6_sentiment_youtube >> step7_sentiment_reddit

        # Sixth: Combined trend detection (after both sentiments)
        step7_sentiment_reddit >> step8_trend_combined

        # Seventh: Summarization (after trends)
        step8_trend_combined >> step9_summarization

        # Phase 4: Load Analytics Data (after LLM processing)
        step9_summarization >> load_analytics_data

        # Phase 5: Final DBT (after analytics data is loaded)
        load_analytics_data >> final_dbt_run >> final_dbt_dashboard_views

    else:
        # Fallback: create a simple task that explains the issue
        def explain_pipeline_structure(**context):
            """Explain the pipeline structure and manual execution approach."""
            message = """
            Complete LLM Pipeline Structure:

            Phase 1: Initial DBT Run
            1. initial_dbt_run              - Run all DBT models
            2. initial_dbt_dashboard_views  - Ensure dashboard views exist

            Phase 2: Data Extraction
            3. extract_cleaned_data         - Extract latest social media data

            Phase 3: LLM Processing
            4. step3_translate_youtube      - Translate latest YouTube cleaned file
            5. step4_entity_youtube         - Extract entities from translated YouTube
            6. step5_entity_reddit          - Extract entities from latest Reddit cleaned
            7. step6_sentiment_youtube      - Sentiment analysis on YouTube entities
            8. step7_sentiment_reddit       - Sentiment analysis on Reddit entities
            9. step8_trend_combined         - Combined trend detection
            10. step9_summarization         - Generate final summary

            Phase 4: Data Loading
            11. load_analytics_data         - Load processed data to analytics DB

            Phase 5: Final DBT Run
            12. final_dbt_run              - Run all DBT models with new data
            13. final_dbt_dashboard_views  - Ensure dashboard views persist

            Dependencies (STRICT SEQUENTIAL - NO PARALLEL EXECUTION):
            1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9 → 10 → 11 → 12 → 13

            Key Points:
            - Data extraction only starts AFTER initial DBT run and dashboard views are complete
            - All LLM steps run sequentially (no parallel processing)
            - Analytics data loading only starts after ALL LLM processing is complete
            - Final DBT run ensures dashboard views persist
            """
            print(message)
            return {"status": "info", "message": message}

        info_task = PythonOperator(
            task_id='pipeline_info',
            python_callable=explain_pipeline_structure,
        )
