#!/usr/bin/env python3
"""
Direct Sentiment Analysis Pipeline

This script runs sentiment analysis on specified platform data (YouTube or Reddit)
and combines results with original data, including placeholders for entity fields.
"""

import pandas as pd
import json
import os
import sys
from pathlib import Path
import argparse
from datetime import datetime # Added for timestamping

# Get the directory of the current script (data_pipeline)
_CURRENT_SCRIPT_DIR = Path(__file__).resolve().parent
# Get the project root directory (one level up from data_pipeline)
_PROJECT_ROOT = _CURRENT_SCRIPT_DIR.parent

# Add project root to sys.path to allow imports from llm_enrichment, etc.
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from llm_enrichment.sentiment.sentiment_analysis import SentimentAnalyzer

def main():
    print("🚀 Real Sentiment Analysis Pipeline")
    print("=" * 50)

    # --- Argument Parsing ---
    parser = argparse.ArgumentParser(description="Run sentiment analysis on YouTube or Reddit data.")
    parser.add_argument(
        "platform",
        type=str,
        choices=["youtube", "reddit"],
        help="Platform to process ('youtube' or 'reddit'). Used for determining source platform value and default file/column names if --input_file is not specified."
    )
    parser.add_argument(
        "--input_file",
        type=str,
        default=None,
        help="Optional: Path to a specific input CSV file (relative to project root if not absolute). Overrides platform-based file selection."
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default="data/intermediate/sentiment_analysis", # Relative to project root
        help="Directory to save the output files (relative to project root if not absolute)."
    )
    parser.add_argument(
        "--ollama-host",
        type=str,
        default=None,
        help="Optional: Ollama host URL (e.g., http://localhost:11434 or ngrok URL). Overrides the default in sentiment_analysis_config.py."
    )
    args = parser.parse_args()
    # --- End Argument Parsing ---

    platform = args.platform
    
    # Resolve output_dir relative to _PROJECT_ROOT if it's not absolute
    output_dir_path = Path(args.output_dir)
    if not output_dir_path.is_absolute():
        output_dir_path = _PROJECT_ROOT / output_dir_path
    output_dir_path.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    # --- File and Column Configuration based on Platform ---
    source_platform_value = platform # Platform argument always defines the source_platform for output

    if args.input_file:
        input_file_path_arg = Path(args.input_file)
        if not input_file_path_arg.is_absolute():
            input_file_path = _PROJECT_ROOT / input_file_path_arg
        else:
            input_file_path = input_file_path_arg
        # When a specific input file is given (e.g., entity extraction output),
        # assume standardized column names from that process.
        id_column = "id"
        text_column_primary = "original_text"
        text_column_secondary = None # Entity extraction output should have a single, clean text column
        print(f"ℹ️ Using provided input file: {input_file_path}")
        print(f"ℹ️ Expecting standardized ID column: '{id_column}' and Text column: '{text_column_primary}' from input file.")
    else:
        # Default behavior: determine input file and columns based on platform for raw data
        if platform == "youtube":
            id_column = "comment_pk"  # Standard ID column for YouTube raw data
            text_column_primary = "comment_text_en_nllb"  # Standard text column for YouTube raw data
            text_column_secondary = "comment_text"  # Fallback text column for YouTube raw data
            default_input_filename = "20250528_full_youtube_comments_cleaned_nllb_translated.csv"
        elif platform == "reddit":
            id_column = "comment_id"  # Standard ID column for Reddit raw data
            text_column_primary = "body_clean"  # Standard text column for Reddit raw data
            text_column_secondary = None
            default_input_filename = "20250528_full_reddit_comments_cleaned.csv"
        else:
            # This case should not be reached due to argparse choices
            print(f"❌ Unknown platform: {platform}")
            sys.exit(1)
        # Use _PROJECT_ROOT to find the data directory from the new script location
        input_file_path = _PROJECT_ROOT / "data" / "intermediate" / default_input_filename
        print(f"ℹ️ Using platform-default input file for {platform}: {input_file_path}")
        print(f"ℹ️ Expecting platform-specific ID column: '{id_column}' and Text column: '{text_column_primary}'")
    # --- End File and Column Configuration ---

    print(f"📂 Loading: {input_file_path} for platform: {platform}")
    if not input_file_path.exists():
        print(f"❌ Input file not found: {input_file_path}")
        sys.exit(1)

    original_df = pd.read_csv(input_file_path)
    print(f"📄 Loaded {len(original_df)} total records from {input_file_path}")

    # DEBUG: Print column names and head of the loaded DataFrame
    print(f"DEBUG: Columns in original_df: {original_df.columns.tolist()}")
    if not original_df.empty:
        print(f"DEBUG: First 3 rows of original_df:\\n{original_df.head(3)}")
        # Check if expected columns exist and print some of their values
        if id_column in original_df.columns:
            print(f"DEBUG: Sample of '{id_column}' column (first 3 values):\\n{original_df[id_column].head(3)}")
            print(f"DEBUG: Count of non-NA in '{id_column}': {original_df[id_column].notna().sum()} out of {len(original_df)}")
        else:
            print(f"DEBUG: Expected ID column '{id_column}' NOT FOUND in original_df.")

        if text_column_primary in original_df.columns:
            print(f"DEBUG: Sample of '{text_column_primary}' column (first 3 values):\\n{original_df[text_column_primary].head(3)}")
            print(f"DEBUG: Count of non-NA in '{text_column_primary}': {original_df[text_column_primary].notna().sum()} out of {len(original_df)}")
            # Count non-empty strings after stripping
            non_empty_text_count = original_df[text_column_primary].astype(str).str.strip().ne('').sum()
            print(f"DEBUG: Count of non-empty strings in '{text_column_primary}': {non_empty_text_count} out of {len(original_df)}")
        else:
            print(f"DEBUG: Expected primary text column '{text_column_primary}' NOT FOUND in original_df.")

        if text_column_secondary and text_column_secondary in original_df.columns:
            print(f"DEBUG: Sample of '{text_column_secondary}' column (first 3 values):\\n{original_df[text_column_secondary].head(3)}")
            print(f"DEBUG: Count of non-NA in '{text_column_secondary}': {original_df[text_column_secondary].notna().sum()} out of {len(original_df)}")
            non_empty_text_secondary_count = original_df[text_column_secondary].astype(str).str.strip().ne('').sum()
            print(f"DEBUG: Count of non-empty strings in '{text_column_secondary}': {non_empty_text_secondary_count} out of {len(original_df)}")
        elif text_column_secondary:
            print(f"DEBUG: Expected secondary text column '{text_column_secondary}' NOT FOUND in original_df.")
    # END DEBUG

    # Prepare DataFrame for sentiment analysis (needs 'id', 'original_text', 'source_platform')
    comments_for_analysis = []
    for _, row in original_df.iterrows():
        text_to_analyze = ""
        # Prioritize primary text column, then secondary if available
        primary_text = row.get(text_column_primary, "")
        if pd.notna(primary_text) and str(primary_text).strip() != "":
            text_to_analyze = str(primary_text)
        elif text_column_secondary: # Check if a secondary column is defined
            secondary_text = row.get(text_column_secondary, "")
            if pd.notna(secondary_text) and str(secondary_text).strip() != "":
                text_to_analyze = str(secondary_text)

        current_id = row.get(id_column)
        if pd.notna(current_id) and text_to_analyze.strip() != "": # Ensure text_to_analyze is not empty
            comments_for_analysis.append({
                "id": current_id,
                "original_text": text_to_analyze, # Already ensured it's a string and stripped
                "source_platform": source_platform_value
            })

    # DEBUG: Print length of comments_for_analysis
    print(f"DEBUG: Number of records prepared for sentiment analysis (len(comments_for_analysis)): {len(comments_for_analysis)}")
    if not comments_for_analysis and not original_df.empty:
        print(f"DEBUG: comments_for_analysis is empty. This means the condition (pd.notna(current_id) and text_to_analyze.strip() != '') was false for all rows.")
        print(f"DEBUG: Review the DEBUG output above to check if '{id_column}' and '{text_column_primary}' (or '{text_column_secondary}') exist and contain valid, non-empty data in the input CSV: {input_file_path}")
    # END DEBUG

    df_with_text = pd.DataFrame(comments_for_analysis)
    df_with_text = df_with_text.dropna(subset=['id', 'original_text']) # Ensure no NaN ids or texts

    if df_with_text.empty:
        print("❌ No valid text found for sentiment analysis after processing. Exiting.")
        sys.exit(1)

    print(f"📊 Prepared {len(df_with_text)} records with text for sentiment analysis.")

    # Show sample data for analysis
    print(f"\n📋 Sample Records for Analysis (first 3 with text):")
    for idx, row in df_with_text.head(3).iterrows():
        print(f"   ID {row['id']}: {str(row['original_text'])[:60]}...")

    # Run sentiment analysis
    print(f"\n🤖 Running sentiment analysis...")
    if args.ollama_host:
        print(f"   Using Ollama host: {args.ollama_host}")
    analyzer = SentimentAnalyzer(ollama_host=args.ollama_host) # Pass ollama_host
    results_df = analyzer.process_comments_batch(df_with_text) # Renamed to results_df

    print(f"✅ Processed {len(results_df)} comments for sentiment.")

    # Show sentiment results summary
    print(f"\n📈 Sentiment Results Summary:")
    if not results_df.empty:
        sentiment_counts = results_df['overall_sentiment'].value_counts()
        for sentiment, count in sentiment_counts.items():
            print(f"   {str(sentiment).capitalize()}: {count} ({count/len(results_df)*100:.1f}%)")
        avg_confidence = results_df['sentiment_confidence_score' if 'sentiment_confidence_score' in results_df.columns else 'confidence_score'].mean() # Handle potential rename
        print(f"   Average Sentiment Confidence: {avg_confidence:.3f}")
    else:
        print("   No sentiment results to summarize.")

    # Save sentiment results
    sentiment_output_filename = f"{platform}_sentiment_results_{timestamp}.csv"
    sentiment_output_file_path = output_dir_path / sentiment_output_filename # Use resolved path
    results_df.to_csv(sentiment_output_file_path, index=False, na_rep='NULL')
    print(f"\n📁 Sentiment analysis results saved to: {sentiment_output_file_path}")

    # Show sample sentiment results
    print(f"\n📋 Sample Sentiment Results (first 2):")
    for _, row in results_df.head(2).iterrows():
        print(f"--- Record ID {row['id']} ---")
        print(f"Text: {str(row['original_text'])[:60]}...")
        print(f"Sentiment: {row['overall_sentiment']} (strength: {row.get('sentiment_strength', 'N/A')}/10)")
        print(f"Confidence: {row.get('sentiment_confidence_score', row.get('confidence_score', 'N/A')):.3f}") # Handle potential rename
        print(f"Aspects: Artist={row.get('artist_sentiment', 'N/A')}, Music={row.get('music_quality_sentiment', 'N/A')}")
        print()

    # Create combined data: original data + sentiment results + entity placeholders
    print(f"\n🔗 Creating combined data...")

    # Prepare original_df for merge by creating a common 'id' column for merging
    # This 'id' column in original_df_for_merge will match the 'id' column in results_df
    original_df_for_merge = original_df.copy()
    original_df_for_merge['id_for_merge'] = original_df_for_merge[id_column]

    # Ensure 'id_for_merge' and results_df['id'] are of compatible types
    if not pd.api.types.is_dtype_equal(original_df_for_merge['id_for_merge'].dtype, results_df['id'].dtype):
        try:
            print(f"Aligning ID types for merge. Original DF ID type: {original_df_for_merge['id_for_merge'].dtype}, Results DF ID type: {results_df['id'].dtype}")
            original_df_for_merge['id_for_merge'] = original_df_for_merge['id_for_merge'].astype(results_df['id'].dtype)
        except Exception as e:
            print(f"Warning: Could not cast original DF ID type to results DF ID type: {e}. Trying string conversion for merge.")
            original_df_for_merge['id_for_merge'] = original_df_for_merge['id_for_merge'].astype(str)
            results_df['id'] = results_df['id'].astype(str)

    combined_df = pd.merge(
        original_df_for_merge,
        results_df,
        left_on='id_for_merge',
        right_on='id',
        how='left', # Keep all original rows, add sentiment where available
        suffixes=('_orig', None) # Suffix for conflicting columns from original_df if any
    )

    # Clean up merged columns
    if 'id_orig' in combined_df.columns and 'id' in combined_df.columns: # 'id' from results_df is preferred
        combined_df = combined_df.drop(columns=['id_orig'])
    if 'id_for_merge' in combined_df.columns: # Drop the temporary merge key
         combined_df = combined_df.drop(columns=['id_for_merge'])

    # 'original_text' from results_df is the one analyzed. If original_df also had 'original_text', it's now 'original_text_orig'.
    if 'original_text_orig' in combined_df.columns and 'original_text' in combined_df.columns:
        combined_df = combined_df.drop(columns=['original_text_orig'])
    # Same for 'source_platform'
    if 'source_platform_orig' in combined_df.columns and 'source_platform' in combined_df.columns:
        combined_df = combined_df.drop(columns=['source_platform_orig'])

    # Add placeholder entity columns
    entity_placeholder_columns = {
        'entity_confidence': None, 'artists_found': '[]', 'artists_count': 0,
        'songs_found': '[]', 'songs_count': 0, 'genres_found': '[]', 'genres_count': 0,
        'events_found': '[]', 'events_count': 0, 'albums_found': '[]', 'albums_count': 0,
        'music_labels_found': '[]', 'music_labels_count': 0, 'other_entities_found': '[]', 'other_entities_count': 0,
        'locations_found': '[]', 'locations_count': 0, 'organizations_found': '[]', 'organizations_count': 0,
        'persons_found': '[]', 'persons_count': 0, 'products_found': '[]', 'products_count': 0,
        'technologies_found': '[]', 'technologies_count': 0,
    }
    for col_name, default_value in entity_placeholder_columns.items():
        if col_name not in combined_df.columns: # Add only if not present
            combined_df[col_name] = default_value

    # Ensure 'sentiment_confidence_score' is the final name for this field from results
    if 'confidence_score' in combined_df.columns and 'sentiment_confidence_score' not in combined_df.columns:
         combined_df = combined_df.rename(columns={'confidence_score': 'sentiment_confidence_score'})


    # Save combined data
    combined_filename = f"{platform}_combined_sentiment_original_data_{timestamp}.csv"
    combined_file_path = output_dir_path / combined_filename # Use resolved path
    combined_df.to_csv(combined_file_path, index=False, na_rep='NULL')

    print(f"\n📁 Combined data saved to: {combined_file_path}")
    print(f"📊 Combined data has {len(combined_df)} records with {len(combined_df.columns)} columns.")

    print(f"\n✅ Sentiment analysis pipeline for '{platform}' completed.")
    print(f"   Next steps might involve Trend Detection, Summarization, or Database Integration.")

    return True

if __name__ == "__main__":
    main()
