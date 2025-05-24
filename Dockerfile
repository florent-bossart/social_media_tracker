FROM python:3.10-slim

ARG DEBIAN_FRONTEND=noninteractive

ENV PYTHONUNBUFFERED=1
ENV POETRY_VIRTUALENVS_IN_PROJECT=true

ENV AIRFLOW_HOME=/app/airflow

ENV DBT_DIR=$AIRFLOW_HOME/dbt_social_media_tracker
ENV DBT_TARGET_DIR=$DBT_DIR/target
ENV DBT_PROFILES_DIR=$DBT_DIR
ENV DBT_VERSION=1.9.1

WORKDIR $AIRFLOW_HOME

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libpq-dev \
    python3-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml poetry.lock ./

RUN pip3 install --upgrade --no-cache-dir pip \
    && pip3 install poetry \
    && poetry install --no-interaction --no-root

COPY scripts scripts
RUN chmod +x scripts/entrypoint.sh

COPY data_pipeline /app/data_pipeline
COPY dags /app/airflow/dags
COPY dbt_social_media_tracker /app/airflow/dbt_social_media_tracker
