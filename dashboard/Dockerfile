# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Install Poetry
RUN pip install poetry

# Copy only pyproject.toml and poetry.lock to leverage Docker cache
COPY pyproject.toml poetry.lock* /app/

# Install project dependencies
# --no-root is used because we are not installing the project itself as a package, just its dependencies
# --only main is used to not install development dependencies
RUN poetry config virtualenvs.create false && poetry install --only main --no-root

# Copy the rest of the dashboard application code into the container
COPY . /app/dashboard

# Expose the port Streamlit runs on
EXPOSE 8501

# Command to run the Streamlit application
# We use the dashboard subdirectory explicitly if dashboard.py is inside it.
CMD ["streamlit", "run", "dashboard/dashboard.py", "--server.port=8501", "--server.address=0.0.0.0"]
