# 📊 Project: Japanese Music Trends Detection

## 📝 Project Description

Automated data pipeline that tracks trending artists on social media (like YouTube and Reddit), analyzes the sentiment of public posts in real-time on a daily basis, and visualizes evolving public opinions on different themes (e.g., tech innovations, climate change, major events).

The pipeline is orchestrated using **Airflow**, and data transformation is handled by **DBT**, ensuring clean and analyzable datasets. The project will use cost-free or low-cost data sources and open-source tools to avoid cloud expenses.

## How to Use

### Prerequisites

1. Install poetry with the dependencies from pyproject.toml
2. Install docker
3. Create an account on GCP to be able to query YouTube API. Look for the API in GCP and it should guide you on what you need to do.
4. Create an account for Reddit API https://www.reddit.com/prefs/apps
5. Copy and complete env_file.example
6. Install Ollama https://ollama.com/
   - Linux: `curl -fsSL https://ollama.com/install.sh | sh`
7. Install ollama models: `ollama pull llama3:7b`

### Running the Project

1. Run `docker compose build`
2. Run `docker compose up`
3. You will be able to manually trigger each step from Airflow

> **Note:** The LLM part takes a lot of processing. You can use different machines to run the LLM part. You will need to set up a tunnel from your execution environment to the processing machine, and install Ollama on the processing machine.

### Daily DAGs

- **fetch_reddit_daily_data** - Get Reddit data using the API
- **fetch_youtube_daily_data** - Get YouTube data using the API
- **Load_all_social_media_raw_today** - Load YouTube and Reddit data in the raw schema
- **llm_complete_pipeline_full** - All the LLM part + DBT

### LLM Step by Step

- **dbt_run** - Clean the data and create intermediary tables
- **cleaned_data_extraction** - Extract intermediary data for LLM processing
- **llm_step_1_translate_youtube_optimized** - Translate Japanese YouTube comments into English (optimized version with special memory config)
- **llm_step2_entity_youtube** - Extract entities from YouTube
- **llm_step3_entity_reddit** - Extract entities from Reddit
- **llm_step4_sentiment_youtube** - Extract sentiment from YouTube
- **llm_step5_sentiment_reddit** - Extract sentiment from Reddit
- **llm_step6_trend_combined** - Generate trends files
- **llm_step7_summarization** - Generate summarization
- **step8_load_analytics_simple** - Load LLM generated data into the analytics schema
- **dbt_run** - Generate the views for the dashboard

### Optional DAGs

- **update_youtube_comments_rotating** - Query YouTube API on already fetched videos to get comment updates (if you still have not reached YouTube quota)
- **load_all_youtube_comment_updates** - Load these new comments in the raw schema

Some other DAGs to load/extract files separately.


## 💾 Database Backup & Restore

The project includes comprehensive database backup and restore functionality for easy project forking and data sharing.

### Creating a Backup

```bash
# Create a compressed backup of the entire database
./scripts/backup_database.sh
```

This creates a `.tar.gz` file in the `backups/` directory containing:

- Complete SQL dump of all schemas (raw, staging, analytics)
- Backup metadata and restore instructions
- Sample data for Japanese music trend analysis

### Restoring a Backup

```bash
# Restore the latest backup (auto-detects Docker/local setup)
./scripts/restore_database.sh

# Restore a specific backup file
./scripts/restore_database.sh backup_20240622_120000.tar.gz

# Force restore without prompts (useful for automation)
./scripts/restore_database.sh --force

# Get help with all options
./scripts/restore_database.sh --help
```

The restore script automatically:

- Detects whether you're using Docker or local PostgreSQL
- Extracts and validates the backup
- Safely drops and recreates the database
- Verifies the restore was successful

Perfect for getting started with sample data when forking this project!

## 📈 Project Status

### Key Highlights

- ✅ Data ingestion from APIs
- ✅ Data orchestration with Airflow
- ✅ Data transformation and modeling with DBT
- ✅ Natural Language Processing (Sentiment Analysis)
- ✅ Interactive dashboard for stakeholders with Streamlit

### Next Steps

- More logging
- More error handling
- More unit tests
- More documentation

## 🚀 Project Plan

### 0. Setup Work Environment

**Setup:**

- Init git, poetry, direnv
- Install/Init Docker images to run Airflow, DBT, Postgres

### 1. Data Collection

**Sources:**

- YouTube API
- Reddit (PRAW or Pushshift API)

**Method:**

- Python scripts as Airflow tasks to extract posts containing target keywords/hashtags

### 2. Data Storage

- Dockerized **PostgreSQL** database
- Design raw and staging tables for DBT transformations

### 3. Data Transformation (DBT)

- Clean text data: remove noise (hashtags, URLs, emojis, etc.)
- Build models:
  - Translation JP to EN (YouTube only)
  - Entity Extraction
  - Sentiment Analysis
  - Trend detection
  - Summarization

### 4. Models

Open-source libraries:

- **Translation JP to EN** (YouTube only) → NLLB200
- **Entity Extraction** → OLLAMA
- **Sentiment Analysis** → OLLAMA
- **Trend detection** → OLLAMA
- **Summarization** → OLLAMA

### 5. Workflow Orchestration (Airflow)

Automate the pipeline:

- Extract → Load → Transform (DBT) → Transform (Python/LLM) → Load → Transform (DBT) → Analyze
- Schedule daily

### 6. Visualization

Build a **dashboard** to display:

- Sentiment trends over time
- Most discussed topics
- Positive/negative sentiment spikes

**Tools:**

- Streamlit (Python-friendly)
