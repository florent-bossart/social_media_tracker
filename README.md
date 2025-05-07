# 📊 Project: Social Media Sentiment Tracker for Global Trends

## PROJECT STATUS :
[DONE]
Docker compose for DBT, AIRFLOW, POSTGRES Database, FastAPI container to query youtube and reddit easily
Built API query logic + file generation

[NEXT]
Keep running the data extraction manually for a few days to have enough data to work with
Initiate database schema
Initial load of the raw data / build Integration Pipeline

[LATER]
Test different LLM to detect trends
Build Transformation Pipeline
Define PROD data model, to be able to start working on dashboards
Write DAGS for full orchestration
Finalise Dashboards

[ENHANCEMENTS]
Add logging
Better error handling
Unit tests
Refactor duplicated code
More doc





## 📝 Project Description

Build an automated data pipeline that tracks trending hashtags and topics on social media (like Twitter/X and Reddit), analyzes the sentiment of public posts in real-time or near-real-time, and visualizes evolving public opinions on different themes (e.g., tech innovations, climate change, major events).
The pipeline will be orchestrated using **Airflow**, and data transformation will be handled by **DBT**, ensuring clean and analyzable datasets. The project will use cost-free or low-cost data sources and open-source tools to avoid cloud expenses.

### Key Highlights:
- ✅ Data ingestion from APIs
- ✅ Data orchestration with Airflow
- ✅ Data transformation and modeling with DBT
- ✅ Natural Language Processing (Sentiment Analysis)
- ✅ Interactive dashboard for stakeholders
- ✅ (Optional) Alerts for trends and pipeline failures

---

## 🚀 Project Plan

### 0. Setup Work environment
**Sources:**
- Init git, poetry, direnv
- Install/Init Docker images to run Airflow, DBT, Postgres

### 1. Data Collection
**Sources:**
- Twitter/X (API v2, filtered stream or search API)
- Reddit (PRAW or Pushshift API)
- (Optional) RSS feeds from news aggregators

**Method:**
- Python scripts as Airflow tasks to extract posts containing target keywords/hashtags.

### 2. Data Storage
- Local **Postgres** database (Dockerized recommended).
- Design raw and staging tables for DBT transformations.

### 3. Data Transformation (DBT)
- Clean text data: remove noise (hashtags, URLs, emojis, etc.).
- Build models:
  - Cleaned posts
  - Aggregated sentiments over time (daily/hourly)
  - Trending hashtags and topics

### 4. Sentiment Analysis
- Open-source libraries:
  - `TextBlob` (simple, no-cost)
  - `VADER` (for social media-specific sentiment)
  - (Optional) HuggingFace models for advanced analysis
- Append sentiment scores to your transformed data.

### 5. Workflow Orchestration (Airflow)
- Automate the pipeline:
  - Extract → Load → Transform → Analyze
  - Schedule hourly or daily
  - Add alerting on pipeline failure (email/Slack)

### 6. Visualization
- Build a **dashboard** to display:
  - Sentiment trends over time
  - Most discussed topics
  - Positive/negative sentiment spikes
- Tools:
  - Streamlit (Python-friendly)
  - Or Metabase / Superset (SQL-based dashboards)

### 7. Optional Enhancements (Bonus 🚀)
- **Trend Detection:** Simple anomaly detection for spikes.
- **Geo Analysis:** If location data is available.
- **Alerts:** Daily digest of trending topics via email/Slack.
- **Dockerization:** Containerize the entire project for portability.

---

## 📅 Timeline Suggestion

| Week | Task |
|------|------|
| **1** | Set up Airflow, Postgres, DBT, connect APIs |
| **2** | Build ETL pipeline, store raw data, basic transformations |
| **3** | Implement sentiment analysis, create DBT models |
| **4** | Build dashboard, test end-to-end automation |
| **5** | Polish project, add optional enhancements, write documentation |
| **6** | Prepare presentation and portfolio showcase |

---

## ✅ Project Outcome

- 🚀 End-to-end automated data pipeline (Airflow + DBT + APIs)
- 🔍 Clean, transformed datasets with sentiment scores
- 📊 Visual dashboard for non-technical stakeholders
- 🛎️ Optional: Alerts and trend detection
- 💼 Resume-ready project & strong interview case study!

---

## 🧩 Optional Next Steps

- [x] Define target hashtags/topics
- [ ] Set up GitHub repository and CI/CD (GitHub Actions)
- [ ] Prepare project demo video or presentation slides
- [ ] (Optional) Add Docker Compose for full project deployment
- [ ] Write blog post or LinkedIn article about the project 🚀
