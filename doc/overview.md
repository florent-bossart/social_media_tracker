# 📊 Project Overview

```mermaid
flowchart TD
    A[Twitter API] --> B[Airflow DAG]
    B --> C[PostgreSQL DB]
    C --> D[dbt Transformations]
    D --> E[Sentiment Results]
    E --> F[Streamlit Dashboard]
