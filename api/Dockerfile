FROM python:3.10-slim

ARG DEBIAN_FRONTEND=noninteractive

ENV PYTHONUNBUFFERED=1

# Force Poetry to install packages globally (not in .venv)
ENV POETRY_VIRTUALENVS_CREATE=false

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libpq-dev \
    python3-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy pyproject and install dependencies
COPY ./api/pyproject.toml ./api/poetry.lock ./

RUN pip3 install --upgrade --no-cache-dir pip \
    && pip3 install poetry \
    && poetry install --only main

# Copy app code
COPY api ./api

CMD ["poetry", "run", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
