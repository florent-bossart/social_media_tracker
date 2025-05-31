"""
Mock Sentiment Analysis Module for Japanese Music Social Media Data

This module provides mock sentiment analysis for testing the pipeline,
generating realistic sentiment data without requiring LLM API calls.
"""

import json
import logging
import pandas as pd
import random
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MockSentimentAnalyzer:
    """Mock Sentiment Analysis class for pipeline testing"""

    def __init__(self):
        # Create output directory
        self.output_dir = "/home/florent.bossart/code/florent-bossart/social_media_tracker/data/intermediate/sentiment_analysis"
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)

        # Sentiment keywords for rule-based analysis
        self.positive_words = [
            "love", "amazing", "best", "incredible", "fantastic", "awesome", "perfect",
            "brilliant", "beautiful", "great", "excellent", "outstanding", "wonderful",
            "favorite", "obsessed", "addicted", "masterpiece", "genius", "banger",
            "fire", "slaps", "peak", "legendary", "iconic"
        ]

        self.negative_words = [
            "hate", "terrible", "awful", "worst", "horrible", "trash", "garbage",
            "cringe", "annoying", "boring", "mid", "disappointing", "overrated",
            "bland", "stale", "repetitive", "uninspired", "lazy", "generic"
        ]

        self.neutral_words = [
            "okay", "alright", "decent", "fine", "average", "standard", "typical",
            "normal", "regular", "common", "usual", "ordinary"
        ]

        logger.info("MockSentimentAnalyzer initialized")

    def analyze_sentiment_rule_based(self, text: str) -> Dict[str, Any]:
        """Rule-based sentiment analysis with realistic results"""
        text_lower = text.lower()

        # Count sentiment indicators
        pos_count = sum(1 for word in self.positive_words if word in text_lower)
        neg_count = sum(1 for word in self.negative_words if word in text_lower)
        neu_count = sum(1 for word in self.neutral_words if word in text_lower)

        # Determine overall sentiment
        if pos_count > neg_count and pos_count > neu_count:
            overall_sentiment = "positive"
            sentiment_strength = min(10, 6 + pos_count)
            confidence = min(0.95, 0.7 + pos_count * 0.1)
        elif neg_count > pos_count and neg_count > neu_count:
            overall_sentiment = "negative"
            sentiment_strength = max(1, 4 - neg_count)
            confidence = min(0.95, 0.7 + neg_count * 0.1)
        else:
            overall_sentiment = "neutral"
            sentiment_strength = 5
            confidence = 0.6

        # Analyze specific aspects
        artist_sentiment = "none"
        music_quality_sentiment = "none"
        performance_sentiment = "none"
        personal_experience_sentiment = "none"

        # Simple aspect detection
        if any(word in text_lower for word in ["artist", "singer", "band", "group"]):
            artist_sentiment = overall_sentiment

        if any(word in text_lower for word in ["song", "music", "track", "album", "sound"]):
            music_quality_sentiment = overall_sentiment

        if any(word in text_lower for word in ["concert", "live", "performance", "show", "stage"]):
            performance_sentiment = overall_sentiment

        if any(word in text_lower for word in ["i", "me", "my", "feel", "think", "love", "hate"]):
            personal_experience_sentiment = overall_sentiment

        # Generate emotional indicators
        emotional_indicators = []
        if overall_sentiment == "positive":
            emotional_indicators = random.sample(["joy", "excitement", "love", "admiration"], k=random.randint(1, 3))
        elif overall_sentiment == "negative":
            emotional_indicators = random.sample(["disappointment", "frustration", "dislike", "boredom"], k=random.randint(1, 3))
        else:
            emotional_indicators = random.sample(["neutrality", "indifference"], k=1)

        # Check for comparisons
        has_comparison = any(word in text_lower for word in ["vs", "better than", "worse than", "compared to"])

        return {
            "overall_sentiment": overall_sentiment,
            "sentiment_strength": sentiment_strength,
            "confidence_score": confidence,
            "sentiment_reasoning": f"Rule-based analysis: {pos_count} positive, {neg_count} negative, {neu_count} neutral indicators",

            # Aspect sentiments
            "artist_sentiment": artist_sentiment,
            "music_quality_sentiment": music_quality_sentiment,
            "performance_sentiment": performance_sentiment,
            "personal_experience_sentiment": personal_experience_sentiment,

            # Emotional indicators
            "emotional_indicators": emotional_indicators,
            "emotional_indicators_count": len(emotional_indicators),

            # Comparative analysis
            "has_comparison": has_comparison,
            "comparison_type": "artist_vs_artist" if has_comparison else "",
            "favorable_entities": [] if not has_comparison else ["entity1"],
            "unfavorable_entities": [] if not has_comparison else ["entity2"],
            "comparison_sentiment": "mild_preference" if has_comparison else ""
        }

    def process_comments_batch(self, comments_df: pd.DataFrame) -> pd.DataFrame:
        """Process a batch of comments for sentiment analysis"""
        results = []

        for idx, row in comments_df.iterrows():
            text = row.get('original_text', '') or row.get('translated_text', '')
            if not text:
                logger.warning(f"No text found for row {idx}")
                continue

            logger.info(f"Processing comment {idx + 1}/{len(comments_df)}")

            # Analyze sentiment
            sentiment_data = self.analyze_sentiment_rule_based(text)

            # Prepare result row
            result_row = {
                'id': row.get('id', idx),
                'source_platform': row.get('source_platform', 'unknown'),
                'original_text': text,
                'analysis_date': datetime.now().strftime('%Y-%m-%d'),
                'overall_sentiment': sentiment_data['overall_sentiment'],
                'sentiment_strength': sentiment_data['sentiment_strength'],
                'confidence_score': sentiment_data['confidence_score'],
                'sentiment_reasoning': sentiment_data['sentiment_reasoning'],

                # Aspect sentiments
                'artist_sentiment': sentiment_data['artist_sentiment'],
                'music_quality_sentiment': sentiment_data['music_quality_sentiment'],
                'performance_sentiment': sentiment_data['performance_sentiment'],
                'personal_experience_sentiment': sentiment_data['personal_experience_sentiment'],

                # Emotional indicators
                'emotional_indicators': json.dumps(sentiment_data['emotional_indicators']),
                'emotional_indicators_count': sentiment_data['emotional_indicators_count'],

                # Comparative analysis
                'has_comparison': sentiment_data['has_comparison'],
                'comparison_type': sentiment_data['comparison_type'],
                'favorable_entities': json.dumps(sentiment_data['favorable_entities']),
                'unfavorable_entities': json.dumps(sentiment_data['unfavorable_entities']),
                'comparison_sentiment': sentiment_data['comparison_sentiment']
            }

            results.append(result_row)

        return pd.DataFrame(results)

    def save_results(self, results_df: pd.DataFrame, output_filename: str) -> str:
        """Save sentiment analysis results to CSV"""
        output_path = Path(self.output_dir) / output_filename

        # Ensure all columns are properly formatted for PostgreSQL
        for col in results_df.columns:
            if results_df[col].dtype == 'object':
                results_df[col] = results_df[col].astype(str).replace('nan', '')

        results_df.to_csv(output_path, index=False)
        logger.info(f"Sentiment analysis results saved to: {output_path}")

        return str(output_path)

    def analyze_file(self, input_file_path: str, output_filename: Optional[str] = None) -> str:
        """Analyze sentiment for all comments in a file"""
        logger.info(f"Starting sentiment analysis for file: {input_file_path}")

        # Load input data
        df = pd.read_csv(input_file_path)
        logger.info(f"Loaded {len(df)} rows for sentiment analysis")

        # Generate output filename if not provided
        if not output_filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_filename = f"{timestamp}_sentiment_analysis.csv"

        # Process all comments
        results_df = self.process_comments_batch(df)

        # Save results
        output_path = self.save_results(results_df, output_filename)

        # Log summary statistics
        sentiment_counts = results_df['overall_sentiment'].value_counts()
        logger.info(f"Sentiment analysis complete. Results summary:")
        for sentiment, count in sentiment_counts.items():
            logger.info(f"  {sentiment}: {count} ({count/len(results_df)*100:.1f}%)")

        avg_confidence = results_df['confidence_score'].mean()
        logger.info(f"Average confidence score: {avg_confidence:.3f}")

        comparisons = results_df['has_comparison'].sum()
        logger.info(f"Comments with comparisons: {comparisons}")

        return output_path

