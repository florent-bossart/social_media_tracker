# File Detection Utilities

## Overview
The utils module provides intelligent file detection capabilities for the LLM pipeline, automatically identifying the latest files for each processing step.

## Components

### `file_detection.py`
Core file detection utilities with pattern-based matching and date extraction.

**Key Features:**
- **Intelligent date extraction**: Parses YYYYMMDD patterns from filenames
- **Latest file selection**: Automatically finds most recent files
- **Pattern-based matching**: Flexible glob patterns for different file types
- **Priority logic**: Prefers combined files over individual platform files
- **Robust error handling**: Graceful handling of missing files or invalid patterns

**Available Functions:**

#### `find_latest_cleaned_file(platform, data_dir)`
Finds the latest cleaned data file for a platform.
```python
latest_file = find_latest_cleaned_file("youtube", "data/intermediate/Cleaned_data")
```

#### `find_latest_translated_file(platform, data_dir)`
Finds the latest translated file for a platform.
```python
latest_file = find_latest_translated_file("youtube", "data/intermediate/translated")
```

#### `find_latest_entity_file(platform, data_dir)`
Finds the latest entity extraction file for a platform.
```python
latest_file = find_latest_entity_file("youtube", "data/intermediate/entity_extraction")
```

#### `find_latest_sentiment_file(platform, data_dir)`
Finds the latest sentiment analysis file, preferring combined files.
```python
latest_file = find_latest_sentiment_file("reddit", "data/intermediate/sentiment_analysis")
```

#### `find_latest_trend_file(trend_type, data_dir)`
Finds the latest trend detection file, preferring combined sources.
```python
latest_file = find_latest_trend_file("artist_trends", "data/intermediate/trend_detection")
```

## File Patterns

### Cleaned Data Files
- **Pattern**: `YYYYMMDD_*_{platform}_comments_cleaned.csv`
- **Example**: `20250617_2025-06-11_youtube_comments_cleaned.csv`

### Translated Files
- **Pattern**: `YYYYMMDD_*_{platform}_comments_cleaned_*_translated.csv`
- **Example**: `20250617_2025-06-11_youtube_comments_cleaned_nllb_translated.csv`

### Entity Extraction Files
- **Pattern**: `YYYYMMDD_{platform}_entities.csv`
- **Example**: `20250617_youtube_entities.csv`

### Sentiment Analysis Files
- **Individual**: `{platform}_combined_sentiment_original_data_YYYYMMDD_HHMMSS.csv`
- **Combined**: `combined_sentiment_original_data_YYYYMMDD_HHMMSS.csv`
- **Priority**: Combined files preferred over individual platform files

### Trend Detection Files
- **Individual**: `{type}_trends_YYYYMMDD_{platform}.csv`
- **Combined**: `{type}_trends_YYYYMMDD_combined.csv`
- **Priority**: Combined files preferred over individual platform files

## Usage in Pipeline

### Airflow DAG Integration
All LLM pipeline DAGs use these utilities for automatic file detection:

```python
from dags.llm_pipeline.file_detection_utils import find_latest_cleaned_file

# Find latest file automatically
input_file = find_latest_cleaned_file("youtube", "/app/data/intermediate/Cleaned_data")
```

### Standalone Usage
Can be used independently for file management:

```python
from llm_enrichment.utils.file_detection import find_latest_entity_file
import os

# Find latest entity file
base_dir = os.path.abspath(".")
entity_file = find_latest_entity_file("reddit", f"{base_dir}/data/intermediate/entity_extraction")
```

## Date Extraction Logic

### Pattern Recognition
- **Primary**: `YYYYMMDD` at the start of filename
- **Secondary**: `YYYY-MM-DD` format within filename
- **Fallback**: File modification time for files without date patterns

### Sorting Logic
- **Latest first**: Files sorted by extracted date in descending order
- **Combined preferred**: When multiple files exist for same date, combined files win
- **Platform fallback**: Individual platform files used when combined unavailable

## Error Handling

### Missing Files
- **Graceful degradation**: Returns `None` when no files found
- **Clear error messages**: Descriptive logging for debugging
- **Pattern validation**: Validates glob patterns before searching

### Invalid Dates
- **Fallback logic**: Uses file modification time for invalid date patterns
- **Robust parsing**: Handles various date format variations
- **Error logging**: Logs parsing issues for debugging

## Testing

### Validated Scenarios
- ✅ **YouTube cleaned files**: Successfully finds latest extracted data
- ✅ **Reddit cleaned files**: Correctly identifies most recent files
- ✅ **Translated files**: Properly detects NLLB translated files
- ✅ **Entity files**: Accurately finds entity extraction results
- ✅ **Sentiment files**: Prefers combined over individual platform files
- ✅ **Trend files**: Correctly prioritizes combined trend data

### File Pattern Examples
```
data/intermediate/Cleaned_data/20250617_2025-06-11_youtube_comments_cleaned.csv
data/intermediate/translated/20250617_2025-06-11_youtube_comments_cleaned_nllb_translated.csv
data/intermediate/entity_extraction/20250617_youtube_entities.csv
data/intermediate/sentiment_analysis/reddit_combined_sentiment_original_data_20250617_051234.csv
data/intermediate/trend_detection/artist_trends_20250617_combined.csv
```

## Benefits

### Automation
- **No manual file paths**: Completely eliminates hardcoded file paths
- **Always latest data**: Automatically processes most recent data
- **Smart file selection**: Intelligent preference for combined datasets

### Reliability
- **Robust pattern matching**: Handles various filename formats
- **Error resilience**: Graceful handling of missing or malformed files
- **Consistent behavior**: Predictable file selection across all pipeline steps

### Maintainability
- **Single source of truth**: Centralized file detection logic
- **Easy updates**: Simple pattern modifications for new file formats
- **Clear documentation**: Well-documented patterns and behaviors
