FROM python:3.12.10-slim

ARG DEBIAN_FRONTEND=noninteractive

ENV PYTHONUNBUFFERED=1

# Force Poetry to install packages globally (not in .venv)
ENV POETRY_VIRTUALENVS_CREATE=false

WORKDIR /app

# Copy pyproject and install dependencies
COPY pyproject.toml poetry.lock ./

RUN pip3 install --upgrade --no-cache-dir pip \
    && pip3 install poetry \
    && poetry install --only main

# Copy app code
COPY api ./api

CMD ["poetry", "run", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
