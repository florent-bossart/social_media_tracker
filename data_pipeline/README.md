# Data Pipeline Module

## Overview
The data_pipeline module provides comprehensive data processing tools for the Japanese Music Trends Analysis project, handling everything from data extraction and translation to LLM-powered analysis and database operations.

## 🏗️ Module Structure

### **Data Extraction**
- **`extract_cleaned_comments.py`** - Extract all cleaned comments from database
- **`extract_cleaned_comments_by_date.py`** - Extract comments with date filtering
- **`extract_cleaned_data_full.py`** - Full data extraction with additional processing

### **Translation & Processing**
- **`translate_youtube_comments.py`** - Modern NLLB-based translation (Japanese → English)
- **`translate_comment_jp_to_en_NLLB.py`** - Generic NLLB translation utility
- **`translate_comment_jp_to_en_MARIANMT.py`** - MarianMT-based translation (legacy)

### **LLM Pipeline**
- **`run_complete_pipeline.py`** - Full multi-stage LLM analysis pipeline
- **`run_sentiment_pipeline.py`** - Standalone sentiment analysis
- **`run_specific_entity_extraction.py`** - Standalone entity extraction

### **Database Operations**
- **`init_db.py`** - Database initialization and schema creation
- **`load_json_to_postgres.py`** - JSON data loading to PostgreSQL
- **`load_analytics_data.py`** - Analytics data processing and loading

### **Utilities**
- **`fix_youtube_headers.py`** - CSV header standardization utility
- **`generate_wordcloud_text.py`** - Text processing for word cloud generation

---

## 🚀 Quick Start Guide

### **1. Data Extraction**
```bash
# Extract latest comments with date filter
python data_pipeline/extract_cleaned_comments_by_date.py --date 2025-06-11 --source both

# Extract all comments
python data_pipeline/extract_cleaned_comments.py
```

### **2. Translation**
```bash
# Translate latest YouTube comments
poetry run python data_pipeline/translate_youtube_comments.py --latest-only

# Translate specific file
poetry run python data_pipeline/translate_youtube_comments.py --input-file path/to/file.csv
```

### **3. LLM Analysis**
```bash
# Run complete pipeline (entity extraction → sentiment → trends → insights)
python data_pipeline/run_complete_pipeline.py --input-dir data/intermediate/translated

# Run specific sentiment analysis
python data_pipeline/run_sentiment_pipeline.py youtube --input_file path/to/entities.csv
```

### **4. Database Setup**
```bash
# Initialize database schema
python data_pipeline/init_db.py

# Load JSON data to PostgreSQL
python data_pipeline/load_json_to_postgres.py
```

---

## 📊 Data Flow

### **Complete Pipeline Flow**
```
Raw Data (JSON) → Database → Cleaned CSV → Translated CSV → Entities → Sentiment → Trends → Insights
     ↓               ↓            ↓             ↓           ↓          ↓         ↓        ↓
load_json_to_   extract_     translate_    run_specific_  run_      trend_    summary_
postgres.py     cleaned_     youtube_      entity_        sentiment detection  generation
                comments     comments      extraction     pipeline
```

### **File Naming Conventions**
- **Cleaned**: `YYYYMMDD_YYYY-MM-DD_{platform}_comments_cleaned.csv`
- **Translated**: `YYYYMMDD_YYYY-MM-DD_{platform}_comments_cleaned_nllb_translated.csv`
- **Entities**: `YYYYMMDD_{platform}_entities.csv`
- **Sentiment**: `{platform}_combined_sentiment_original_data_YYYYMMDD_HHMMSS.csv`

---

## 🛠️ Configuration

### **Environment Variables**
```bash
# Database Configuration
WAREHOUSE_USER="your_db_user"
WAREHOUSE_PASSWORD="your_db_password"
WAREHOUSE_HOST="localhost"
WAREHOUSE_PORT="5432"
WAREHOUSE_DB="your_database"

# LLM Configuration
OLLAMA_HOST="https://your-llm-host.com"
```

### **Dependencies**
```bash
# Install with Poetry
poetry install

# Or with pip
pip install -r requirements.txt
```

---

## 📋 Script Documentation

