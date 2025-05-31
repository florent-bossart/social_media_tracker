# 📊 Project: Social Media Sentiment Tracker for Global Trends

## PROJECT STATUS :
[DONE]
Docker compose for DBT, AIRFLOW, POSTGRES Database, FastAPI container to query youtube and reddit easily
Built API query logic + file generation
Built json to postgres load + Airflow dags
Started playing with DBT/do some data cleaning
Test different LLM to detect trends
Define PROD data model
Write DAGS for full orchestration
Added LLM using laptop GPU + tunneling (program still triggered from the VM)
  - Entity extraction is working - ~6 hours for reddit extraction
  - sentiment analysis - 6 hours youtube / 18hours reddit
  - Trend detection - TBD
  - Summarization - TBD
Added DBT transformation using


[NEXT]
Clean the code base
Test Trend and Summarization
Adapt final data model if needed.
add streamlit + build dashboard


[LATER]
Work on presentation

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
  - Translation JP to EN (youtube only) => MARIANMT
  - Entity Extraction => OLLAMA
  - Sentiment Analysis => OLLAMA
  - Trend detection => OLLAMA
  - Summarization => OLLAMA

### 5. Workflow Orchestration (Airflow)
- Automate the pipeline:
  - Extract → Load → Transform (DBT) → Transform (Python/LLM) → Load  → Analyze
  - Schedule  daily

### 6. Visualization
- Build a **dashboard** to display:
  - Sentiment trends over time
  - Most discussed topics
  - Positive/negative sentiment spikes
- Tools:
  - Streamlit (Python-friendly)


### 7. Optional Enhancements (Bonus 🚀)
- **Trend Detection:** Simple anomaly detection for spikes.
- **Dockerization:** Containerize the entire project for portability.

---

## 📅 Timeline Suggestion

| Step | Task |
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
- [x] (Optional) Add Docker Compose for full project deployment
- [ ] Write blog post or LinkedIn article about the project 🚀
