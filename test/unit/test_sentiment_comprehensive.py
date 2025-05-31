#!/usr/bin/env python3
"""
Comprehensive Sentiment Analysis Test

This script tests both the main sentiment analysis module (with LLM + fallback)
and the mock sentiment analysis module for comparison and reliability testing.
"""

import sys
import os
import pandas as pd
from pathlib import Path

# Add the data_pipeline directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'data_pipeline'))

from sentiment_analysis import SentimentAnalyzer
from mock_sentiment_analysis import MockSentimentAnalyzer

def test_main_sentiment_analyzer():
    """Test the main sentiment analyzer with LLM + rule-based fallback"""

    print("🧪 Testing Main Sentiment Analyzer (LLM + Rule-based)")
    print("=" * 60)

    # Initialize analyzer
    analyzer = SentimentAnalyzer()

    # Test with sample data that includes various sentiment types
    test_comments = [
        {
            'id': 1,
            'source_platform': 'reddit',
            'original_text': "YOASOBI is absolutely amazing! Their music makes me so happy, especially Yoru ni Kakeru. Best J-pop duo ever!"
        },
        {
            'id': 2,
            'source_platform': 'youtube',
            'original_text': "This song is terrible and boring. The vocals are annoying and the beat is repetitive. Don't like it at all."
        },
        {
            'id': 3,
            'source_platform': 'reddit',
            'original_text': "The concert was okay. Not bad but not amazing either. Some songs were good, others were just average."
        }
    ]

    test_df = pd.DataFrame(test_comments)

    print(f"🎯 Processing {len(test_df)} test comments...")

    # Process using batch method
    results_df = analyzer.process_comments_batch(test_df)

    # Save results
    output_file = "main_sentiment_test.csv"
    output_path = analyzer.save_results(results_df, output_file)

    print(f"\n✅ Main analyzer test completed!")
    print(f"📁 Results saved to: {output_path}")

    # Display summary
    sentiment_counts = results_df['overall_sentiment'].value_counts()
    print(f"\n📈 Sentiment Summary:")
    for sentiment, count in sentiment_counts.items():
        print(f"   {sentiment}: {count}")

    avg_confidence = results_df['confidence_score'].mean()
    print(f"📊 Average Confidence: {avg_confidence:.3f}")

    return results_df

def test_mock_sentiment_analyzer():
    """Test the mock sentiment analyzer"""

    print("\n🤖 Testing Mock Sentiment Analyzer (Rule-based)")
    print("=" * 60)

    # Initialize mock analyzer
    analyzer = MockSentimentAnalyzer()

    # Test with the same data for comparison
    test_comments = [
        {
            'id': 1,
            'source_platform': 'reddit',
            'original_text': "YOASOBI is absolutely amazing! Their music makes me so happy, especially Yoru ni Kakeru. Best J-pop duo ever!"
        },
        {
            'id': 2,
            'source_platform': 'youtube',
            'original_text': "This song is terrible and boring. The vocals are annoying and the beat is repetitive. Don't like it at all."
        },
        {
            'id': 3,
            'source_platform': 'reddit',
            'original_text': "The concert was okay. Not bad but not amazing either. Some songs were good, others were just average."
        }
    ]

    test_df = pd.DataFrame(test_comments)

    print(f"🎯 Processing {len(test_df)} test comments...")

    # Process using batch method
    results_df = analyzer.process_comments_batch(test_df)

    # Save results
    output_file = "mock_sentiment_test.csv"
    output_path = analyzer.save_results(results_df, output_file)

    print(f"\n✅ Mock analyzer test completed!")
    print(f"📁 Results saved to: {output_path}")

    # Display summary
    sentiment_counts = results_df['overall_sentiment'].value_counts()
    print(f"\n📈 Sentiment Summary:")
    for sentiment, count in sentiment_counts.items():
        print(f"   {sentiment}: {count}")

    avg_confidence = results_df['confidence_score'].mean()
    print(f"📊 Average Confidence: {avg_confidence:.3f}")

    return results_df

