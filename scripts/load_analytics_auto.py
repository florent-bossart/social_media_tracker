#!/usr/bin/env python3
"""
Auto-detect and load latest analytics data files.
"""

import os
import sys
import glob
from pathlib import Path
import subprocess

def find_latest_file(pattern, directory):
    """Find the most recent file matching the pattern in the directory."""
    files = glob.glob(os.path.join(directory, pattern))
    if not files:
        return None
    # Sort by modification time, most recent first
    files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    return files[0]

def main():
    # Base directory
    base_dir = '/app/airflow/data/intermediate'

    # Find latest files
    entity_reddit = find_latest_file('*reddit_entities.csv', f'{base_dir}/entity_extraction')
    entity_youtube = find_latest_file('*youtube_entities.csv', f'{base_dir}/entity_extraction')
    sentiment_reddit = find_latest_file('reddit_*_sentiment_*.csv', f'{base_dir}/sentiment_analysis')
    sentiment_youtube = find_latest_file('youtube_*_sentiment_*.csv', f'{base_dir}/sentiment_analysis')
    artist_trends = find_latest_file('artist_trends_*.csv', f'{base_dir}/trend_analysis')
    genre_trends = find_latest_file('genre_trends_*.csv', f'{base_dir}/trend_analysis')
    temporal_trends = find_latest_file('temporal_trends_*.csv', f'{base_dir}/trend_analysis')
    trend_summary = find_latest_file('trend_summary_*.json', f'{base_dir}/trend_analysis')
    insights_summary = find_latest_file('trend_insights_*.json', f'{base_dir}/summarization')
    metrics_csv = find_latest_file('*_metrics.csv', f'{base_dir}/summarization')
    wordcloud_file = f'{base_dir}/wordcloud_source_text.txt'

    # Build command
    cmd_parts = ['python', '/app/data_pipeline/load_analytics_data.py']

    if entity_reddit:
        cmd_parts.extend(['--entities-file-reddit', entity_reddit])
    if entity_youtube:
        cmd_parts.extend(['--entities-file-youtube', entity_youtube])
    if sentiment_reddit:
        cmd_parts.extend(['--sentiment-file-reddit', sentiment_reddit])
    if sentiment_youtube:
        cmd_parts.extend(['--sentiment-file-youtube', sentiment_youtube])
    if artist_trends:
        cmd_parts.extend(['--artist-trends-file', artist_trends])
    if genre_trends:
        cmd_parts.extend(['--genre-trends-file', genre_trends])
    if temporal_trends:
        cmd_parts.extend(['--temporal-trends-file', temporal_trends])
    if trend_summary:
        cmd_parts.extend(['--trend-summary-json', trend_summary])
    if insights_summary:
        cmd_parts.extend(['--insights-summary-json', insights_summary])
    if metrics_csv:
        cmd_parts.extend(['--summarization-metrics-file', metrics_csv])
    if os.path.exists(wordcloud_file):
        cmd_parts.extend(['--wordcloud-text-file', wordcloud_file])

    # Add truncate flag
    cmd_parts.append('--truncate')

    print('Files found:')
    print(f'  Entity Reddit: {entity_reddit}')
    print(f'  Entity YouTube: {entity_youtube}')
    print(f'  Sentiment Reddit: {sentiment_reddit}')
    print(f'  Sentiment YouTube: {sentiment_youtube}')
    print(f'  Artist Trends: {artist_trends}')
    print(f'  Genre Trends: {genre_trends}')
    print(f'  Temporal Trends: {temporal_trends}')
    print(f'  Trend Summary: {trend_summary}')
    print(f'  Insights Summary: {insights_summary}')
    print(f'  Metrics CSV: {metrics_csv}')
    print(f'  Wordcloud: {wordcloud_file if os.path.exists(wordcloud_file) else "Not found"}')

    print(f'Running command: {" ".join(cmd_parts)}')

    # Execute the loading script
    result = subprocess.run(cmd_parts, capture_output=True, text=True)
    print(f'Return code: {result.returncode}')
    print(f'STDOUT: {result.stdout}')
    if result.stderr:
        print(f'STDERR: {result.stderr}')

    if result.returncode != 0:
        sys.exit(1)

if __name__ == '__main__':
    main()
