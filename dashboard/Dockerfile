# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry

# Copy only dependency files first to leverage Docker cache
COPY dashboard/pyproject.toml dashboard/poetry.lock* /app/

# Configure Poetry and install dependencies
RUN poetry config virtualenvs.create false && \
    poetry install --only main --no-root

# Copy only the dashboard application files
COPY dashboard/*.py /app/

# Expose the port Streamlit runs on
EXPOSE 8501

# Command to run the Streamlit application
CMD ["streamlit", "run", "main_dashboard.py", "--server.port=8501", "--server.address=0.0.0.0"]