def main():
    """Test function for mock sentiment analysis"""
    print("=== Testing Mock Sentiment Analysis ===")

    analyzer = MockSentimentAnalyzer()

    # Test data
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

    print(f"Processing {len(test_df)} test comments...")

    # Process the comments
    results_df = analyzer.process_comments_batch(test_df)

    print("\n=== Sentiment Analysis Results ===")

    # Display results
    for idx, row in results_df.iterrows():
        print(f"\n--- Comment {row['id']} ---")
        print(f"Text: {row['original_text'][:80]}...")
        print(f"Overall Sentiment: {row['overall_sentiment']} (strength: {row['sentiment_strength']}/10)")
        print(f"Confidence: {row['confidence_score']:.3f}")
        print(f"Aspects - Artist: {row['artist_sentiment']}, Music: {row['music_quality_sentiment']}, Performance: {row['performance_sentiment']}")
        print(f"Emotional Indicators: {row['emotional_indicators']}")
        if row['has_comparison']:
            print(f"Comparison: {row['comparison_type']}")
        print(f"Reasoning: {row['sentiment_reasoning']}")

    # Save test results
    output_path = analyzer.save_results(results_df, "mock_sentiment_test.csv")
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

    print("\n=== Mock Sentiment Analysis Test Complete ===")

if __name__ == "__main__":
    main()
