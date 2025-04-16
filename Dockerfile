FROM python:3.12.10-slim

ARG DEBIAN_FRONTEND=noninteractive

ENV PYTHONUNBUFFERED=1

ENV AIRFLOW_HOME=/app/airflow

### 1.1
ENV DBT_DIR=$AIRFLOW_HOME/dbt_social_media_tracker

ENV DBT_TARGET_DIR=$DBT_DIR/target

ENV DBT_PROFILES_DIR=$DBT_DIR

ENV DBT_VERSION=1.9.1

# DBT


WORKDIR $AIRFLOW_HOME

COPY scripts scripts
RUN chmod +x scripts/entrypoint.sh

COPY pyproject.toml poetry.lock ./

RUN pip3 install --upgrade --no-cache-dir pip \
    && pip3 install poetry \
    && poetry install --only main