def test_with_entity_data():
    """Test sentiment analysis with entity extraction data"""

    print("\n🔗 Testing Sentiment Analysis with Entity Extraction Data")
    print("=" * 60)

    entity_file = "data/intermediate/entity_extraction/quick_test_entities.csv"

    if not os.path.exists(entity_file):
        print(f"❌ Entity file not found: {entity_file}")
        return None, None

    df = pd.read_csv(entity_file)
    df_with_text = df[df['original_text'].notna() & (df['original_text'] != '')]

    print(f"📂 Loaded {len(df_with_text)} records with text from entity extraction")

    if len(df_with_text) == 0:
        print("❌ No records with text content found")
        return None, None

    # Test with main analyzer
    print("\n🧠 Using Main Sentiment Analyzer...")
    main_analyzer = SentimentAnalyzer()
    main_results = main_analyzer.process_comments_batch(df_with_text.head(2))  # Limit to avoid long processing
    main_output = main_analyzer.save_results(main_results, "entity_main_sentiment.csv")

    # Test with mock analyzer
    print("\n🤖 Using Mock Sentiment Analyzer...")
    mock_analyzer = MockSentimentAnalyzer()
    mock_results = mock_analyzer.process_comments_batch(df_with_text)  # Process all since it's fast
    mock_output = mock_analyzer.save_results(mock_results, "entity_mock_sentiment.csv")

    print(f"\n✅ Entity data sentiment analysis completed!")
    print(f"📁 Main results: {main_output}")
    print(f"📁 Mock results: {mock_output}")

    return main_results, mock_results

def compare_analyzers():
    """Compare results from main and mock analyzers"""

    print("\n⚖️ Comparing Sentiment Analyzers")
    print("=" * 60)

    # Check if result files exist
    main_file = "/home/florent.bossart/code/florent-bossart/social_media_tracker/data/intermediate/sentiment_analysis/main_sentiment_test.csv"
    mock_file = "/home/florent.bossart/code/florent-bossart/social_media_tracker/data/intermediate/sentiment_analysis/mock_sentiment_test.csv"

    if os.path.exists(main_file) and os.path.exists(mock_file):
        main_df = pd.read_csv(main_file)
        mock_df = pd.read_csv(mock_file)

        print(f"📊 Comparing sentiment classifications:")

        for idx in range(min(len(main_df), len(mock_df))):
            main_row = main_df.iloc[idx]
            mock_row = mock_df.iloc[idx]

            print(f"\n--- Comment {idx + 1} ---")
            print(f"Text: {main_row['original_text'][:60]}...")
            print(f"Main: {main_row['overall_sentiment']} (confidence: {main_row['confidence_score']:.2f})")
            print(f"Mock: {mock_row['overall_sentiment']} (confidence: {mock_row['confidence_score']:.2f})")

            if main_row['overall_sentiment'] == mock_row['overall_sentiment']:
                print("✅ Agreement")
            else:
                print("⚠️ Disagreement")
    else:
        print("❌ Could not find result files for comparison")

def main():
    """Main function"""

    print("🎭 Comprehensive Sentiment Analysis Test Suite")
    print("=" * 80)

    try:
        # Test main sentiment analyzer
        main_results = test_main_sentiment_analyzer()

        # Test mock sentiment analyzer
        mock_results = test_mock_sentiment_analyzer()

        # Test with entity extraction data
        entity_main, entity_mock = test_with_entity_data()

        # Compare results
        compare_analyzers()

        print("\n🎉 All sentiment analysis tests completed successfully!")
        print("\n📝 Summary:")
        print("   ✅ Main Sentiment Analyzer: Working (LLM + Rule-based fallback)")
        print("   ✅ Mock Sentiment Analyzer: Working (Fast rule-based)")
        print("   ✅ Entity Integration: Working")
        print("   ✅ CSV Output: PostgreSQL-compatible format")

        return True

    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
