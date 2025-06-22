# 📊 Project: Japanese Music trends Detection

## 📝 Project Description

Automated data pipeline that tracks trending artists on social media (like youtube and Reddit), analyzes the sentiment of public posts in real-time on a Daily basis, and visualizes evolving public opinions on different themes (e.g., tech innovations, climate change, major events).
The pipeline is orchestrated using **Airflow**, and data transformation is handled by **DBT**, ensuring clean and analyzable datasets. The project will use cost-free or low-cost data sources and open-source tools to avoid cloud expenses.


## How to use :

Install poetry with the dependencies from pyproject.toml
Install docker
Create an account on GCP to be able to query youtube API. Look for the API in GCP and it should guide you on what you need to do.
Create an account for Reddit API https://www.reddit.com/prefs/apps
Copy and complete env_file.example
Install Ollama https://ollama.com/  Linux : curl -fsSL https://ollama.com/install.sh | sh
Install ollama models : ollama pull llama3:7b

Run docker compose build, then docker compose up. Then you will be able to manually trigger each step from Airflow.
!!! The LLM part takes a lot of processing, you can use different machines to run the LLM part, you will need to set up a tunnel from your execution environment to the processing machine, and install Ollama on the processing machine !!!
How to run :
Daily - Run DAGS:
- fetch_reddit_daily_data             => Get reddit data usingthe API
- fetch_youtube_daily_data            => Get youtube data using the API
- Load_all_social_media_raw_today     => Load youtube and reddit data in the raw schema
- llm_complete_pipeline_full          => all the LLM part + dbt
For LLM step by step :
- dbt_run                             => clean the data and create intermediary tables
- cleaned_data_extraction             => extract intermediary data for LLM processing
- llm_step_1_translate_youtube_optimized => translate Japanese youtube comments into English. Optimized version have special memory config
- llm_step2_entity_youtube            => extract entities from youtube
- llm_step3_entity_reddit             => extract entities from reddit
- llm_step4_sentiment_youtube         => extract sentiment from youtube
- llm_step5_sentiment_reddit          => extract sentiment from reddit
- llm_step6_trend_combined            => generate trends files
- llm_step7_summarization             => generate summarization
- step8_load_analytics_simple         => load llm generated data into the analytics schema
- dbt_run                             => generate the views for the dashboard


Other optional dags :
- update_youtube_comments_rotating    => query youtube API on already fetched videos, to get comment updates - if you still have not reached youtube quota
- load_all_youtube_comment_updates    => load these new comments in the raw schema

Some other dags to load/extract files separatly.



## PROJECT STATUS :

[NEXT]
Cre
More logging
More error handling
More Unit tests
More doc

--



### Key Highlights:
- ✅ Data ingestion from APIs
- ✅ Data orchestration with Airflow
- ✅ Data transformation and modeling with DBT
- ✅ Natural Language Processing (Sentiment Analysis)
- ✅ Interactive dashboard for stakeholders with Streamlit

---

## 🚀 Project Plan

### 0. Setup Work environment
**Sources:**
- Init git, poetry, direnv
- Install/Init Docker images to run Airflow, DBT, Postgres

### 1. Data Collection
**Sources:**
- Youtube API
- Reddit (PRAW or Pushshift API)

**Method:**
- Python scripts as Airflow tasks to extract posts containing target keywords/hashtags.

### 2. Data Storage
- Dockerized  **Postgres** database.
- Design raw and staging tables for DBT transformations.

### 3. Data Transformation (DBT)
- Clean text data: remove noise (hashtags, URLs, emojis, etc.).
- Build models:
  - Translation JP to EN (youtube only)
  - Entity Extraction
  - Sentiment Analysis
  - Trend detection
  - Summarization

### 4. Models
- Open-source libraries:
  - Translation JP to EN (youtube only) => NLLB200
  - Entity Extraction => OLLAMA
  - Sentiment Analysis => OLLAMA
  - Trend detection => OLLAMA
  - Summarization => OLLAMA

### 5. Workflow Orchestration (Airflow)
- Automate the pipeline:
  - Extract → Load → Transform (DBT) → Transform (Python/LLM) → Load  → Transform (DBT) →  Analyze
  - Schedule  daily

### 6. Visualization
- Build a **dashboard** to display:
  - Sentiment trends over time
  - Most discussed topics
  - Positive/negative sentiment spikes
- Tools:
  - Streamlit (Python-friendly)
