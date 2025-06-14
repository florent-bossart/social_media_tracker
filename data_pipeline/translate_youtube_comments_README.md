# YouTube Comments Translation Guide

This script translates Japanese YouTube comments to English using the NLLB (No Language Left Behind) model.

## Usage Examples

### 1. Translate a specific file
```bash
poetry run python data_pipeline/translate_youtube_comments.py --input-file data/intermediate/Cleaned_data/20250610_2025-05-31_youtube_comments_cleaned.csv
```

### 2. Translate all YouTube comment files (default behavior)
```bash
poetry run python data_pipeline/translate_youtube_comments.py
```

### 3. Translate files with a specific pattern
```bash
poetry run python data_pipeline/translate_youtube_comments.py --input-pattern "*2025-05-31*youtube*.csv"
```

### 4. Custom column names and output directory
```bash
poetry run python data_pipeline/translate_youtube_comments.py \
  --column text_clean \
  --output-column text_english \
  --output-dir data/intermediate/my_translations
```

## Arguments

- `--input-file`: Path to a specific file to translate
- `--input-pattern`: File pattern to search for (default: `*youtube_comments_cleaned.csv`)
- `--column`: Column containing text to translate (default: `text_clean`)
- `--output-column`: Name for translated column (default: `text_clean_en_nllb`)
- `--output-dir`: Output directory (default: `data/intermediate/translated`)

## What it does

1. **Detects Japanese text**: Only translates text containing Japanese characters
2. **Batch processing**: Processes multiple texts efficiently
3. **Preserves data**: Keeps all original columns and adds translation column
4. **Smart naming**: Adds `_nllb_translated` suffix to output files
5. **Progress tracking**: Shows translation progress with progress bars

## Output

The script creates new CSV files with the same structure as input files, plus an additional column containing English translations of Japanese text. Non-Japanese text is left untranslated.

Output files are saved with `_nllb_translated.csv` suffix.
