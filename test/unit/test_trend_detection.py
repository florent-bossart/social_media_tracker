#!/usr/bin/env python3
"""
Test Script for Trend Detection Module

This script tests the trend detection functionality with the existing
entity-sentiment combined data.

Author: GitHub Copilot Assistant
Date: 2025-01-07
"""

import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_pipeline.trend_detection import TrendDetector
from data_pipeline.trend_detection_config import TrendDetectionConfig, get_config
import json

def test_trend_detection():
    """Test the trend detection module"""
    print("🔍 Testing Trend Detection Module")
    print("=" * 50)

    # Input and output paths
    input_file = "data/intermediate/sentiment_analysis/entity_sentiment_combined.csv"
    output_dir = "data/intermediate/trend_analysis"

    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"❌ Input file not found: {input_file}")
        return False

    try:
        # Initialize trend detector with development config
        config = get_config("development")
        detector = TrendDetector(config)

        print(f"📁 Input file: {input_file}")
        print(f"📁 Output directory: {output_dir}")
        print()

        # Run trend analysis
        print("🚀 Starting trend analysis...")
        result = detector.analyze_trends(input_file, output_dir)

        if result["status"] == "success":
            print("✅ Trend analysis completed successfully!")
            print()

            # Display summary
            summary = result["summary"]
            print("📊 ANALYSIS SUMMARY")
            print("-" * 30)
            print(f"Analysis timestamp: {summary['analysis_timestamp']}")
            print(f"Artists analyzed: {summary['overview']['total_artists_analyzed']}")
            print(f"Genres analyzed: {summary['overview']['total_genres_analyzed']}")
            print(f"Time periods: {summary['overview']['time_periods_analyzed']}")
            print()

            # Top artists
            if summary["top_artists"]:
                print("🎤 TOP ARTISTS")
                print("-" * 20)
                for i, artist in enumerate(summary["top_artists"], 1):
                    print(f"{i}. {artist['name']}")
                    print(f"   Trend Strength: {artist['trend_strength']}")
                    print(f"   Mentions: {artist['mentions']}")
                    print(f"   Sentiment: {artist['sentiment']}")
                    print(f"   Platforms: {', '.join(artist['platforms'])}")
                    print()

            # Top genres
            if summary["top_genres"]:
                print("🎵 TOP GENRES")
                print("-" * 20)
                for i, genre in enumerate(summary["top_genres"], 1):
                    print(f"{i}. {genre['name']}")
                    print(f"   Popularity Score: {genre['popularity_score']}")
                    print(f"   Sentiment Trend: {genre['sentiment_trend']}")
                    print(f"   Artist Diversity: {genre['artist_diversity']}")
                    print(f"   Platform Presence: {genre['platforms']}")
                    print()

            # Sentiment patterns
            print("😊 SENTIMENT PATTERNS")
            print("-" * 25)
            patterns = summary["sentiment_patterns"]
            print(f"Positive trends: {patterns['positive_trends']}")
            print(f"Negative trends: {patterns['negative_trends']}")
            print(f"Neutral trends: {patterns['neutral_trends']}")
            print()

            # Engagement levels
            print("📈 ENGAGEMENT LEVELS")
            print("-" * 23)
            engagement = summary["engagement_levels"]
            print(f"High engagement: {engagement['high']}")
            print(f"Medium engagement: {engagement['medium']}")
            print(f"Low engagement: {engagement['low']}")
            print()

            # Output files
            print("📁 OUTPUT FILES")
            print("-" * 18)
            for file_type, file_path in result["output_files"].items():
                print(f"{file_type}: {file_path}")
            print()

            # Metrics
            metrics = result["metrics"]
            print(f"✨ Generated {metrics['artist_trends_found']} artist trends")
            print(f"✨ Generated {metrics['genre_trends_found']} genre trends")
            print(f"✨ Analyzed {metrics['temporal_periods_analyzed']} temporal periods")

            return True

        else:
            print(f"❌ Trend analysis failed: {result['error']}")
            return False

    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_configuration():
    """Test configuration validation"""
    print("\n🔧 Testing Configuration")
    print("=" * 30)

    # Test default configuration
    config = TrendDetectionConfig()
    issues = config.validate()

    if issues:
        print("❌ Default configuration issues:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("✅ Default configuration is valid")

    # Test different config types
    for config_type in ["development", "production", "research"]:
        config = get_config(config_type)
        issues = config.validate()
        status = "✅" if not issues else "❌"
        print(f"{status} {config_type.capitalize()} configuration")
        if issues:
            for issue in issues:
                print(f"    - {issue}")

def main():
    """Main test function"""
    print("🧪 TREND DETECTION MODULE TESTS")
    print("=" * 40)

    # Test configuration first
    test_configuration()

    # Test trend detection functionality
    success = test_trend_detection()

    if success:
        print("\n🎉 All tests completed successfully!")
        return 0
    else:
        print("\n💥 Some tests failed!")
        return 1

if __name__ == "__main__":
    exit(main())
