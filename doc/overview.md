<<<<<<< HEAD
flowchart TD
    %% Extraction
    A1[Reddit API] --> B1[data/reddit/YYYY-MM-DD/*.json]
    A2[YouTube API] --> B2[data/youtube/YYYY-MM-DD/*.json]

    %% Orchestration
    B1 --> C[Airflow DAGs]
    B2 --> C

    %% Data Loading
    C --> D[(PostgreSQL Warehouse)]

    %% Transformation
    D --> E[dbt Transformations]

    %% ML & Results
    E --> F[ML Models]
    E --> G[Sentiment & Results]
    F --> G
    G --> H[Streamlit Dashboard]
=======
# 📊 Project Overview

```mermaid
flowchart TD
    A[Twitter API] --> B[Airflow DAG]
    B --> C[PostgreSQL DB]
    C --> D[dbt Transformations]
    D --> E[Sentiment Results]
    E --> F[Streamlit Dashboard]
>>>>>>> a1d0bee8fb0f8f41024243a6eb16e9e9547e8567