| Script | Purpose | Input | Output | Documentation |
|--------|---------|--------|--------|---------------|
| `extract_cleaned_comments_by_date.py` | Extract filtered comments | Database | CSV files | [📖 README](extract_cleaned_comments_by_date_README.md) |
| `translate_youtube_comments.py` | Japanese→English translation | Cleaned CSV | Translated CSV | [📖 README](translation_scripts_README.md) |
| `run_complete_pipeline.py` | Full LLM analysis pipeline | Translated CSV | Multiple outputs | [📖 README](run_complete_pipeline_README.md) |
| `run_sentiment_pipeline.py` | Sentiment analysis | Entity CSV | Sentiment CSV | [📖 README](run_sentiment_pipeline_README.md) |
| `run_specific_entity_extraction.py` | Entity extraction | Cleaned/Translated CSV | Entity CSV | [📖 README](run_specific_entity_extraction_README.md) |
| `load_json_to_postgres.py` | Data loading | JSON files | Database tables | [📖 README](database_operations_README.md) |
| `init_db.py` | Database setup | None | Database schema | [📖 README](database_operations_README.md) |
| `translate_comment_jp_to_en_NLLB.py` | Generic NLLB translation | CSV files | Translated CSV | [📖 README](translation_scripts_README.md) |
| `fix_youtube_headers.py` | CSV header standardization | CSV files | Fixed CSV | Utility script |
| `generate_wordcloud_text.py` | Text processing for wordclouds | CSV files | Text files | Utility script |

---

## 🎯 Common Use Cases

### **Daily Data Processing**
1. **Extract latest data**: Use `extract_cleaned_comments_by_date.py` with yesterday's date
2. **Translate content**: Use `translate_youtube_comments.py --latest-only`
3. **Run analysis**: Use `run_complete_pipeline.py` for full LLM processing
4. **Load results**: Database integration automatic

### **Historical Data Analysis**
1. **Extract date range**: Use date filtering in extraction scripts
2. **Batch processing**: Process multiple files with pattern matching
3. **Trend analysis**: Compare results across time periods

### **Development & Testing**
1. **Sample data**: Extract small date ranges for testing
2. **Pipeline testing**: Use individual scripts for step-by-step validation
3. **Mock analysis**: Use mock sentiment analysis for development

---

## 🔧 Troubleshooting

### **Common Issues**

#### **File Not Found Errors**
- Check file paths and naming conventions
- Ensure previous pipeline steps completed successfully
- Use absolute paths when in doubt

#### **Translation Errors**
- Verify NLLB model is downloaded
- Check available memory (2GB+ recommended)
- Ensure input files have correct column names (`comment_text`)

#### **Database Connection Issues**
- Verify environment variables in `.env` file
- Check database server is running
- Test connection with simple query

#### **LLM Analysis Failures**
- Verify `OLLAMA_HOST` environment variable
- Check LLM server is accessible
- Ensure sufficient memory for model loading

### **Logging**
All scripts provide comprehensive logging:
- **Console output**: Real-time progress and status
- **Log files**: Detailed execution logs in `logs/` directory
- **Error handling**: Graceful degradation with error messages

---

## 📈 Performance Guidelines

### **Memory Requirements**
- **Translation**: 2-4GB RAM for NLLB model
- **LLM Analysis**: 4-8GB RAM for Llama models
- **Database**: 1-2GB RAM for large datasets

### **Processing Times**
- **Translation**: ~100-200 comments/minute
- **Entity Extraction**: ~50-100 comments/minute
- **Sentiment Analysis**: ~100-150 comments/minute
- **Complete Pipeline**: ~30-50 comments/minute end-to-end

### **Optimization Tips**
- **Batch processing**: Use appropriate batch sizes
- **Parallel processing**: Run different platforms simultaneously
- **Resource monitoring**: Monitor memory and CPU usage
- **Incremental processing**: Process only new data when possible

---

## 🔄 Integration

### **Airflow Integration**
All major scripts are integrated with Airflow DAGs:
- **Individual steps**: Separate DAGs for each processing step
- **Complete pipeline**: Single DAG for full workflow
- **Manual execution**: Trigger-based execution only

### **Database Integration**
- **Input**: PostgreSQL tables with cleaned data
- **Output**: Structured tables for analysis results
- **Schema**: Automated schema creation and management

### **Dashboard Integration**
- **Data source**: Processed CSV files and database tables
- **Visualization**: Streamlit dashboard integration
- **Real-time**: Live data updates from pipeline results

---

## ✨ Recent Updates (June 2025)

### **✅ Improvements Made**
- **Column naming consistency**: Fixed end-to-end column standardization
- **File auto-detection**: Intelligent latest file detection
- **Error handling**: Enhanced robustness across all scripts
- **Docker compatibility**: Fixed path issues for containerized deployment
- **Documentation**: Comprehensive documentation for all scripts

### **✅ Production Ready**
- **Airflow integration**: All scripts working in production
- **Error recovery**: Robust error handling and logging
- **Performance optimization**: Optimized for production workloads
- **Monitoring**: Complete logging and progress tracking

The data_pipeline module is production-ready and actively processing Japanese music trend data! 🎵📊
