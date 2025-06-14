# Extract Cleaned Comments by Date - Usage Guide

This script is a copy of `extract_cleaned_comments.py` with date filtering capabilities.

## Features

- Extract Reddit and YouTube comments with optional date filtering
- Support for filtering by `fetch_date_fmt` (Reddit) and `fetch_date` (YouTube)
- Command-line interface with argument parsing
- Option to extract from specific sources (reddit, youtube, or both)

## Usage

### Basic Usage (Extract all comments)
```bash
python extract_cleaned_comments_by_date.py
```

### Extract comments from a specific date onwards
```bash
python extract_cleaned_comments_by_date.py --date 2024-12-01
```

### Extract only Reddit comments from a specific date
```bash
python extract_cleaned_comments_by_date.py --date 2024-12-01 --source reddit
```

### Extract only YouTube comments from a specific date
```bash
python extract_cleaned_comments_by_date.py --date 2024-12-01 --source youtube
```

## Arguments

- `--date`: Filter date in YYYY-MM-DD format. Extract comments with fetch date >= this date (optional)
- `--source`: Source to extract from: reddit, youtube, or both (default: both)

## Date Filtering Logic

- **Reddit**: Uses `fetch_date_fmt >= provided_date`
- **YouTube**: Uses `fetch_date >= provided_date`

## Output Files

Files are saved to `data/intermediate/` with the following naming convention:
- `{extraction_date}_{filter_date}_{source}_comments_cleaned.csv` (when date filter is used)
- `{extraction_date}_{source}_comments_cleaned.csv` (when no date filter is used)

## Examples

1. Extract all comments from both sources:
   ```bash
   python extract_cleaned_comments_by_date.py --source both
   ```

2. Extract Reddit comments from June 1st, 2024 onwards:
   ```bash
   python extract_cleaned_comments_by_date.py --date 2024-06-01 --source reddit
   ```

3. Extract YouTube comments from a specific date:
   ```bash
   python extract_cleaned_comments_by_date.py --date 2024-05-15 --source youtube
   ```
