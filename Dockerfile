FROM python:3.12.10-slim

ARG DEBIAN_FRONTEND=noninteractive

ENV PYTHONUNBUFFERED=1

ENV AIRFLOW_HOME=/app/airflow

<<<<<<< HEAD
ENV DBT_DIR=$AIRFLOW_HOME/dbt_social_media_tracker
ENV DBT_TARGET_DIR=$DBT_DIR/target
ENV DBT_PROFILES_DIR=$DBT_DIR
ENV DBT_VERSION=1.9.1

=======
### 1.1
ENV DBT_DIR=$AIRFLOW_HOME/dbt_social_media_tracker

ENV DBT_TARGET_DIR=$DBT_DIR/target

ENV DBT_PROFILES_DIR=$DBT_DIR

ENV DBT_VERSION=1.9.1

# DBT


>>>>>>> a1d0bee8fb0f8f41024243a6eb16e9e9547e8567
WORKDIR $AIRFLOW_HOME

COPY scripts scripts
RUN chmod +x scripts/entrypoint.sh

<<<<<<< HEAD
COPY data_pipeline /app/data_pipeline

=======
>>>>>>> a1d0bee8fb0f8f41024243a6eb16e9e9547e8567
COPY pyproject.toml poetry.lock ./

RUN pip3 install --upgrade --no-cache-dir pip \
    && pip3 install poetry \
<<<<<<< HEAD
    && poetry install --no-interaction --no-root
=======
    && poetry install --only main
>>>>>>> a1d0bee8fb0f8f41024243a6eb16e9e9547e8567
