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
