#!/usr/bin/env python3
"""
Test script for summarization module
"""

import sys
import os
sys.path.append('/home/florent.bossart/code/florent-bossart/social_media_tracker')

try:
    print("Testing summarization module...")

    # Import the module
    from summarization_standalone import TrendSummarizer
    print("✅ Successfully imported TrendSummarizer")

    # Initialize
    summarizer = TrendSummarizer()
    print("✅ Successfully initialized TrendSummarizer")

    # Test file paths
    base_dir = "/home/florent.bossart/code/florent-bossart/social_media_tracker"
    trend_summary_path = f"{base_dir}/data/intermediate/trend_analysis/trend_summary.json"
    artist_trends_path = f"{base_dir}/data/intermediate/trend_analysis/artist_trends.csv"

    print(f"Trend summary path: {trend_summary_path}")
    print(f"Artist trends path: {artist_trends_path}")

    # Check if files exist
    if os.path.exists(trend_summary_path):
        print("✅ Trend summary file exists")
    else:
        print("❌ Trend summary file missing")

    if os.path.exists(artist_trends_path):
        print("✅ Artist trends file exists")
    else:
        print("❌ Artist trends file missing")

    # Try to load data
    if os.path.exists(trend_summary_path) and os.path.exists(artist_trends_path):
        print("Loading trend data...")
        trend_data = summarizer.load_trend_data(trend_summary_path, artist_trends_path)
        print(f"✅ Successfully loaded trend data: {len(trend_data.get('artist_trends', []))} artists")

        print("Generating summary...")
        summary = summarizer.generate_complete_summary(trend_summary_path, artist_trends_path)
        print("✅ Successfully generated summary")

        print("Exporting summary...")
        output_dir = f"{base_dir}/data/intermediate/summarization"
        outputs = summarizer.export_summary(summary, output_dir)
        print(f"✅ Successfully exported to: {outputs}")

        print("\n📊 SUMMARY RESULTS:")
        print(f"Key Findings: {len(summary['key_findings'])}")
        print(f"Artist Insights: {len(summary['artist_insights'])}")
        print(f"Recommendations: {len(summary['recommendations'])}")
        print(f"Confidence Score: {summary['metadata']['confidence_score']:.2f}")

    else:
        print("❌ Cannot proceed without input files")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
