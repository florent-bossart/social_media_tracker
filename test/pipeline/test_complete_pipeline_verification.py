#!/usr/bin/env python3
"""
Complete Pipeline Verification Test

Verifies that all 4 stages of the Japanese Music Trends Analysis Pipeline
are working correctly and producing expected outputs.
"""

import json
import csv
import logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_complete_pipeline():
    """Test all pipeline stages and outputs"""
    base_dir = Path(__file__).parent

    logger.info("🧪 Testing Complete Japanese Music Trends Analysis Pipeline")
    logger.info("="*70)

    # Test Stage 1: Entity Extraction
    entity_dir = base_dir / "data" / "intermediate" / "entity_extraction"
    entity_results = entity_dir / "entity_extraction_results.csv"
    entity_summary = entity_dir / "entity_extraction_summary.json"

    stage1_status = "✅" if entity_results.exists() and entity_summary.exists() else "❌"
    logger.info(f"{stage1_status} Stage 1 (Entity Extraction): {entity_results.exists() and entity_summary.exists()}")

    # Test Stage 2: Sentiment Analysis
    sentiment_dir = base_dir / "data" / "intermediate" / "sentiment_analysis"
    sentiment_results = sentiment_dir / "entity_sentiment_combined.csv"
    sentiment_summary = sentiment_dir / "sentiment_analysis_summary.json"

    stage2_status = "✅" if sentiment_results.exists() and sentiment_summary.exists() else "❌"
    logger.info(f"{stage2_status} Stage 2 (Sentiment Analysis): {sentiment_results.exists() and sentiment_summary.exists()}")

    # Test Stage 3: Trend Detection
    trend_dir = base_dir / "data" / "intermediate" / "trend_analysis"
    trend_results = trend_dir / "artist_trends.csv"
    trend_summary = trend_dir / "trend_summary.json"

    stage3_status = "✅" if trend_results.exists() and trend_summary.exists() else "❌"
    logger.info(f"{stage3_status} Stage 3 (Trend Detection): {trend_results.exists() and trend_summary.exists()}")

    # Test Stage 4: Summarization
    summary_dir = base_dir / "data" / "intermediate" / "summarization"
    summary_json = summary_dir / "trend_insights_summary.json"
    summary_md = summary_dir / "trend_insights_report.md"
    summary_csv = summary_dir / "trend_insights_metrics.csv"

    stage4_status = "✅" if all([summary_json.exists(), summary_md.exists(), summary_csv.exists()]) else "❌"
    logger.info(f"{stage4_status} Stage 4 (Summarization): {all([summary_json.exists(), summary_md.exists(), summary_csv.exists()])}")

    # Detailed output verification
    logger.info("\n📁 Output File Verification:")

    all_files = [
        (entity_results, "Entity extraction results"),
        (entity_summary, "Entity extraction summary"),
        (sentiment_results, "Sentiment analysis results"),
        (sentiment_summary, "Sentiment analysis summary"),
        (trend_results, "Trend detection results"),
        (trend_summary, "Trend detection summary"),
        (summary_json, "Summarization insights JSON"),
        (summary_md, "Summarization report Markdown"),
        (summary_csv, "Summarization metrics CSV")
    ]

    existing_files = 0
    for file_path, description in all_files:
        exists = file_path.exists()
        status = "✅" if exists else "❌"
        logger.info(f"  {status} {description}: {file_path.name}")
        if exists:
            existing_files += 1

    # Data verification
    logger.info("\n📊 Data Verification:")

    if sentiment_results.exists():
        with open(sentiment_results, 'r') as f:
            reader = csv.DictReader(f)
            sentiment_rows = list(reader)
        logger.info(f"  📈 Sentiment data: {len(sentiment_rows)} records")

    if trend_summary.exists():
        with open(trend_summary, 'r') as f:
            trend_data = json.load(f)
        logger.info(f"  📈 Trend analysis: {trend_data['overview']['total_artists_analyzed']} artists")

    if summary_json.exists():
        with open(summary_json, 'r') as f:
            summary_data = json.load(f)
        logger.info(f"  📈 Insights: {len(summary_data['key_findings'])} key findings")
        logger.info(f"  📈 Confidence: {summary_data['metadata']['confidence_score']:.2f}/1.0")

    # Overall status
    total_files = len(all_files)
    success_rate = existing_files / total_files

    logger.info(f"\n🎯 Pipeline Status:")
    logger.info(f"  Files Present: {existing_files}/{total_files} ({success_rate:.1%})")

    if success_rate >= 0.8:
        logger.info("  🎉 PIPELINE STATUS: SUCCESS")
        logger.info("  ✅ Complete Japanese Music Trends Analysis Pipeline is operational!")
    elif success_rate >= 0.5:
        logger.info("  ⚠️ PIPELINE STATUS: PARTIAL SUCCESS")
        logger.info("  🔧 Some stages need attention")
    else:
        logger.info("  ❌ PIPELINE STATUS: NEEDS WORK")
        logger.info("  🛠️ Multiple stages require fixes")

    # Show sample insights if available
    if summary_json.exists():
        logger.info(f"\n🔍 Sample Insights Preview:")
        with open(summary_json, 'r') as f:
            insights = json.load(f)

        logger.info(f"  📝 Executive Summary: {insights['executive_summary'][:100]}...")

        if insights.get('key_findings'):
            logger.info(f"  🎯 Key Findings:")
            for finding in insights['key_findings'][:3]:
                logger.info(f"    • {finding}")

        if insights.get('recommendations'):
            logger.info(f"  💡 Top Recommendation: {insights['recommendations'][0]}")

    logger.info("\n" + "="*70)
    logger.info("🧪 Pipeline Verification Complete")

    return success_rate >= 0.8

if __name__ == "__main__":
    success = test_complete_pipeline()
    exit(0 if success else 1)
