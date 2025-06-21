#!/usr/bin/env python3
"""
Standalone File Detection Utilities for Airflow DAGs

Self-contained file detection functions to avoid import issues in Airflow.
"""

import os
import re
from pathlib import Path
from typing import Optional, Tuple

def find_latest_file(directory: str, pattern: str, prefer_combined: bool = True) -> Optional[str]:
    """
    Find the most recent file matching the given pattern.

    Args:
        directory: Directory to search in
        pattern: Regex pattern to match files
        prefer_combined: If True, prefer files with 'combined' in name over individual platform files

    Returns:
        Path to the most recent matching file, or None if no matches found
    """
    directory_path = Path(directory)
    if not directory_path.exists():
        print(f"Warning: Directory does not exist: {directory}")
        return None

    matching_files = []

    for file_path in directory_path.glob("*.csv"):
        if re.search(pattern, file_path.name):
            matching_files.append(file_path)

    if not matching_files:
        print(f"Warning: No files found matching pattern '{pattern}' in {directory}")
        return None

    # Separate combined and individual files
    combined_files = [f for f in matching_files if 'combined' in f.name.lower()]
    individual_files = [f for f in matching_files if 'combined' not in f.name.lower()]

    # Choose file set based on preference
    if prefer_combined and combined_files:
        files_to_consider = combined_files
        print(f"Found {len(combined_files)} combined files, preferring these over {len(individual_files)} individual files")
    else:
        files_to_consider = matching_files
        print(f"Considering all {len(matching_files)} matching files")

    # Sort by modification time (most recent first)
    files_to_consider.sort(key=lambda f: f.stat().st_mtime, reverse=True)

    latest_file = str(files_to_consider[0])
    print(f"Selected latest file: {latest_file}")

    return latest_file

def find_latest_cleaned_file(platform: str, base_dir: str) -> Optional[str]:
    """Find the latest cleaned file for a platform."""
    cleaned_dir = Path(base_dir) / "Cleaned_data"
    pattern = rf"\d{{8}}_.*{platform}_comments_cleaned\.csv"
    return find_latest_file(str(cleaned_dir), pattern, prefer_combined=False)

def find_latest_translated_file(platform: str, base_dir: str) -> Optional[str]:
    """Find the latest translated file for a platform."""
    translated_dir = Path(base_dir) / "translated"
    pattern = rf"\d{{8}}_.*{platform}_comments_cleaned.*translated\.csv"
    return find_latest_file(str(translated_dir), pattern, prefer_combined=False)

def find_latest_entity_file(platform: str, base_dir: str) -> Optional[str]:
    """Find the latest entity extraction file for a platform."""
    entity_dir = Path(base_dir) / "entity_extraction"
    pattern = rf"\d{{8}}_{platform}_entities\.csv"
    return find_latest_file(str(entity_dir), pattern, prefer_combined=False)

def find_latest_sentiment_file(platform: str, base_dir: str) -> Optional[str]:
    """Find the latest sentiment analysis file for a platform."""
    sentiment_dir = Path(base_dir) / "sentiment_analysis"
    # Prefer combined files, then fall back to individual platform files
    combined_pattern = rf"{platform}_combined_sentiment_original_data_\d{{8}}_\d{{6}}\.csv"
    individual_pattern = rf"{platform}_sentiment_results_\d{{8}}_\d{{6}}\.csv"

    # First try to find combined files
    combined_file = find_latest_file(str(sentiment_dir), combined_pattern, prefer_combined=True)
    if combined_file:
        return combined_file

    # Fall back to individual files
    return find_latest_file(str(sentiment_dir), individual_pattern, prefer_combined=False)

def find_latest_trend_files(base_dir: str) -> Tuple[Optional[str], Optional[str], Optional[str], Optional[str]]:
    """
    Find the latest trend analysis files.

    Returns:
        Tuple of (artist_trends, genre_trends, temporal_trends, trend_summary) file paths
    """
    trend_dir = Path(base_dir) / "trend_analysis"

    # Prefer combined files over individual platform files
    artist_file = find_latest_file(str(trend_dir), r"artist_trends_\d{8}_\w+\.csv", prefer_combined=True)
    genre_file = find_latest_file(str(trend_dir), r"genre_trends_\d{8}_\w+\.csv", prefer_combined=True)
    temporal_file = find_latest_file(str(trend_dir), r"temporal_trends_\d{8}_\w+\.csv", prefer_combined=True)

    # Find trend summary JSON
    trend_summary = None
    for file_path in trend_dir.glob("*.json"):
        if re.search(r"trend_summary_\d{8}_\w+\.json", file_path.name):
            if not trend_summary or file_path.stat().st_mtime > Path(trend_summary).stat().st_mtime:
                trend_summary = str(file_path)

    return artist_file, genre_file, temporal_file, trend_summary

def find_latest_summarization_files(base_dir: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Find the latest summarization files.

    Returns:
        Tuple of (insights_summary_json, metrics_csv) file paths
    """
    summarization_dir = Path(base_dir) / "summarization"

    if not summarization_dir.exists():
        print(f"Warning: Summarization directory does not exist: {summarization_dir}")
        return None, None

    # Find insights summary JSON file
    insights_json = None
    for file_path in summarization_dir.glob("*.json"):
        if re.search(r"trend_insights_\d{8}_\w+\.json", file_path.name):
            if not insights_json or file_path.stat().st_mtime > Path(insights_json).stat().st_mtime:
                insights_json = str(file_path)

    # Find metrics CSV file
    metrics_csv = None
    for file_path in summarization_dir.glob("*.csv"):
        if re.search(r"trend_insights_\d{8}_\w+_metrics\.csv", file_path.name):
            if not metrics_csv or file_path.stat().st_mtime > Path(metrics_csv).stat().st_mtime:
                metrics_csv = str(file_path)

    return insights_json, metrics_csv

def find_latest_wordcloud_file(base_dir: str) -> Optional[str]:
    """Find the latest wordcloud text file."""
    wordcloud_file = Path(base_dir) / "wordcloud_source_text.txt"
    return str(wordcloud_file) if wordcloud_file.exists() else None
