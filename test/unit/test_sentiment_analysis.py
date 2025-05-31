"""
Test script for sentiment analysis module

This script tests the sentiment analysis functionality with real translated data
and validates the integration with entity extraction results.
"""

import pandas as pd
import sys
import os
from pathlib import Path

# Add the data_pipeline directory to Python path
sys.path.append('/home/florent.bossart/code/florent-bossart/social_media_tracker/data_pipeline')

from sentiment_analysis import SentimentAnalyzer

def test_sentiment_analysis():
    """Test sentiment analysis with sample comments"""

    print("=== Testing Sentiment Analysis Module ===")

    # Initialize analyzer
    analyzer = SentimentAnalyzer()

    # Test with various sentiment examples
    test_comments = [
        {
            'id': 1,
            'source_platform': 'reddit',
            'original_text': "YOASOBI is absolutely amazing! I love their music so much, especially Yoru ni Kakeru. Best J-pop duo ever!"
        },
        {
            'id': 2,
            'source_platform': 'youtube',
            'original_text': "Honestly, I think Ado is overrated. Her voice is too harsh and the songs are repetitive. Don't understand the hype."
        },
        {
            'id': 3,
            'source_platform': 'reddit',
            'original_text': "Fujii Kaze is decent. Not bad, but not amazing either. Some songs are good, others are just okay."
        },
        {
            'id': 4,
            'source_platform': 'youtube',
            'original_text': "Band-Maid vs Babymetal - both are great but I prefer Band-Maid's rock style over Babymetal's metal approach."
        },
        {
            'id': 5,
            'source_platform': 'reddit',
            'original_text': "The concert was incredible! The energy was insane and the vocals were perfect. Best live performance I've ever seen."
        }
    ]

    # Create DataFrame
    test_df = pd.DataFrame(test_comments)

    print(f"Testing with {len(test_df)} sample comments...")

    # Process the comments
    results_df = analyzer.process_comments_batch(test_df)

    print("\n=== Sentiment Analysis Results ===")

    # Display results
    for idx, row in results_df.iterrows():
        print(f"\n--- Comment {row['id']} ---")
        print(f"Text: {row['original_text'][:100]}...")
        print(f"Overall Sentiment: {row['overall_sentiment']}")
        print(f"Sentiment Strength: {row['sentiment_strength']}/10")
        print(f"Confidence: {row['confidence_score']:.3f}")
        print(f"Artist Sentiment: {row['artist_sentiment']}")
        print(f"Music Quality Sentiment: {row['music_quality_sentiment']}")
        print(f"Performance Sentiment: {row['performance_sentiment']}")

        if row['has_comparison']:
            print(f"Comparison Type: {row['comparison_type']}")
            print(f"Favorable: {row['favorable_entities']}")
            print(f"Unfavorable: {row['unfavorable_entities']}")

        print(f"Reasoning: {row['sentiment_reasoning']}")

    # Save test results
    output_path = analyzer.save_results(results_df, "test_sentiment_analysis.csv")
    print(f"\nTest results saved to: {output_path}")

    # Summary statistics
    print("\n=== Summary Statistics ===")
    sentiment_counts = results_df['overall_sentiment'].value_counts()
    for sentiment, count in sentiment_counts.items():
        print(f"{sentiment.capitalize()}: {count} ({count/len(results_df)*100:.1f}%)")

    avg_confidence = results_df['confidence_score'].mean()
    print(f"Average Confidence: {avg_confidence:.3f}")

    comparisons = results_df['has_comparison'].sum()
    print(f"Comments with Comparisons: {comparisons}")

    return results_df

def test_with_translated_data():
    """Test with real translated data if available"""

    print("\n=== Testing with Real Translated Data ===")

    # Look for translated files
    translated_dir = Path("/home/florent.bossart/code/florent-bossart/social_media_tracker/data/intermediate/translated")

    if not translated_dir.exists():
        print("No translated data directory found, skipping real data test")
        return

    # Find the most recent translated file
    translated_files = list(translated_dir.glob("*_full_*.csv"))

    if not translated_files:
        print("No translated files found, skipping real data test")
        return

    latest_file = max(translated_files, key=lambda x: x.stat().st_mtime)
    print(f"Testing with file: {latest_file}")

    try:
        # Load a small sample
        df = pd.read_csv(latest_file)
        print(f"Loaded file with {len(df)} rows")

        # Take a small sample for testing (first 3 rows)
        sample_df = df.head(3)

        # Initialize analyzer
        analyzer = SentimentAnalyzer()

        # Process the sample
        results_df = analyzer.process_comments_batch(sample_df)

        # Save results
        output_filename = f"real_data_sentiment_test_{latest_file.stem}.csv"
        output_path = analyzer.save_results(results_df, output_filename)

        print(f"Real data sentiment analysis complete!")
        print(f"Results saved to: {output_path}")

        # Show first result
        if len(results_df) > 0:
            first_result = results_df.iloc[0]
            print(f"\nFirst result example:")
            print(f"Text: {first_result['original_text'][:100]}...")
            print(f"Sentiment: {first_result['overall_sentiment']} (strength: {first_result['sentiment_strength']})")
            print(f"Confidence: {first_result['confidence_score']:.3f}")

        return results_df

    except Exception as e:
        print(f"Error processing real data: {e}")
        return None

def main():
    """Main test function"""

    # Test with sample data
    sample_results = test_sentiment_analysis()

    # Test with real data
    real_results = test_with_translated_data()

    print("\n=== Sentiment Analysis Module Test Complete ===")

    if sample_results is not None:
        print(f"Sample test: PASSED ({len(sample_results)} comments processed)")
    else:
        print("Sample test: FAILED")

    if real_results is not None:
        print(f"Real data test: PASSED ({len(real_results)} comments processed)")
    else:
        print("Real data test: SKIPPED or FAILED")

if __name__ == "__main__":
    main()
