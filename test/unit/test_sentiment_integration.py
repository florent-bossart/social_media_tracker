#!/usr/bin/env python3
"""
Integration test for sentiment analysis with entity extraction data

This script tests the sentiment analysis module using real entity extraction output data.
"""

import sys
import os
import pandas as pd
from pathlib import Path

# Add the data_pipeline directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'data_pipeline'))

from sentiment_analysis import SentimentAnalyzer

def test_sentiment_analysis_integration():
    """Test sentiment analysis using entity extraction data"""

    print("🧪 Starting Sentiment Analysis Integration Test")
    print("=" * 60)

    # Initialize sentiment analyzer
    print("📊 Initializing sentiment analyzer...")
    analyzer = SentimentAnalyzer()

    # Load entity extraction data
    entity_file = "data/intermediate/entity_extraction/quick_test_entities.csv"
    print(f"📂 Loading entity data from: {entity_file}")

    if not os.path.exists(entity_file):
        print(f"❌ Entity file not found: {entity_file}")
        return False

    df = pd.read_csv(entity_file)
    print(f"📈 Loaded {len(df)} records from entity extraction")
    print(f"🔍 Columns: {list(df.columns)}")

    # Filter records with actual text content
    df_with_text = df[df['original_text'].notna() & (df['original_text'] != '')]
    print(f"📝 Records with text content: {len(df_with_text)}")

    if len(df_with_text) == 0:
        print("❌ No records with text content found")
        return False

    # Test with first few records
    test_records = df_with_text.head(3)
    print(f"\n🎯 Testing sentiment analysis on {len(test_records)} records...")

    results = []

    for idx, row in test_records.iterrows():
        print(f"\n--- Record {idx} ---")
        text = row['original_text']
        print(f"Text: {text[:100]}...")

        try:
            # Analyze sentiment
            sentiment_result = analyzer.analyze_sentiment_llm(text)

            # Fall back to rule-based if LLM fails
            if sentiment_result is None:
                print(f"   LLM analysis failed, using rule-based fallback...")
                sentiment_result = analyzer.analyze_basic_sentiment(text)
                sentiment_result['analysis_method'] = 'rule_based'
            else:
                sentiment_result['analysis_method'] = 'llm'

            print(f"✅ Sentiment: {sentiment_result['overall_sentiment']}")
            print(f"   Confidence: {sentiment_result['confidence']:.2f}")
            print(f"   Method: {sentiment_result['analysis_method']}")

            if sentiment_result.get('sentiment_aspects'):
                print("   Aspects:")
                for aspect, sent in sentiment_result['sentiment_aspects'].items():
                    print(f"     - {aspect}: {sent}")

            # Combine with entity data
            result = {
                'id': row['id'],
                'source_platform': row['source_platform'],
                'original_text': text,
                'extraction_date': row['extraction_date'],
                'entity_confidence': row['confidence_score'],
                'artists': row['entities_artists'] if pd.notna(row['entities_artists']) else '[]',
                'songs': row['entities_songs'] if pd.notna(row['entities_songs']) else '[]',
                'genres': row['entities_genres'] if pd.notna(row['entities_genres']) else '[]',
                **sentiment_result
            }

            results.append(result)

        except Exception as e:
            print(f"❌ Error analyzing sentiment: {str(e)}")
            continue

    if results:
        # Save results
        output_file = "data/intermediate/sentiment_analysis/integration_test_sentiment.csv"
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        results_df = pd.DataFrame(results)
        results_df.to_csv(output_file, index=False)

        print(f"\n✅ Integration test completed successfully!")
        print(f"📁 Results saved to: {output_file}")
        print(f"📊 Processed {len(results)} records")

        # Show summary
        sentiment_counts = results_df['overall_sentiment'].value_counts()
        print(f"\n📈 Sentiment Summary:")
        for sentiment, count in sentiment_counts.items():
            print(f"   {sentiment}: {count}")

        return True
    else:
        print("❌ No results generated")
        return False

def main():
    """Main function"""
    success = test_sentiment_analysis_integration()

    if success:
        print("\n🎉 Sentiment analysis integration test PASSED!")
    else:
        print("\n💥 Sentiment analysis integration test FAILED!")

    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
