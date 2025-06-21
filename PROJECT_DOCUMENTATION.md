# Social Media Analytics Pipeline - Project Documentation

## Overview
This project implements a comprehensive social media analytics pipeline that extracts, processes, and analyzes data from YouTube and Reddit to track music artist mentions, sentiment, and trends.

## Recent Major Improvements

### Pipeline Architecture Fixes (2025-06)
- **Sequential Execution**: Refactored Airflow DAGs for strict sequential execution to prevent resource conflicts
- **DBT Integration**: Fixed DBT DockerOperator command syntax and container execution issues
- **Translation Optimization**: Implemented memory-efficient translation with proper batch processing
- **Data Recovery**: Successfully restored analytics data after accidental truncation

### Artist Filtering Enhancement (2025-06)
- **Problem**: DBT models were including generic words, pronouns, and non-artist terms as "artist names"
- **Solution**: Implemented comprehensive filtering logic with:
  - Exclusion list for generic words ("Unknown", "Her", "You", "None", "They", etc.)
  - Allowlist for legitimate artists that might otherwise be filtered
  - Pattern-based rules for minimum length, format validation
  - Reusable DBT macro `filter_valid_artists()` applied across all dashboard models
- **Result**: Cleaner artist analytics with eliminated false positives

### Technical Fixes
- **Set-returning Functions**: Fixed PostgreSQL errors by refactoring models to use lateral joins instead of set-returning functions in WHERE clauses
- **DBT Model Dependencies**: Corrected missing FROM-clause references and table aliases
- **Memory Management**: Implemented conservative translation batching to prevent OOM crashes

## Current Architecture

### Data Sources
- **YouTube**: Comments, videos, channels via YouTube Data API
- **Reddit**: Posts and comments from music-related subreddits

### Processing Pipeline
1. **Data Extraction**: Raw data collection from APIs
2. **Data Cleaning**: Text normalization, duplicate removal
3. **Translation**: Japanese to English translation for YouTube comments
4. **Entity Extraction**: Artist and genre identification using LLM
5. **Sentiment Analysis**: Comment sentiment scoring
6. **Analytics**: Trend detection and statistical analysis
7. **Dashboard**: Streamlit-based visualization

### Technology Stack
- **Orchestration**: Apache Airflow
- **Data Warehouse**: PostgreSQL
- **Transformation**: DBT (Data Build Tool)
- **ML/LLM**: Transformers, PyTorch
- **Dashboard**: Streamlit
- **Containerization**: Docker, Docker Compose

## Key Components

### DBT Models
- **Intermediate Models**: `int_extracted_artists` - central artist filtering and normalization
- **Dashboard Models**: Various analytics views for the Streamlit dashboard
- **Macros**: `filter_valid_artists()` - reusable filtering logic

### Airflow DAGs
- **Complete Pipeline**: End-to-end processing with sequential execution
- **Individual Steps**: Modular DAGs for specific pipeline stages
- **Data Loading**: Raw data ingestion from APIs

### Dashboard
- **Artist Analytics**: Trend analysis, sentiment tracking
- **Platform Comparison**: YouTube vs Reddit metrics
- **Genre Analysis**: Music genre distribution and trends

## Development Guidelines

### DBT Best Practices
- Use the `filter_valid_artists()` macro for any artist name filtering
- Avoid set-returning functions in WHERE clauses (use lateral joins)
- Test model changes with `dbt parse` before deployment

### Memory Management
- Keep translation batch sizes conservative (≤1000 records)
- Monitor system memory during LLM operations
- Use proper cleanup and garbage collection

### Pipeline Execution
- Ensure sequential execution for memory-intensive tasks
- Use appropriate Airflow pools for resource management
- Validate data quality at each stage

## Monitoring and Maintenance

### Key Metrics to Monitor
- Pipeline execution success rates
- Memory usage during translation
- Data quality (artist name accuracy)
- Dashboard performance

### Regular Tasks
- Review artist filtering effectiveness
- Update exclusion/allowlist as needed
- Monitor for new generic terms in extractions
- Validate data accuracy across platforms

## Getting Started

### Prerequisites
- Docker and Docker Compose
- PostgreSQL database
- API keys for YouTube and Reddit

### Quick Start
1. Clone the repository
2. Set up environment variables (see `env_file.example`)
3. Run `docker-compose up` to start all services
4. Access dashboard at `http://localhost:8501`
5. Monitor Airflow at `http://localhost:8080`

### Running Specific Components
- **Translation only**: Use `translate_youtube_comments_optimized.py`
- **DBT only**: `docker exec` into postgres container and run `dbt build`
- **Dashboard only**: `docker-compose up streamlit_dashboard`

## Troubleshooting

### Common Issues
- **Memory Errors**: Reduce batch sizes, check available RAM
- **DBT Errors**: Validate syntax with `dbt parse`, check model dependencies
- **Pipeline Failures**: Check Airflow logs, verify sequential execution
- **Missing Artists**: Review filtering logic, check allowlist coverage

### Performance Optimization
- Use DBT incremental models for large datasets
- Implement proper indexing on frequently queried columns
- Monitor and tune translation batch sizes
- Use caching for dashboard queries

---

For detailed technical documentation, see individual component READMEs in their respective directories.
