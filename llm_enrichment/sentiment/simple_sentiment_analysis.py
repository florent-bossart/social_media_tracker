"""
Simplified Sentiment Analysis Module for Japanese Music Social Media Data
"""

import json
import logging
import pandas as pd
import requests
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

# Simple configuration
OLLAMA_MODEL = "llama3:latest"
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_TIMEOUT = 120

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SentimentAnalyzer:
    """Simplified Sentiment Analysis class"""

    def __init__(self):
        self.model = OLLAMA_MODEL
        self.base_url = OLLAMA_BASE_URL
        self.timeout = OLLAMA_TIMEOUT

        # Create output directory
        output_dir = "/home/florent.bossart/code/florent-bossart/social_media_tracker/data/intermediate/sentiment_analysis"
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        logger.info(f"SentimentAnalyzer initialized with model: {self.model}")

    def call_ollama_api(self, prompt: str) -> Optional[str]:
        """Call Ollama API"""
        try:
            headers = {
                "ngrok-skip-browser-warning": "true"
            }
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.1}
                },
                timeout=self.timeout,
                headers=headers
            )

            if response.status_code == 200:
                result = response.json()
                return result.get("response", "").strip()
            else:
                logger.warning(f"API returned status code: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"API call failed: {e}")
            return None

    def analyze_sentiment_simple(self, text: str) -> Dict[str, Any]:
        """Simple rule-based sentiment analysis"""
        text_lower = text.lower()

        positive_words = ["love", "amazing", "best", "great", "awesome", "perfect", "brilliant"]
        negative_words = ["hate", "terrible", "awful", "worst", "horrible", "boring", "bad"]

        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)

        if pos_count > neg_count:
            sentiment = "positive"
            strength = min(10, 5 + pos_count)
        elif neg_count > pos_count:
            sentiment = "negative"
            strength = min(10, 5 + neg_count)
        else:
            sentiment = "neutral"
            strength = 5

        return {
            "overall_sentiment": sentiment,
            "sentiment_strength": strength,
            "confidence_score": 0.7,
            "analysis_method": "rule_based"
        }

    def analyze_sentiment_llm(self, text: str) -> Optional[Dict[str, Any]]:
        """LLM-based sentiment analysis"""
        prompt = f"""
Analyze the sentiment of this comment about Japanese music: "{text}"

Respond with JSON only:
{{
    "overall_sentiment": "positive|negative|neutral",
    "sentiment_strength": 7,
    "confidence": 0.85,
    "reasoning": "brief explanation"
}}
"""

        response = self.call_ollama_api(prompt)
        if not response:
            return None

        try:
            # Extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass

        return None

    def process_comments(self, comments_df: pd.DataFrame) -> pd.DataFrame:
        """Process comments for sentiment analysis"""
        results = []

        for idx, row in comments_df.iterrows():
            text = row.get('original_text', '') or row.get('translated_text', '')
            if not text:
                continue

            logger.info(f"Processing comment {idx + 1}/{len(comments_df)}")

            # Try LLM first, fallback to rule-based
            sentiment_data = self.analyze_sentiment_llm(text)
            if not sentiment_data:
                sentiment_data = self.analyze_sentiment_simple(text)
                sentiment_data["analysis_method"] = "rule_based"
            else:
                sentiment_data["analysis_method"] = "llm"

            result = {
                'id': row.get('id', idx),
                'source_platform': row.get('source_platform', 'unknown'),
                'original_text': text,
                'analysis_date': datetime.now().strftime('%Y-%m-%d'),
                'overall_sentiment': sentiment_data.get('overall_sentiment', 'neutral'),
                'sentiment_strength': sentiment_data.get('sentiment_strength', 5),
                'confidence_score': sentiment_data.get('confidence', sentiment_data.get('confidence_score', 0.5)),
                'analysis_method': sentiment_data.get('analysis_method', 'unknown'),
                'reasoning': sentiment_data.get('reasoning', '')
            }

            results.append(result)
            time.sleep(1)  # Small delay

        return pd.DataFrame(results)

    def save_results(self, results_df: pd.DataFrame, filename: str) -> str:
        """Save results to CSV"""
        output_path = f"/home/florent.bossart/code/florent-bossart/social_media_tracker/data/intermediate/sentiment_analysis/{filename}"
        results_df.to_csv(output_path, index=False)
        logger.info(f"Results saved to: {output_path}")
        return output_path

def main():
    """Test function"""
    print("Testing Sentiment Analysis...")

    analyzer = SentimentAnalyzer()

    # Test data
    test_data = pd.DataFrame([
        {"id": 1, "original_text": "YOASOBI is amazing! I love their music so much!"},
        {"id": 2, "original_text": "This song is terrible and boring. Don't like it at all."},
        {"id": 3, "original_text": "It's okay, nothing special but not bad either."}
    ])

    results = analyzer.process_comments(test_data)

    print("\nResults:")
    for _, row in results.iterrows():
        print(f"Text: {row['original_text'][:50]}...")
        print(f"Sentiment: {row['overall_sentiment']} (strength: {row['sentiment_strength']})")
        print(f"Method: {row['analysis_method']}")
        print()

    # Save results
    output_path = analyzer.save_results(results, "test_sentiment_simple.csv")
    print(f"Saved to: {output_path}")

if __name__ == "__main__":
    main()
