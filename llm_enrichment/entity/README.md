# Entity Extraction Module

## Overview
The entity extraction module identifies and extracts Japanese music-related entities (artists, songs, albums, genres) from social media comments using LLM-powered analysis.

## Components

### `entity_extraction.py`
Main entity extraction engine that processes cleaned comment data.

**Key Features:**
- **Multi-entity extraction**: Artists, songs, albums, genres
- **Japanese text handling**: Supports both Japanese and English text
- **LLM integration**: Uses Ollama/Llama models for intelligent extraction
- **Batch processing**: Efficiently processes large datasets
- **Error handling**: Robust error handling and logging

**Usage:**
```python
from llm_enrichment.entity.entity_extraction import EntityExtractor

extractor = EntityExtractor(
    ollama_host="https://your-llm-host.com",
    model_name="llama3.1:8b"
)

results = extractor.extract_entities_from_csv(
    input_file="cleaned_comments.csv",
    output_dir="output/",
    text_column="comment_text"
)
```

### `entity_extraction_config.py`
Configuration settings for entity extraction processing.

**Configuration Options:**
- **Model settings**: LLM model name and parameters
- **Batch processing**: Batch sizes and limits
- **Output formatting**: Column names and file formats
- **Logging**: Log levels and file paths
- **Retry logic**: Retry attempts and timeouts

## Input/Output

### Input Format
- **CSV files** with cleaned comment data
- **Required columns**: `comment_text` (or configurable)
- **Optional columns**: `platform`, `author`, `published_at`

### Output Format
- **CSV file**: `YYYYMMDD_{platform}_entities.csv`
- **Columns**: `comment_text`, `extracted_artists`, `extracted_songs`, `extracted_albums`, `extracted_genres`, `confidence_score`

## Integration

### Airflow DAGs
- **Step 2**: `dags/llm_pipeline/step2_entity_youtube.py`
- **Step 3**: `dags/llm_pipeline/step3_entity_reddit.py`

### Pipeline Integration
Used by downstream modules:
- **Sentiment Analysis**: Analyzes sentiment for extracted entities
- **Trend Detection**: Identifies trending entities
- **Summarization**: Generates insights about entity patterns

## Configuration

### Environment Variables
```bash
OLLAMA_HOST="https://your-llm-host.com"
```

### Model Requirements
- **LLM Model**: Llama 3.1-8B or compatible
- **Memory**: Sufficient for batch processing
- **Network**: Stable connection to LLM host

## Error Handling
- **Connection failures**: Graceful degradation with retries
- **Invalid responses**: Parsing error handling
- **Missing data**: Handles empty or malformed input
- **Logging**: Comprehensive error logging to `logs/entity_extraction.log`

## Performance
- **Batch processing**: Configurable batch sizes for memory efficiency
- **Parallel processing**: Multi-threaded where applicable
- **Progress tracking**: Real-time progress indicators
- **Resource optimization**: Memory and CPU usage optimization
