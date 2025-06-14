# YouTube Comments Translation Script - Usage Guide

This script translates Japanese YouTube comments to English using the NLLB model.

## Current Behavior vs New Options

### Original Script Behavior:
- **Processes ALL YouTube files** in the folder matching the pattern

### New Script Options:
- **Process ALL files** (default): Same as original behavior
- **Process LATEST file only**: Use `--latest-only` flag

## Usage Examples

### 1. Process ONLY the latest YouTube file (recommended):
```bash
cd /home/florent.bossart/code/florent-bossart/social_media_tracker
poetry run python data_pipeline/translate_youtube_comments.py --latest-only
```

### 2. Process ALL YouTube files in the folder:
```bash
poetry run python data_pipeline/translate_youtube_comments.py
```

### 3. Process a specific file:
```bash
poetry run python data_pipeline/translate_youtube_comments.py --input-file data/intermediate/Cleaned_data/20250610_2025-05-31_youtube_comments_cleaned.csv
```

### 4. Customize the output directory:
```bash
poetry run python data_pipeline/translate_youtube_comments.py --latest-only --output-dir data/intermediate/my_translations
```

## Available Options

- `--latest-only`: Process only the most recent file (by date in filename)
- `--input-file`: Specify exact file path to process
- `--input-pattern`: File pattern to search for (default: `*youtube_comments_cleaned.csv`)
- `--column`: Column name to translate (default: `text_clean`)
- `--output-column`: Name for translated column (default: `text_clean_en_nllb`)
- `--output-dir`: Output directory (default: `data/intermediate/translated`)

## File Detection Logic

The script looks for files with pattern `YYYYMMDD_*_youtube_***.csv` in:
`/home/florent.bossart/code/florent-bossart/social_media_tracker/data/intermediate/Cleaned_data/`

When using `--latest-only`, it sorts by the date (YYYYMMDD) at the beginning of the filename and picks the most recent one.

## Expected Output

- Input: `20250610_2025-05-31_youtube_comments_cleaned.csv`
- Output: `20250610_2025-05-31_youtube_comments_cleaned_nllb_translated.csv`
- Location: `data/intermediate/translated/` (or your custom output directory)

## Based on Your Current Files:

Your current YouTube files:
- `20250528_full_youtube_comments_cleaned.csv`
- `20250530_full_youtube_comments_cleaned.csv`
- `20250610_2025-05-31_youtube_comments_cleaned.csv` ← **This would be selected as latest**

## Recommended Command:

```bash
poetry run python data_pipeline/translate_youtube_comments.py --latest-only
```

This will process only the most recent file: `20250610_2025-05-31_youtube_comments_cleaned.csv`
