# Sentiment Analysis Module

## Overview
The sentiment analysis module analyzes emotional sentiment towards extracted Japanese music entities using LLM-powered natural language processing.

## Components

### `sentiment_analysis.py`
Main sentiment analysis engine that processes entity-extracted data.

**Key Features:**
- **Entity-specific sentiment**: Analyzes sentiment for each extracted entity
- **Multi-dimensional analysis**: Overall sentiment, confidence scoring, emotional categorization
- **LLM integration**: Uses Ollama/Llama models for nuanced sentiment understanding
- **Japanese context awareness**: Understands cultural context in Japanese music discussions
- **Batch processing**: Efficiently processes large datasets
- **Robust error handling**: Comprehensive error handling and logging

**Usage:**
```python
from llm_enrichment.sentiment.sentiment_analysis import SentimentAnalyzer

analyzer = SentimentAnalyzer(
    ollama_host="https://your-llm-host.com",
    model_name="llama3.1:8b"
)

results = analyzer.analyze_sentiment_from_csv(
    input_file="entities.csv",
    output_dir="output/",
    text_column="comment_text"
)
```

### `sentiment_analysis_config.py`
Configuration settings for sentiment analysis processing.

**Configuration Options:**
- **Model settings**: LLM model name and parameters
- **Sentiment categories**: Positive, neutral, negative thresholds
- **Batch processing**: Batch sizes and processing limits
- **Output formatting**: Column names and file formats
- **Logging**: Log levels and file paths (fixed to use relative paths)
- **Retry logic**: Retry attempts and connection timeouts

### `mock_sentiment_analysis.py`
Mock sentiment analyzer for testing and development without LLM dependency.

**Features:**
- **Development testing**: Allows pipeline testing without LLM access
- **Consistent output format**: Matches real analyzer output structure
- **Deterministic results**: Predictable sentiment scores for testing
- **Fast execution**: No network dependencies for rapid iteration

## Input/Output

### Input Format
- **CSV files** with entity extraction results
- **Required columns**: `comment_text`, extracted entity columns
- **Optional columns**: `platform`, `author`, `published_at`, `confidence_score`

### Output Format
- **CSV file**: `{platform}_combined_sentiment_original_data_YYYYMMDD_HHMMSS.csv`
- **Columns**: Original columns plus `sentiment_score`, `sentiment_label`, `confidence`, `emotional_category`

## Integration

### Airflow DAGs
- **Step 4**: `dags/llm_pipeline/step4_sentiment_youtube.py`
- **Step 5**: `dags/llm_pipeline/step5_sentiment_reddit.py`

### Pipeline Integration
Feeds into downstream modules:
- **Trend Detection**: Uses sentiment data for trend analysis
- **Summarization**: Incorporates sentiment patterns in insights

## Configuration

### Environment Variables
```bash
OLLAMA_HOST="https://your-llm-host.com"
```

### Logging Configuration
- **Log file**: `logs/sentiment_analysis.log` (relative path)
- **Log level**: Configurable (INFO, DEBUG, ERROR)
- **Automatic directory creation**: Creates logs directory if missing

## Sentiment Categories

### Sentiment Labels
- **Positive**: Favorable, enthusiastic, supportive sentiment
- **Neutral**: Balanced, informational, or ambiguous sentiment
- **Negative**: Critical, disappointing, or unfavorable sentiment

### Confidence Scoring
- **High (0.8-1.0)**: Clear, unambiguous sentiment
- **Medium (0.5-0.8)**: Moderate confidence in sentiment
- **Low (0.0-0.5)**: Uncertain or mixed sentiment

### Emotional Categories
- **Excitement**: High energy positive emotions
- **Appreciation**: Thoughtful positive emotions
- **Disappointment**: Negative emotions about expectations
- **Criticism**: Analytical negative emotions
- **Neutral**: Balanced or informational tone

## Error Handling
- **Connection failures**: Graceful degradation with retries
- **Invalid LLM responses**: Response parsing and validation
- **Missing entity data**: Handles incomplete input gracefully
- **File path issues**: Fixed hardcoded path problems
- **Logging**: Comprehensive error logging with relative paths

## Performance
- **Batch processing**: Configurable batch sizes for optimal performance
- **Progress tracking**: Real-time progress indicators with tqdm
- **Memory efficiency**: Optimized for large datasets
- **Parallel processing**: Multi-threaded where applicable

## Recent Fixes (2025-06-17)
- **✅ Fixed logging paths**: Changed from hardcoded absolute paths to relative paths
- **✅ Directory creation**: Automatic logs directory creation
- **✅ Docker compatibility**: Works correctly in containerized environments
- **✅ Error handling**: Improved error handling for file operations
